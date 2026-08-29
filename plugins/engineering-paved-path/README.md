# engineering-paved-path

Eleven engineering skills that more than one agent needs, packaged once so nothing has to copy them. Five other plugins in this marketplace depend on it; you can also install it on its own and invoke the skills by hand.

```sh
/plugin install engineering-paved-path@dev-workbench
```

## What is in it

| Skill | Answers | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `project-commands` | What does *this* repository run to typecheck, lint or test? | 128 | 1 147 |
| `severity-scale` | Is this finding `critical`, and what does that stop? | 123 | 1 075 |
| `onion-architecture` | Which ring does this backend code sit in, and which way may it point? | 122 | 2 916 |
| `frontend-architecture` | Where does this frontend file go, and how is it split? | 117 | 1 951 |
| `security` | What untrusted input does this touch, and what is the check? | 109 | 3 420 |
| `typescript-expert` | How do I express this in the type system? | 96 | 3 827 |
| `mermaid-diagram` | Which diagram type, and how do I write it? | 63 | 1 798 |
| `postgresql-table-design` | How should this table look — types  indexes  constraints? | 44 | 3 951 |
| `scoped-change` | Am I building or changing more than was asked? | 123 | 1 008 |
| `systematic-debugging` | Something is wrong. What is actually causing it? | 120 | 1 210 |
| `verification-before-completion` | Can I say this is done? | 102 | 1 120 |

**Always-on** is the `description` line, in tokens. It is in context for every session the plugin is enabled, because that line is how Claude decides whether the skill is relevant. **On invoke** is the body of `SKILL.md`, paid only when the skill fires. Reference files under each skill load on demand and are not counted here — that distinction is why a skill can carry a large reference tree without costing anything until it is used.

Total always-on cost: **1143 tokens** across 11 skills.

## Invoking them

Skills are namespaced by plugin:

```
/engineering-paved-path:project-commands
/engineering-paved-path:severity-scale
/engineering-paved-path:onion-architecture
/engineering-paved-path:frontend-architecture
/engineering-paved-path:security
/engineering-paved-path:typescript-expert
/engineering-paved-path:mermaid-diagram
/engineering-paved-path:postgresql-table-design
/engineering-paved-path:systematic-debugging
/engineering-paved-path:verification-before-completion
/engineering-paved-path:scoped-change
```

Most of the time you will not type these. Claude loads a skill when its `description` matches what you are doing, and the agents in the plugins that depend on this one name them directly in their own routing tables.

## The two skills the other plugins are built on

**`project-commands`** exists because a command typed from habit is a guess wearing the costume of a fact. It resolves typecheck, lint and test **independently**, stopping at the first source that answers: the task itself, then a convention file, then the CI workflow, then the manifest's script table — and the runner prefix comes from the lockfile, never from memory. The rule it enforces in one line:

> You may run a script whose definition you have read. You may never run a script whose existence you are guessing at.

Finding nothing is a valid answer. The skill says which four sources it read and that each was empty, rather than inventing a command or installing a tool.

**`severity-scale`** defines `critical` / `major` / `minor` / `note` by **what each level stops**, not by how bad it feels — so two reviewers converge without negotiating. Three rules travel with it:

| Rule | Why |
| :--- | :--- |
| A deterministic finding outranks a model-produced one, and nothing may downgrade it | A failing test is reproducible. A read of the code is not, however right it is |
| A model-produced `critical` must survive an adversarial pass before it blocks anything, and **uncertain counts as refuted** | The first time a gate refuses a correct change on a finding nobody can reproduce, the gate starts getting bypassed |
| A model finding on a line the branch never touched is a `note` | It is a pre-existing condition someone chose to mention, not a consequence of this change |

## The two that everything else leans on

**`verification-before-completion`** holds one rule: *if you have not run the command in this turn, you cannot say it passes.* Its useful half is that a check has **three** outcomes, not two — passed, failed, and **did not run**. "Nothing found" and "nothing looked at" produce the same silence and mean opposite things, and a linter with no files, a suite that collected zero tests, or a gate the repository never defined all exit 0 while proving nothing.

Six components in this marketplace were each restating a piece of that rule. They now point at it instead, which is the duplication [docs/COST-BASELINE.md](../../docs/COST-BASELINE.md) nominates as its first optimisation target: an agent prompt is paid on every dispatch, a skill body only when it fires.

**`systematic-debugging`** holds the other: *no fix before the cause is known.* A change that makes a symptom disappear without an explanation has either fixed the defect or moved it, and you cannot tell which from the outside — the second being worse than leaving it, because the next person inherits a bug with a comment above it saying it was handled.

It starts from **an observed symptom you can point at**. Reading code to judge whether it looks right, with nothing having gone wrong, is a review and routes elsewhere. That boundary is not decorative: it was added after a routing probe caught the skill firing on "is this function correct?"

## The half a plugin cannot do

**`scoped-change`** holds two failures that are the same failure pointed different ways: building more than was asked, and changing more than was needed. Both feel like care while you are doing them, and both read as noise to a reviewer, who cannot tell a deliberate improvement from an accident without asking.

Its test for anything in a diff: **would this line be here if the request had never arrived?**

But the skill can only reach half the problem, and the README should say so rather than imply otherwise. **A skill fires on a request; over-building is an impulse.** "Make it configurable" reaches this skill. The urge to add a factory while implementing something perfectly well-specified does not, because nothing in the request signals it.

That half is always-on behaviour, and always-on belongs in the repository's own `CLAUDE.md` — where it costs the user's own budget, knowingly, rather than a plugin's. [`always-on.md`](skills/scoped-change/always-on.md) carries six lines to copy in, and the reasoning for why this marketplace does not inject them with a hook the way some others do: a plugin that installs its opinions into every turn has taken a decision belonging to whoever owns the repository.

## The one thing to know before using the architecture skills

**`onion-architecture` and `frontend-architecture` do not know your folder names.** Both open with a *Read the repository first* step that establishes three things: whether a boundary gate already exists (dependency-cruiser, `eslint-plugin-boundaries`, an Nx constraint), which directories hold which kind of code, and where the composition root is.

Where a gate exists, **the gate is the authority and the skill is commentary.** Where none exists, the skill says so and applies its rules as a proposal rather than as a finding — because an architecture rule invented on the spot and reported as the repository's own is worse than no rule: the next reader obeys it believing someone decided it.

The code samples inside these skills are shapes to recognise, not paths to open. They use plausible names drawn from one running subject so the structure is readable; none of them is a citation, and none of them describes a real repository.

## What each skill covers

**`onion-architecture`** — the five rings and the one rule that generates them all (dependencies point inward). A four-step placement procedure, eight rules, an escalation order for when the boundary gate fails, and three reference files: what goes in each file of a module, when a dependency needs a port, and which ring gets which test.

**`frontend-architecture`** — six principles for React and the Next.js App Router, a five-step placement procedure, and three reference files covering folder strategies, component splitting and state placement, and App Router specifics including the `'use client'` boundary. It answers *where does it go*, not *is it written correctly*.

**`security`** — OWASP-grounded review of untrusted input, with checklists, unsafe/safe code pairs, and a references file pointing at the external sources it draws on. The pairs are written in one stack so they are comparable; every rule is about a boundary that exists in all of them. `spec-creator` in `sdd-engineering` invokes it before writing a spec's untrusted-inputs section, and `review-lenses` reaches it on any diff touching auth, input parsing, uploads or secrets.

**`typescript-expert`** — type-level work: generics, inference, declaration merging. Ships a strict `tsconfig` reference, a utility-types file, a cheatsheet, and `ts_diagnostic.py`.

**`mermaid-diagram`** — a decision guide for picking the diagram type, syntax for eleven of them, and seven worked templates drawn from one running subject so the shapes are comparable. Gantt and pie deliberately have no template: neither has an honest subject, and inventing plausible numbers for a diagram is the same failure as seeding fake rows to make a screen look fuller.

**`postgresql-table-design`** — column types, keys, indexes and constraints, in one file with no reference tree.

## `ts_diagnostic.py` has three outcomes, not two

The bundled diagnostic reports on a project's TypeScript configuration. It obeys `project-commands` without a model in the loop, and the reason is worth stating, because the script used to get it wrong:

**It discovers the sources instead of assuming `src/`.** tsconfig's `include` and `files` first, then `git ls-files`, then a walk. A repository whose code lives in `packages/*/src`, `app/` or `lib/` is not a repository with no TypeScript in it.

**Every check can say `not scanned`.** An empty grep and a missing directory used to print the same green tick — so the script reported *zero* `any` usages and *zero* unsafe assertions for a codebase full of both. A false clean is the worst failure a diagnostic can have, because it is indistinguishable from good news.

**It never reads a verdict through a pipe.** `tsc --noEmit | head -20` throws away the exit code, and the exit code is the verdict.

## What is deliberately not here

Framework and library skills — React, Next.js, Fastify, Zod, an ORM. They are being written separately and will arrive as minor releases. Two consequences worth knowing now:

- The agents in the plugins that depend on this one route to skills through tables in their own prompts. Those tables list what exists today; adding a skill here means adding its row there, which is a minor bump for both plugins.
- Until they exist, nothing here names a skill that is not installed. Where no skill covers the work, the agents are told to cite the repository's own conventions rather than to cite nothing — a backticked name is a promise, and a promise with nothing behind it sends a reader looking for a file that does not exist.

## Dependencies

None. This plugin is the bottom of the graph, which is why it is built and tagged first.

## Compatibility

Claude Code >= 2.1.110 — the floor for version-constrained plugin dependencies, which the plugins that depend on this one use.
