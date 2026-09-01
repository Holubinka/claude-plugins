# Sources

Gathered for a skill on TypeScript/Node backend structure. Grouped by the question each one
answers, with what it actually claims — a link list is not a reference file.

Where two sources disagree, that is recorded rather than resolved. A skill that flattens a real
disagreement into one rule is asserting more than its sources support.

## Where components live, and how the tree is organised

**[Node.js Best Practices §1.1 — Structure by business components](https://github.com/goldbergyoni/nodebestpractices)**
The canonical list, maintained since 2016. Organise the root by *business components* — bounded
contexts like `orders`, `users` — each with its own API, logic and data. The reasoning is scope of
change: *"every change is performed over a granular and smaller scope — the mental overload,
development friction, and deployment fear are much smaller."*

**[Node.js Best Practices §1.2 — Layer your components with 3-tiers](https://github.com/goldbergyoni/nodebestpractices)**
Inside each component: `entry-points` (controllers, consumers), `domain` (logic, services, DTOs),
`data-access`. The rule with teeth: **keep the web layer within its boundaries** — passing an
Express `req`/`res` into domain code couples the logic to the framework and makes it unreachable
from a scheduled job or a queue consumer.

**[Screaming Architecture & Colocation — thetshaped.dev](https://thetshaped.dev/p/screaming-architecture-and-colocation-nodejs-typescript-react)**
Folders named for business concepts, not technical roles. The test it offers: a layered tree answers
*"where are all my controllers?"* and cannot answer *"where is order creation?"*

**[Vertical Slice Architecture in Node.js — one folder per use case](https://thetshaped.dev/p/vertical-slice-architecture-in-nodejs-typescript-one-folder-per-use-case)**
The stronger form of the same idea, sliced per use case rather than per entity.

**[Layered architecture vs feature folders — DEV](https://dev.to/saber-amani/layered-architecture-vs-feature-folders-43lm)**
The failure mode stated plainly: with all services in one folder, *"domain boundaries blur, and
developers start calling services from other services."* Recommends the hybrid most teams land on —
features at the top level, layers inside each.

**[Bulletproof Node.js project architecture — DEV](https://dev.to/santypk4/bulletproof-node-js-project-architecture-4epf)**
Widely-cited layered layout. Useful mainly as the *contrast* case: it is the structure the two
sources above argue against at scale, and knowing why it is popular matters.

## Where business logic goes

**[Anemic Domain Model — Martin Fowler](https://martinfowler.com/bliki/AnemicDomainModel.html)**
The canonical statement of the anti-pattern: domain objects holding data and no behaviour, with all
rules in services. Fowler's nuance is the part usually dropped — a service layer is *not* the
problem, and *"service layer advocates use a service layer in conjunction with a behaviourally rich
domain model."*

**[Domain Logic Patterns: Transaction Script, Domain Model, Table Module & Service Layer](https://chanhle.dev/en/blog/enterprise-domain-logic-patterns)**
The four classical options and when each fits. Names the common anti-pattern precisely: a Domain
Model *structure* with Transaction Script *behaviour*.

**[Rich vs. Anemic Domain Model — Educative](https://www.educative.io/courses/hexagonal-architecture-web-apps/rich-vs-anemic-domain-model)**
The practical version of the same distinction, inside a hexagonal-architecture context.

**[An Introduction to Domain-Driven Design — Khalil Stemmler](https://khalilstemmler.com/articles/domain-driven-design-intro/)**
DDD written specifically against TypeScript and Node rather than translated from Java or C#, which
is what makes it usable here.

**[Four-Layer Module Architecture for TypeScript & Express](https://shadisbaih.medium.com/module-architecture-with-four-layers-presentation-application-domain-infrastructure-63f042a7ddca)**
Presentation / application / domain / infrastructure, worked in TypeScript.

**Disagreement to preserve.** Fowler and the DDD sources want behaviour on the domain objects.
Node's own best-practices list is comfortable with services holding the logic, and much of the Node
ecosystem ships transaction scripts and is fine. The honest rule is about *where the rule is
enforced consistently*, not about which shape wins — and a skill that picks a winner is asserting
more than these sources do.

## Constants, utils, helpers

**[How To Write Maintainable Utility Functions In TypeScript — Nazar Boyko](https://www.nazarboyko.com/articles/maintainable-utility-functions-typescript)**
The line worth quoting: *a folder called `utils` is technical debt with a smile.* The mechanism —
it starts as innocent helpers and becomes 1500 lines nobody can inventory.

**[File Naming Conventions — DEV](https://dev.to/damiansiredev/file-naming-conventions-keep-your-project-clean-and-readable-1plk)**
Avoid `helpers.ts`, `utils.ts`, `common.ts`. Name for purpose. Constants in a file named as such
rather than folded into a general utility bucket.

**[basarat/typescript-book — style guide](https://github.com/basarat/typescript-book/blob/master/docs/styleguide/styleguide.md)**
One of the longest-standing TypeScript style references; useful for naming and file conventions
rather than architecture.

**Note.** This marketplace's own `frontend-architecture` skill already carries a **utils / helpers /
lib** distinction that is language-neutral — *knows our domain* vs *would drop into an unrelated
project unchanged* vs *a preconfigured integration*. The backend skill should reuse that test rather
than invent a second one.

## Patterns — when, and when not

**[Rule of three (computer programming) — Wikipedia](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming))**
Copy once; abstract on the third. The reasoning matters more than the number: with two examples you
do not yet know the shape of the abstraction, or whether there is one.

**[Abstraction: The Rule Of Three — Los Techies](https://lostechies.com/derickbailey/2012/10/31/abstraction-the-rule-of-three/)**
The longer argument for the same rule.

**[The Rule of Three: Applying abstractions and patterns — Holden Rehg](https://holdenrehg.com/blog/2021-09-20_rule-of-three)**
Applies it specifically to reaching for a design pattern.

**[Code Smell 273 — Overengineering](https://maxicontieri.substack.com/p/code-smell-273-overengineering)**
Catalogue entry: unnecessary abstraction layers, patterns applied without a forcing requirement.

**[Over-engineering examples in code — Jamie Wen](https://jamiewen00.medium.com/over-engineering-examples-in-code-21c365ae4ecc)**
Concrete before/after examples, which is what a skill needs — a principle without a shape to
recognise does not change behaviour.

**[Stop Overengineering — DEV](https://dev.to/thebitforge/stop-overengineering-how-to-write-clean-code-that-actually-ships-18ni)**
Includes the wrapper rule: know what you want from wrapping a library before wrapping it, otherwise
use the library.

## TypeScript, and how much of it

**[Node.js Best Practices §1.6 — Use TypeScript sparingly and thoughtfully](https://github.com/goldbergyoni/nodebestpractices)**
The uncomfortable source, and the reason to keep it. It cites research that TypeScript catches
roughly 20% of bugs earlier and 80% escape type checking, and argues that sophisticated type-level
code raises complexity — which itself raises bug count and fix time.

**This contradicts the direction of most TypeScript writing, including this marketplace's own
`typescript-expert` skill.** Both belong: `typescript-expert` is for when a type problem is already
in front of you; this is the check on reaching for one when it is not. A backend skill that cites
only the enthusiastic sources is selecting its evidence.

**[TypeScript Best Practices for Production Code in 2026 — DEV](https://dev.to/_d7eb1c1703182e3ce1782/typescript-best-practices-for-production-code-in-2026-lb0)**
The current baseline set: `strict`, `noUncheckedIndexedAccess`, no `any`, discriminated unions for
async state, `satisfies` for config, `import type`, explicit return types on exports.

**[Generics vs Union types — Mihai Oltean](https://blog.mihaioltean.com/typescript-stories-generics-vs-union-types)**
The decision most generics advice skips: often a union is the right answer and a generic is the
reflex. Directly useful for the generics section.

**[TypeScript Best Practices for Large-Scale Applications — Abhishek Gautam](https://www.abhs.in/blog/typescript-best-practices-large-scale-applications-2026)**
Constraints on generics rather than bare `<T>`; where inference is enough and an annotation is noise.

## Still to find

Named here so the gaps are visible rather than quietly unresearched:

- A source on **repository pattern in Node specifically** — when it earns its place over calling the
  ORM directly, which is the most common over-application in this ecosystem.
- Something measured rather than argued on **feature-folders vs layers at scale**. Every source above
  is reasoning, not evidence.
- **Error handling and result types** — where a backend puts its failure modes. Adjacent to structure
  and not covered by anything gathered here.
