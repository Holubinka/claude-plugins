---
name: backend-architecture
description: "Decides where backend code goes in a Node or TypeScript service and how it is split — which folder a new module belongs in, whether to organise by feature or by technical layer, where a constant lives, what earns a place in a shared utility, where the business rules go, and whether a design pattern is warranted yet. Use when adding a module, endpoint, job or consumer, when a file has outgrown its folder, when reaching for a repository, factory or strategy, or when a service starts calling another service."
metadata:
  version: "1.0.0"
keywords: [backend, nodejs, structure, placement, patterns]
---

# Backend architecture — where code goes, and how it is split

Placement and decomposition for Node and TypeScript services. Sources for every claim here are in
[`references.md`](references.md).

**This is not the ring question.** Which ring code belongs to and which way its dependencies may
point is `engineering-paved-path:onion-architecture`. This answers the one before it: what the
folders are called, what lives in each, and when a pattern has earned its place.

## 0. Read the repository first — find what to reuse

Before deciding where anything goes, **find the answer the repository has already given.** A
structure invented alongside an existing one is worse than either, because now there are two.

Establish four things, and say what you found:

1. **The top-level shape.** Are folders named for business concepts (`orders`, `billing`) or for
   technical roles (`controllers`, `services`, `models`)? Both work; mixing them at the same level
   does not.
2. **What one complete slice looks like.** Open the module most like the one you are adding and read
   all of it. That file set — its names, its layering, its test placement — is the specification,
   and it beats every rule below.
3. **The seams that already exist.** A base class, a shared error type, a request-context object, a
   validation helper, a repository interface. **Reusing a seam that fits is worth more than any
   placement decision you make** — a second way to do the same thing costs everyone who reads either.
4. **Whether a boundary is enforced.** An import-graph linter, dependency-cruiser, an Nx constraint,
   ESLint import rules. Where one exists it is the authority and this skill is commentary; where none
   does, say so and apply what follows as a proposal.

**Report which of the four you found before proposing anything.** A repository with a clear
convention and one violation needs the convention followed, not a better structure.

## 1. Components first, layers inside them

The shape that survives growth is **business components at the top level, technical layers inside
each**:

```
orders/
  entry-points/     controllers, queue consumers, scheduled jobs
  domain/           the rules. Services, entities, value objects
  data-access/      repositories, queries, the ORM
```

A layers-first tree answers *where are all the controllers* and cannot answer *where is order
creation*. The failure mode is documented and specific: with every service in one folder, boundaries
blur and services begin calling other services, which is the tangle the split existed to prevent.

**The rule with teeth is the web boundary.** No framework object crosses into `domain/`. An Express
`req`/`res`, a Fastify reply, a Nest decorator argument — pass the values, never the transport. The
moment domain code takes a `req`, that logic is unreachable from a queue consumer, a cron job and a
test, and you find out when you need one of the three.

**Do not restructure an existing repository to match this.** A consistent layers-first tree works;
converting it is a migration with its own review. Use this shape for new components and say that the
existing ones differ.

## 2. Where the business rules live

The honest answer is **enforced in one place, consistently** — and the sources genuinely disagree
about which place.

| Shape | Rules live in | Fits |
| :--- | :--- | :--- |
| Transaction script | The service method, top to bottom | CRUD, thin flows, small services |
| Domain model | Entities and value objects; services coordinate | Invariants that must hold everywhere the data is touched |

**The anti-pattern is mixing the two shapes** — entity classes holding only data while every rule
lives in a service, so the object can be built in an invalid state by anyone who skips it. Fowler
calls that *anemic*, and the half usually dropped when he is quoted is that a service layer is fine
*alongside* behaviour-carrying objects.

The test, whichever shape the repository chose: **can this object exist in a state its rules
forbid?** If yes the rule is in the wrong place, whatever the folder is called.

## 3. Constants, utils, helpers

**A folder called `utils` is technical debt with a smile.** It starts as three innocent functions and
becomes fifteen hundred lines nobody can inventory. The problem is not the name — it is that no test
governs what may enter.

The test, which this marketplace's `frontend-architecture` skill also uses, so the two agree:

| Kind | Test | Home |
| :--- | :--- | :--- |
| **helper** | Knows your domain — an order, a tenant, a currency | Beside its consumer, moving to shared only on the second one |
| **util** | Would drop into an unrelated project unchanged — `clamp`, `chunk` | The shared lib folder |
| **lib** | A preconfigured integration, not a function — the HTTP client, the logger | The shared lib folder |

If you cannot say which of the three a new file is, it is not ready to be extracted. Leave it where
it is used.

**Constants** go beside what they configure, in a named file, exported individually — not in one
global bucket, which everything imports and which becomes a dependency edge between modules that
have nothing to do with each other. **A magic value is a constant that has not been named yet**, and
naming it is worth doing at one use, because the name is the explanation.

## 4. Patterns — when, and mostly not yet

**The rule of three.** Copy it once. On the third occurrence, abstract — and not before, because with
two examples you do not yet know the shape of the abstraction or whether there is one. A wrong
abstraction is more expensive than the duplication it removed, and harder to reverse.

[`patterns.md`](patterns.md) has the pattern-by-pattern version: what each is for, the signal that it
is warranted, and the much more common signal that it is not.

**A pattern is warranted by a requirement you can name, not by the possibility of one.** "We might
swap the provider" is not a second implementation. And do not wrap a library until you can say what
the wrapper gives you — one added by reflex reimplements a subset badly and still leaks.

## 5. Boundary with the sibling skills

| Question | Skill |
| :--- | :--- |
| Which ring, and which way may dependencies point? | `engineering-paved-path:onion-architecture` |
| Where does a *frontend* file go? | `engineering-paved-path:frontend-architecture` |
| A generic that will not infer, a slow `tsc`, type-level work | `engineering-paved-path:typescript-expert` |
| Am I building more than was asked? | `engineering-paved-path:scoped-change` |
| How should this table look? | `engineering-paved-path:postgresql-table-design` |

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Proposing a structure before reading the existing one | Step 0. The repository has usually already decided |
| Passing `req` or `res` into a service | Pass the values. The transport stays at the entry point |
| A shared `constants.ts` imported everywhere | Beside what it configures. A shared bucket is a dependency edge |
| A repository interface with one implementation | The ORM is already an abstraction. Name the second before adding a first |
| Extracting on the second occurrence | Rule of three. Two do not show you the shape |
| Restructuring a consistent tree to match a better one | That is a migration, with its own review |
| A new helper beside an existing one that nearly fits | Reuse the seam. A second way to do one thing costs every reader |
