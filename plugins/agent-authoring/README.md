# agent-authoring

Conventions for writing skills and agents, and a static audit that checks a set of them still agrees with itself.

```sh
/plugin install agent-authoring@dev-workbench
```

## What is in it

| Component | Answers | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `authoring` (skill) | Why does this skill never fire — or fire on everything? | 109 | 1 143 |
| `model-routing` (skill) | Which tier, how much effort, and is this fan-out worth it? | 115 | 1 250 |
| `scripts/audit-harness.py` | Do these files still say true things about each other? | — | — |

## The rule the authoring skill exists for

The frontmatter `description` is the only part always in context, and it is the whole of what the model sees when deciding whether to open the body. So it answers **when does this apply** — never **what does this do, step by step**.

**A description that reads like a procedure gets followed instead of the body.** Nothing errors: the model reads three summarised steps, believes it now knows the workflow, and never loads the file where the actual rules live. The result is a confident run that skipped every hard-won detail the skill was written for — and it is repeatable, which makes it worse than an unreliable failure.

| Instead of | Write |
| :--- | :--- |
| "Runs the release pipeline: validate, score, commit, push, draft" | "Use when preparing a release — a version bump, a changelog, or 'is this branch ready to ship'" |
| "Analyses TypeScript configuration and reports issues" | "Use when a type error is longer than the code that produced it, when `tsc` is slow, or when a generic will not infer" |

Four tests ship with it, to run before shipping a description: the **procedure** test (could someone act on this without opening the body?), the **symptom** test (would the sentence a frustrated person actually types match it?), the **negative** test (name a close request that must *not* fire it), and the **overlap** test against its siblings.

The negative test is the one that catches greed. It is easy to raise a trigger rate by widening a description until it matches everything nearby, and the cost is paid on every turn by every skill that now competes with it. **A description that cannot be made to fail is not a trigger, it is a category label.**

## Verify by behaviour, never by self-report

Run it on something small and real, then ask it to do the thing it must not do. A read-only agent must be **technically unable**, not merely unwilling.

**Asking a subprocess to describe its own configuration produces confident, contradictory answers.** It will tell you it has no write access while holding a tool that writes. Test what it does; never what it says about itself.

## `model-routing` — the two knobs save different things

**Model tier** lowers cost per token and latency. It does *not* reduce how many tokens get produced. **Reasoning effort** reduces the token count. Conflating them produces the specific failure of a cheap model being handed work it has to redo: the same tokens, several times, at a lower price each.

The skill routes by the shape of the work rather than by the role, and carries the trigger for overriding a default at dispatch: **when one dispatch's own scope exceeds roughly ten distinct changes or spans more than one module, upgrade it** — not for quality, but because a cheap tier does not reduce token count and an over-scoped agent pays the fresh-context restart tax on every correction round.

Its more useful half is the list of where savings actually are, in order of impact — partition the scope and name the other lanes, point agents at a map before they search, ask for a compact structured return, do not fan out when one agent suffices, choose lanes from the change rather than from a roster, and send a follow-up to a running agent instead of spawning a fresh one. **Cost comes from not duplicating work, not from making agents cheaper.**

## The audit

```sh
python3 scripts/audit-harness.py <path> [<path> ...]
```

A path can be a marketplace's `plugins/` directory, a single plugin, or a project's `.claude/` directory. No model, no network, nothing executed — it parses frontmatter and prose. Exit status is 1 if any `FAIL` was reported.

| Check | What it catches |
| :--- | :--- |
| `A1` | A description promising a roster the body never dispatches — including a name that exists nowhere at all, listed beside ones that do |
| `A2` | A fan-out table listing two or more lanes with no column saying **when each one runs**. A roster with no conditions is a roster the user has to pick from by hand |
| `A3` | A fan-out of two or more that never requires a single-message dispatch — so the lanes run in series and the parallelism was imagined |
| `A4` | A backticked `plugin:name` that does not resolve to anything in the set |

`A4` is the machine form of a rule worth stating on its own: **a backticked cross-plugin name is a promise that it resolves at install time.** If a component cannot make that promise, it names the role in prose instead. Every dependency edge in this marketplace is an application of that rule, and this check is what stops one from being forgotten.

**Warnings never fail the run.** `A3` is a warning because a serial fan-out is slow rather than wrong, and a check that blocks on a judgement call is a check that gets disabled — after which it checks nothing.

The `evals/fixtures/drifted-set` directory is a set with one of each failure in it, so you can see what the output looks like before pointing the script at something you care about:

```sh
python3 scripts/audit-harness.py evals/fixtures/
```

## What it will not do

| Not this | Why |
| :--- | :--- |
| Judge whether a skill is any good | It reads structure, not quality. A perfect description in front of a bad skill produces a reliably bad run |
| Run, dispatch or evaluate anything | It is a parser. Behaviour is measured by running the thing, which is what an eval suite is for |
| Check bare names | Only the namespaced `plugin:name` form is treated as a promise. A bare `researcher` in prose is a role, and roles are how a component refers to something it does not depend on |
| Rewrite a description for you | The four tests are for a person to apply. A description rewritten by the thing being triggered is not a test of anything |

## Dependencies

None. It is about writing skills and agents, so depending on any would be circular in spirit if not in the manifest.

## Compatibility

Claude Code >= 2.1.110. The audit script needs Python 3.10 or newer and nothing else — no YAML library, deliberately, so it runs in the environments it is most useful in.
