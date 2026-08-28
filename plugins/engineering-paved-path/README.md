# engineering-paved-path

Six engineering skills that more than one agent needs, packaged once so nothing has to copy them. `architecture-review` and `sdd-engineering` both depend on this plugin; you can also install it on its own and invoke the skills by hand.

```sh
/plugin install engineering-paved-path@dev-workbench
```

## What is in it

| Skill | Answers | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `onion-architecture` | Which ring does this backend code sit in, and which way may it point? | 122 | 2 934 |
| `frontend-architecture` | Where does this frontend file go, and how is it split? | 117 | 1 966 |
| `security` | What untrusted input does this touch, and what is the check? | 72 | 3 345 |
| `mermaid-diagram` | Which diagram type, and how do I write it? | 63 | 1 794 |
| `postgresql-table-design` | How should this table look — types, indexes, constraints? | 44 | 3 952 |
| `typescript-expert` | How do I express this in the type system? | 96 | 3 619 |

**Always-on** is the `description` line, in tokens. It is in context for every session the plugin is enabled, because that line is how Claude decides whether the skill is relevant. **On invoke** is the body of `SKILL.md`, paid only when the skill fires. Reference files under each skill load on demand and are not counted here — `zod`-scale reference trees are the reason that distinction matters.

Total always-on cost: **514 tokens** across 20 files, about 200 KB on disk.

## Invoking them

Skills are namespaced by plugin:

```
/engineering-paved-path:onion-architecture
/engineering-paved-path:frontend-architecture
/engineering-paved-path:security
/engineering-paved-path:mermaid-diagram
/engineering-paved-path:postgresql-table-design
/engineering-paved-path:typescript-expert
```

Most of the time you will not type these. Claude loads a skill when its `description` matches what you are doing, and the agents in `sdd-engineering` and `architecture-review` name them directly in their own routing tables.

## The one thing to know before using the architecture skills

**`onion-architecture` and `frontend-architecture` do not know your folder names.** Both open with a *Read the repository first* step that establishes three things: whether a boundary gate already exists (dependency-cruiser, `eslint-plugin-boundaries`, an Nx constraint), which directories hold which kind of code, and where the composition root is.

Where a gate exists, **the gate is the authority and the skill is commentary.** Where none exists, the skill says so and applies its rules as a proposal rather than as a finding — because an architecture rule invented on the spot and reported as the repository's own is worse than no rule: the next reader obeys it believing someone decided it.

The code samples inside these skills are shapes to recognise, not paths to open. They use plausible file names so the structure is readable; none of them is a citation.

## What each skill covers

**`onion-architecture`** — the five rings and the one rule that generates them all (dependencies point inward). A four-step placement procedure, eight rules, an escalation order for when the boundary gate fails, and three reference files: what goes in each file of a module, when a dependency needs a port, and which ring gets which test.

**`frontend-architecture`** — six principles for React and the Next.js App Router, a five-step placement procedure, and three reference files covering folder strategies, component splitting and state placement, and App Router specifics including the `'use client'` boundary. It answers *where does it go*, not *is it written correctly*.

**`security`** — OWASP-grounded review of untrusted input, with checklists, unsafe/safe code pairs, and a references file pointing at the external sources it draws on. `spec-creator` in `sdd-engineering` invokes it before writing a spec's untrusted-inputs section.

**`mermaid-diagram`** — a decision guide for picking the diagram type, syntax for eleven of them, and seven worked templates drawn from one running subject so the shapes are comparable. Gantt and pie deliberately have no template: neither has an honest subject, and inventing plausible numbers for a diagram is the same failure as seeding fake rows to make a screen look fuller.

**`postgresql-table-design`** — column types, keys, indexes and constraints, in one file with no reference tree.

**`typescript-expert`** — type-level work: generics, inference, declaration merging. Ships a strict `tsconfig` reference, a utility-types file, a cheatsheet, and `ts_diagnostic.py`, which reports on a project's TypeScript configuration and common misconfigurations.

## What is deliberately not here

Framework and library skills — React, Next.js, Fastify, Zod, an ORM. They are being written separately and will arrive as minor releases. Two consequences worth knowing now:

- The agents in `sdd-engineering` route to skills through tables in their own prompts. Those tables list what exists today; adding a skill here means adding its row there, which is a minor bump for both plugins.
- Until they exist, `implementation-planner` and `implementer` are told to cite the repository's own conventions where no skill covers the work, rather than to cite nothing.

## Dependencies

None. This plugin is the bottom of the graph, which is why it is built and tagged first.

## Compatibility

Claude Code >= 2.1.110 — the floor for version-constrained plugin dependencies, which the plugins that depend on this one use.
