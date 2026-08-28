# Testing the rings

The reason to draw the rings at all: each one gets a cheaper test than the one outside it.
Pure core gets unit tests, the imperative shell gets integration tests, and the shell stays
thin so there is less of it to test the expensive way `[FC]`.

---

## 1. Which test for which ring

| Ring | Test | Needs |
|---|---|---|
| Core | Call the function, assert the value | nothing |
| Ports | Nothing — an interface has no behaviour | — |
| Application (service) | Construct with a fake repository and mock adapters | nothing |
| Application (repository) | The real database | a container runtime |
| Infrastructure (routes) | Inject a request through the app factory with overrides | the database only if the route queries |
| Infrastructure (adapters) | Test the real thing, or do not test it | varies |

**Make the filename the contract.** A distinct suffix for database-backed tests — `*.it.test.ts`
is the common one — lets the two lanes run as separate CI jobs, one of which needs no container
runtime at all. A test that imports the database helper and does not carry the suffix breaks
that split silently: the fast lane starts requiring a database, and nobody notices until CI is
slow for everyone.

Whatever the repository already uses, keep. Inventing a second convention beside an existing one
is worse than either.

## 2. The core is free to test

No setup, no fixtures, no doubles:

```ts
// deriveStatus takes `now` as a parameter, so there is no clock to mock.
expect(deriveStatus(runs, now)).toBe('stale');
```

**If a test of a "pure" function needs a mock, the function is not in the core ring.** Move the
I/O out and pass the result in.

A well-drawn pure core is entirely this: stub the ports it was handed, assert on values — no
server, no database, no credentials.

## 3. The service seam

A service should be testable with a fake repository. Where the service builds its own repository
in the constructor, the only way in is to overwrite the private field afterwards:

```ts
const svc = new RepoIntelService(container);
(svc as unknown as { repo: Record<string, unknown> }).repo = {
  getBasics: async () => opts.basics ?? null,
};
```

That is brittle in a specific and quiet way: rename the private field and the test silently
exercises the **real** repository against a stub database handle, still passing for the wrong
reason.

The commoner outcome is worse — a service with no seam gets no hermetic test at all, and its
logic is reachable only through a database-backed test. That is the most expensive test in the
suite, paying for a container runtime to exercise logic that needs none.

The fix is one default parameter ([layering.md](layering.md) §3):

```ts
constructor(container: Container, repo = new AgentsRepository(container.db)) { … }
```

```ts
// Then, with no container runtime and no database:
const svc = new AgentsService(fakeContainer, {
  list: async () => [agentRow({ name: 'reviewer' })],
} as unknown as AgentsRepository);

expect(await svc.list('ws-1')).toEqual([expect.objectContaining({ name: 'reviewer' })]);
```

Add the seam when you next touch the service for another reason. **Do not add it as a standalone
refactor with no test behind it** — a seam nothing uses is just a wider constructor.

## 4. Faking the outside

Adapters are substituted at the composition root, not by module mocking. The app factory takes
config, a database handle and overrides, and that is the whole test surface:

```ts
const app = await buildApp({
  config,
  overrides: { llm: { openrouter: new MockLLMProvider() }, git: new MockGitClient() },
});
const res = await app.inject({ method: 'GET', url: '/agents' });
```

No `vi.mock`. **If you find yourself reaching for module mocking to replace an external call,
the call is not behind a port yet** — go add one ([ports-and-adapters.md](ports-and-adapters.md)
§3). Module mocking couples the test to an import path, so it keeps passing after the code moves
and stops passing after an unrelated rename.

A smoke test can run the whole app with no database at all where the driver connects lazily.
That works only for routes that never query, and it is worth having exactly for that: it proves
the wiring without paying for infrastructure.

## 5. Integration tests

Drive real routes against the real database with real migrations and seed data, mocking only the
outside world. Self-skip when the container runtime is absent, so a developer without it still
gets a green fast lane:

```ts
const hasDocker = await dockerAvailable();
const d = hasDocker ? describe : describe.skip;
```

Two things to know before writing one:

- **A fire-and-forget use case needs polling, not a sleep.** Where the route returns before the
  work finishes, assert with a helper that waits for the state you expect and fails on a
  timeout. A fixed sleep is either flaky or slow, usually both in sequence.
- **A module-level singleton is shared between two app instances in one process.** An event bus
  or run registry exported as a module value makes parallel tests interfere in a way that looks
  like flakiness in whichever test happens to run second.

Reserve these for what genuinely needs the database: the repository, a migration, a constraint, a
transaction. **A use case tested here that could have been tested in §3 costs a container pull
on every CI run** — that is the whole reason the rings are worth drawing.

## 6. What not to test

- **Ports.** An interface has no behaviour. Testing that a mock returns what you told it to
  returns nothing.
- **The container's wiring.** A getter returning the concrete type it was written to return is a
  tautology. That it returns the *override* when one is given is already proven by every test
  that passes one.
- **Thin adapters.** An adapter that is mostly one SDK call has nothing of yours in it. Test the
  parsing helper it uses — which lives in the core — not the HTTP round trip.
