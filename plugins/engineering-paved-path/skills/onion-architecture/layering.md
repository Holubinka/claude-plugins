# Layering — what goes in each file

The anatomy of one module. Every rule here is [SKILL.md](SKILL.md) §2's arrow applied to one
file.

A module is a vertical slice. Inside it, the rings run `route → service → repository →
database`, with a pure-transform file as the core anything may call.

The file names below are the common convention, not a requirement. [SKILL.md](SKILL.md) §0 says
to map them onto the names the repository actually uses first; do that, then read this.

The code samples use a fictional `agents` module purely so the shapes are readable. They are
illustrations, not citations — do not go looking for them in the repository you are working on.

---

## 1. Module anatomy

| File | Ring | Holds | Never holds |
|---|---|---|---|
| `routes.ts` | Infrastructure | Request schema, tenancy resolution, delegation, "not found" → HTTP error | ORM calls, business rules, DTO mapping |
| `service.ts` | Application | The use case, policy, row → DTO mapping | request/response objects, raw SQL, concrete adapters, `node:fs` |
| `<verb>-executor.ts` | Application | One long or background use case lifted out of a fat service | same as `service.ts` |
| `repository.ts` | Application | Database access, and only that | the container, DTOs, policy |
| `helpers.ts` | Core | Pure transforms, DTO mappers | anything with a callable dependency |
| `types.ts` | Ports | A port interface used only by this module | implementations |
| `constants.ts` | Core | Literals, job kinds, secret names | anything computed |

A module with only a route file is not automatically wrong — a thin read-only endpoint may not
need the rest. It becomes wrong the moment that file starts doing two of the jobs above.

## 2. The route

```ts
export default async function agentsRoutes(appBase: FastifyInstance) {
  const app = appBase.withTypeProvider<ZodTypeProvider>();
  const service = new AgentsService(app.container);

  app.get('/agents/:id', { schema: { params: IdParams } }, async (req) => {
    const { workspaceId } = await getContext(app.container, req);
    const agent = await service.get(workspaceId, req.params.id);
    if (!agent) throw new NotFoundError('Agent not found');
    return agent;
  });
}
```

Four things happen and nothing else: validate (declaratively, through the framework's schema
hook), resolve tenancy, delegate, translate absence into an error.

**Declare the schema, do not parse in the handler body.** A schema declared where the framework
expects it rejects bad input before the handler runs and types the request object for free.
Hand-rolling `Schema.parse(req.body)` inside the handler moves validation after the framework's
own error handling and produces a different failure shape for the same class of bad request.

**The "undefined → 404" convention.** A service returns `undefined` for *not found*; the route
turns it into an HTTP error. Services do not throw HTTP concepts — that is what keeps them
usable from a CLI, a worker or a test.

## 3. The service

```ts
export class AgentsService {
  private repo: AgentsRepository;

  constructor(private container: Container) {
    this.repo = new AgentsRepository(container.db);
  }

  async list(workspaceId: string): Promise<Agent[]> {
    const rows = await this.repo.list(workspaceId);
    return rows.map(toAgentDto);
  }
}
```

This is the common shape, and it has **one defect**: the repository is constructed, not
injected. Add the seam:

```ts
constructor(container: Container, repo = new AgentsRepository(container.db)) {
  this.container = container;
  this.repo = repo;
}
```

One default parameter. Existing call sites (`new AgentsService(app.container)`) keep working, and
a test can now pass a fake. Without it, the only way to substitute a repository is
`(svc as unknown as { repo: … }).repo = fake` — a test that reaches through a private field
breaks on any refactor that renames it, and it is the reliable sign that this seam is missing.

**Reach adapters through the container, never by import.** `container.git`, `await
container.github()`, `await container.llm(provider)`. The container resolves overrides and
secrets; importing the concrete client bypasses both.

This is the half of the container that is prescribed, and it does not contradict the Service
Locator warning in [SKILL.md](SKILL.md) §1 — see that section for the line. Ports come from the
container; the repository comes from a parameter. A reviewer who reads only §1 will flag the
method below and be wrong.

**Degrade rather than throw when enrichment is optional:**

```ts
async listModels(provider: Provider): Promise<ModelInfo[]> {
  try { const llm = await this.container.llm(provider); return await llm.listModels(); }
  catch { return []; }
}
```

Degrade only where the caller can genuinely proceed without the value. Swallowing an error that
the caller needed is worse than throwing it.

## 4. When a service is too big

Not at a line count — at a **second reason to change**. A service that both answers short reads
and owns a long multi-step pipeline has two, and the pipeline is what moves:

```ts
constructor(private container: Container) {
  this.repo = new ReviewRepository(container.db);
  this.agents = container.agentsRepo;
  this.executor = new ReviewRunExecutor(container, this.repo, this.agents);
}
```

The service keeps the public method surface and the short reads; the executor owns one long use
case. Note the executor takes its collaborators **as constructor parameters** — it already has
the seam §3 asks for.

The failure mode to watch for: the pipeline moves out into its own files but the facade never
shrinks, because every extracted step is still re-exported through it. Extraction that leaves
the original file the same size did not happen.

## 5. The repository

```ts
export class AgentsRepository {
  constructor(private db: Db) {}

  async list(workspaceId: string): Promise<AgentRow[]> {
    return this.db.select().from(t.agents).where(eq(t.agents.workspaceId, workspaceId));
  }
}
```

A database handle, not the container. Rows out, not DTOs. No policy — deciding *whether* a user
may see a row is the service's job; the repository only scopes the query it was asked for.

**Splitting a large repository.** Past roughly 200 lines, move the queries into free functions
grouped by aggregate and keep the class as a dispatcher, so the public surface stays stable:

```ts
import * as pullRepo from './repository/pull.repo.js';

export class ReviewRepository {
  constructor(private db: Db) {}

  getPull(workspaceId: string, prId: string): Promise<PullRow | undefined> {
    return pullRepo.getPull(this.db, workspaceId, prId);
  }
}
```

**Transactions across repositories.** Where the ORM's transaction handle is shaped like the
database handle, a method that must join a caller's transaction takes the handle instead
of reading `this.db`:

```ts
async insertRun(run: NewRun, db: Db | Tx = this.db) { … }
```

Then one `db.transaction(async (tx) => { … })` in the service passes `tx` to each repository. Do
not open a transaction inside a repository method that a caller might already have wrapped.

**Translate errors at this boundary**. A unique-violation should leave the repository as
the application's own error type, not as a driver error. Nothing outside the repository should
need to know which driver is underneath.

## 6. Where mapping happens

Exactly one depth: **row → DTO in the pure-transform file, called from the service.**

```ts
const rows = await this.repo.list(workspaceId);
return rows.map(toAgentDto);
```

Not in the route — mapping inline in a handler is the violation §3.5 names. And not in the
repository, which would make it impossible to compose two queries into one DTO.

The pure-transform file is core: no container, no I/O. A **type-only** import of the schema for
an inferred row type is a tolerated edge, and a good boundary gate distinguishes it (in
dependency-cruiser, `dependencyTypesNot: ['type-only']`). A *value* import of the schema into a
pure helper is not tolerated.

## 7. Cross-slice sharing

One slice importing another couples them at the file level. Three legitimate escapes, in order
of preference:

1. **A shared module** — request context helpers, common id schemas. For genuinely generic
   HTTP-adjacent pieces.
2. **A repository on the container.** Constructed in the composition root precisely so consuming
   modules use `container.agentsRepo` instead of reaching into another module's folder.
3. **A port** — when the other slice is really a service to this one, define the interface this
   slice needs in its own `types.ts` and inject the implementation.

**Escape 2 and rule §3.5 pull against each other, and the ordering above is the tie-breaker.**
A repository returns rows (§3.2), so taking one off the container carries a persistence row out
of its slice — which §3.5 forbids.

Watch for the way this hides: if row types are declared in a neutral location rather than inside
the owning module, a `no-cross-module` rule never matches, the row spreads through public
signatures, and no gate ever reports it.

So: escape 2 is for reaching a *behaviour* on another slice. The moment its rows start appearing
in your own signatures, you wanted escape 3 — declare the minimal shape your slice actually
needs in your own `types.ts` and map to it in the owning slice's pure-transform file.

A constant with no neutral home — a job kind shared by a producer and a consumer — is the one
case that resists all three. Put it in the shared module rather than importing it across slices.

## 8. The platform layer is not a lower layer

A `platform/` (or `infra/`, `core/`) directory that holds cross-cutting infrastructure *and* the
composition root necessarily imports the feature modules. That makes a folder-level cycle by
design. Do not "fix" it — and do not treat that directory as a place where module code
may be parked to dodge a layering rule.

Two deviations worth naming when you find them there:

- **Infrastructure that persists.** A job runner that owns its own table directly rather than
  through a repository is a real deviation. It is defensible — the runner is infrastructure that
  happens to write — but it should be recorded as a deviation, not copied as a pattern.
- **Module-level singletons the container assigns rather than constructs.** An event bus
  exported as a module-level value means two application instances in one process share state.
  That is fine in production and a trap in tests, which is exactly where two instances happen.
