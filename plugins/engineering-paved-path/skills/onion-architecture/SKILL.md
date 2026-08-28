---
name: onion-architecture
description: "Decides which ring backend code belongs in and which direction its dependencies may point. Use when adding or changing a route, service, repository or adapter; when choosing between a handler, a use case, a query and a pure transform; when introducing a port for a new external dependency; when wiring something into the composition root; or when a boundary gate such as dependency-cruiser fails. Covers layering, ports and adapters, the composition root, and which test each ring gets."
metadata:
  version: "1.0.0"
  tags: onion-architecture, hexagonal, ports-and-adapters, layering, dependency-rule, composition-root, backend
---

# Onion Architecture — which ring, and which way it points

Placement and dependency direction for backend code.

**One rule generates the rest: dependencies point inward, never outward**. Every rule below is that rule applied to a specific arrow. When a rule and the direction seem to disagree, the direction wins and the rule is wrong.

## Navigation

| Read | For |
|---|---|
| **This file** | The rings, the four-step procedure, what to do when the gate fails, red flags, the review checklist |
| [layering.md](layering.md) | What goes in the handler / use case / query / pure-transform file, DTO mapping, when a service splits into an executor |
| [ports-and-adapters.md](ports-and-adapters.md) | When a dependency needs a port, where the interface lives, the mock obligation, degraded contracts, secrets |
| [testing-the-rings.md](testing-the-rings.md) | Which ring gets which test, the constructor seam, the integration-test rule |

## 0. Read the repository first

This skill names the rings; **it does not know your folder names.** Before applying it, spend one pass establishing three things, and say in your output what you found:

1. **Does a boundary gate already exist?** Look for `.dependency-cruiser.cjs`/`.js`, `eslint-plugin-boundaries`, `import/no-restricted-paths`, an Nx or Turbo project graph constraint, an ArchUnit-style test. **If one exists, it is the authority and this file is commentary.** Its rules carry their own reasons; read those instead of guessing.
2. **Which directories hold which kind of code.** Map the five rings in §1 onto the names this repository actually uses. Write the mapping down once; every later answer refers to it.
3. **Where the composition root is** — the single file that names concrete types and wires them together. If there is none, that is itself the most valuable finding.

Where no gate and no convention exist, say so plainly and apply §1–§3 as a proposal, not as a finding. **An architecture rule invented on the spot and reported as the repository's own is worse than no rule**: the next reader obeys it believing someone decided it.

---

## 1. The rings

Naming, not moving. The rings are a lens over the folders that already exist.

| Ring | Holds | Typically |
|---|---|---|
| **Core** — pure | Domain logic, contracts, pure transforms. No I/O, no framework, no clock, no randomness. | a domain or core package, shared contracts, per-module helper and status files |
| **Ports** — interfaces | What the inside needs from the outside, expressed as a type. | an `adapters`/`ports` interface file, or a module-local `types.ts` when it has one user |
| **Application** — use cases | Orchestration and persistence calls. Knows ports, never implementations. | service files, long-running executors, repository files |
| **Infrastructure** — edges | Driving adapters (HTTP, CLI, queue consumers) and driven adapters (database, LLM, git, third-party APIs). | route/controller files, an `adapters/` tree, the DB layer |
| **Composition root** | Wiring. Outside the rings on purpose — the one place allowed to name every concrete type. | a container or bootstrap file, the app entry point, a module index |

**The composition root importing everything is not a violation to fix.** A composition root is *defined* as the single place that knows the concrete graph.

Everywhere else the container is a **port factory, and only that**. Asking it for a port — `container.git`, `await container.llm(provider)` — is not merely allowed; §3.3 requires it, because the container is what resolves overrides and secrets. Reaching into it for a collaborator that could have arrived as a parameter — a repository above all — is the Service Locator anti-pattern, and it is the move that removes the seam a test needs.

So a service *holding* a container is not the violation. `this.repo = new Repository(container.db)` inside that service is.

**Vertical slices and rings compose.** If the repository is organised by feature rather than by layer, the rings live *inside* each slice. That hybrid is a design, not a half-finished migration — see §6.

## 2. The four-step procedure

Run in order for any "where does this go" question. Stop when the answer is determined.

**1 — Name the kind of code.** HTTP shape · use case · persistence · pure transform · external call · wiring · constant. If you cannot name it, it is not ready to be placed.

**2 — Find its ring.**

| The code… | Ring |
|---|---|
| reads the request, sets a status code, declares the request schema | Infrastructure — route / controller |
| orchestrates a use case, applies policy, maps rows → DTOs | Application — service |
| is a long or background use case pulled out of a fat service | Application — executor |
| is a database query | Application — repository |
| transforms values and calls nothing | Core — helpers |
| talks to a network, a disk or a subprocess | Infrastructure — adapter |
| is the *shape* of that external thing | Ports — shared interface file (2+ users) or module-local types (1 user) |
| decides which implementation is used | Composition root |
| must run without the web server present — a CLI, a worker, a CI runner | Core |

**3 — Check the arrow points inward.** Outer may call any inner, directly, without a proxy method. Inner may never name outer. If your import goes the wrong way, the thing you need is in the wrong ring — move the thing, do not add the import.

**4 — Run the gate**, if §0 found one. It is faster than reasoning about it. If the repository has no gate, say so in your output rather than implying a check happened.

**When it fails, escalate in this order — stop at the first that works:**

1. **Move the code.** Nine times in ten the rule is right and the file is in the wrong ring. Check the frozen baseline first, if the gate keeps one: if the same edge is already frozen from another file, the thing you are importing has no home, and giving it one clears both.
2. **Narrow the rule**, with the reason recorded beside it. Only when a whole category is legitimately exempt — the bar is "the rule is wrong", not "the rule is inconvenient".
3. **Baseline it**, deliberately, only for something you intend to fix and only with a note saying what would fix it.

Prefer a gate with no inline-ignore comment. A regenerated baseline re-freezes the **whole** file, so regenerate only when a refactor has *removed* entries: confirm the strict count fell, then read the diff to check nothing was added. Regenerating to silence a new violation is the one thing a boundary gate cannot survive.

## 3. The rules

1. **A route validates, resolves tenancy, delegates, and maps "not found" to its HTTP shape.** Nothing else. Declare the request schema declaratively where the framework supports it rather than parsing the body by hand inside the handler.
2. **A repository takes a database handle, returns rows, and holds nothing else.** Never the container. Past roughly 200 lines, split by aggregate into free functions behind the class.
3. **A service depends on ports, and gets its repository as a parameter.** `constructor(container: Container, repo = new XRepository(container.db))` — the default keeps call sites unchanged, and the parameter is what makes the service testable. Keeping the container is right: that is how ports are reached (§1). Taking the repository out of it, or building one inside the constructor, is what this rule forbids.
4. **Every external call goes behind a port**. A port is not finished until the mock implementation of it exists beside the real one.
5. **Data crossing a ring boundary is a plain structure**. A persistence row type never leaves its module; map it to a DTO in the module's pure-transform file. Mapping inline in a route is a violation.
6. **Parse once, at the edge** `[PK]`. The contract layer is the boundary. Inside a service the value is already the parsed type — do not re-validate it.
7. **Secrets reach code only through a secrets port.** Never through the config object, never through `process.env` at the point of use.
8. **The pure core stays dependency-light** `[FC]`. Anything it needs beyond its two or three declared runtime dependencies arrives as a parameter or a callback.

## 4. Boundary with the sibling skills

Split by **question asked**, not by technology.

| Skill | Answers |
|---|---|
| **onion-architecture** (this) | *Which ring, and which way does it point?* |
| `engineering-paved-path:frontend-architecture` | *Where does this go on the client, and what crosses the Server/Client line?* |
| `engineering-paved-path:postgresql-table-design` | *How should the table look — types, indexes, constraints?* |
| `engineering-paved-path:security` | *What untrusted input does this touch, and what is the check?* |

Do not load this skill for "why is this query slow", "how do I add a framework hook", or "write this migration". Framework-specific and ORM-specific skills answer those; this one does not.

## 5. Red flags

Stop when you catch yourself writing any of these.

| Red flag | Rule broken |
|---|---|
| "It's a two-line query, I'll do it in the handler" | 1 — this is how every 400-line route file started |
| "The service can just take the container" | 3 — then the repository has no seam, and the only way to fake it is monkey-patching a private field |
| "I'll import the concrete client here, it's simpler" | 4 — the service now needs the real network to run |
| "I'll return the row, the route can map it" | 5 — a persistence row in a route couples HTTP to the schema |
| "The neighbouring slice already has that constant, I'll import it" | §1 — cross-slice import; move it to a shared place or behind a port |
| "The adapter needs a constant from the feature module" | §1 — the constant belongs beside the adapter, not in a feature |
| "I'll re-parse the body in the service to be safe" | 6 — it is already parsed; a second parse hides where the contract lives |
| "`node:fs` is fine here, it's just a read" | 4 — the port already has a read method |
| "The composition root imports modules, that's a cycle, I'll fix it" | §1 — it is the composition root; leave it |
| "I'll regenerate the baseline to get CI green" | §2 — the baseline only shrinks |

## 6. What this costs, honestly

Onion is not free and this skill does not pretend otherwise. Bogard moved his team off it because services grow into a big ball of mud regardless of how many layers guard them. Domain-Driven Hexagon warns that most projects never swap databases, so a repository justified by swappability is dead weight.

The position taken here: **the repository earns its place by isolating persistence and giving tests a seam**, not by promising portability. Where a repository is organised as vertical slices with rings inside each slice, that hybrid is the design, not a compromise on the way to something purer. Do not introduce `domain/`, `application/` and `infrastructure/` folders on top of a structure that works; name the rings where the code already sits.

## 7. Review checklist

- [ ] No ORM or SQL outside a repository file (§3.2)
- [ ] No direct database handle in a route (§3.1)
- [ ] The service takes its repository as a parameter (§3.3)
- [ ] Every new external call has a port **and** a mock (§3.4)
- [ ] No persistence row type crosses out of its module (§3.5)
- [ ] No import from another vertical slice (§1)
- [ ] Nothing in the adapter tree imports a feature module (§1)
- [ ] The pure core still declares only its intended runtime dependencies (§3.8)
- [ ] No secret read from the config object or `process.env` at the point of use (§3.7)
- [ ] The repository's own boundary gate exits 0, and the baseline did not grow (§2)
