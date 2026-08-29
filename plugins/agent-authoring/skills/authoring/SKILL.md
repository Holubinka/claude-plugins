---
name: authoring
description: "Conventions for writing a skill or an agent that fires when it should and does what it says. Use when creating one, editing one that triggers too often or never, deciding whether a job wants a skill or a subagent, choosing a tools allowlist, or reviewing a set of them for overlap. Its sharpest rule concerns the frontmatter description, which is the only part always in context and the part most often written as a summary of the body."
metadata:
  version: "1.0.0"
keywords: [authoring, skills, agents, frontmatter, description]
---

# Authoring skills and agents

Two artefacts, one shared failure: **the part that is always in context gets written as a summary of
the part that is not.**

## The description is a trigger, never a procedure

The frontmatter `description` is the only thing loaded on every turn, and it is the whole of what the
model sees when deciding whether to open the body. So it answers **"when does this apply?"** — never
"what does this do, step by step".

**A description that reads like a procedure gets followed instead of the body.** This is the failure
worth naming, because nothing errors: the model reads three summarised steps, believes it now knows
the workflow, and never loads the file where the actual rules live. The result is a plausible,
confident run that skipped every hard-won detail the skill was written for.

Write it out of the trigger's vocabulary, not the author's:

| Instead of | Write |
| :--- | :--- |
| "Runs the release pipeline: validate, score, commit, push, draft" | "Use when preparing a release — a version bump, a changelog, or 'is this branch ready to ship'" |
| "Analyses TypeScript configuration and reports issues" | "Use when a type error is longer than the code that produced it, when `tsc` is slow, or when a generic will not infer" |
| "Manages database migrations" | "Use when adding a column, backfilling existing rows, or when a migration failed halfway and the schema and the history disagree" |

**Pack in the symptoms a person would actually type** — the error string, the file name, the phrase
they would use when frustrated. Those are what the description is matched against.

Three more rules that hold everywhere:

- **`name` must match the directory or filename**, and must be lowercase with hyphens.
- **Never mention what the body does mechanically.** Every sentence spent on mechanism is a sentence
  not spent on the trigger, at the one cost that is paid on every single turn.
- **Length is a real cost.** The description is in context whether or not the skill ever fires. Long
  enough to be lexically specific; not a second body.

[`description-tests.md`](description-tests.md) has four checks to run against a description before
shipping it, including the overlap check that catches two skills competing for the same request.

## Body shape

Do **not** repeat the description as the opening line — it is already in context. Start with the name
and one line of what this is, then:

- **When to use** — concrete situations.
- **When NOT to use** — a table routing to the sibling that fits better. This is what keeps
  overlapping skills distinguishable, and it is the section most often skipped. Add a row whenever a
  new sibling lands beside an existing one.
- **The steps**, in the order they are done.
- **One worked example** with realistic output, and a sentence on what the interesting part of it
  was. One good example beats three thin ones.
- **Common mistakes**, as a `| Mistake | Fix |` table, **populated from failures actually observed**.
  A table of hypotheticals reads the same and teaches nothing.

Aim for a body under about 1 500 words. Past that, move reference material into a sibling file and
point at it: a reference file loads on demand and costs nothing until it does.

**Bundled resources** go in `scripts/` (executable) or `assets/` (pasted or embedded) beside the
skill, referenced by path. A snippet longer than about thirty lines that every invocation would
otherwise retype belongs in a file — it gets tested once instead of re-derived each run.

## Skill or agent

A skill is knowledge loaded into the current context. An agent is **a separate context with its own
permissions**. That difference is the entire test: reach for an agent when you need isolation or
restriction, not when you need instructions.

[`skill-or-agent.md`](skill-or-agent.md) has the four conditions an agent needs, and the overlap check
that decides whether a new role is a role at all.

## Verify by behaviour, never by self-report

Run it on something small and real, then **ask it to do the thing it must not do.** A read-only agent
must be *technically unable*, not merely unwilling.

**Asking a subprocess to describe its own configuration produces confident, contradictory answers.**
It will tell you it has no write access while holding a tool that writes. Test what it does; never
what it says about itself.

For a skill, the equivalent test is a request that *should not* fire it. A skill that fires on
everything has a description that describes a category rather than a trigger, and it costs every
turn.
