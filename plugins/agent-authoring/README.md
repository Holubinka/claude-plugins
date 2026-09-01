# agent-authoring

Conventions for writing skills and agents, a static audit that checks a set of them still agrees with itself, and a local log for recording how an installed plugin actually behaved.

**The log works for every plugin in this marketplace, not only this one.** It is here because this is where the question *how do you know your components are any good* already lives.

```sh
/plugin install agent-authoring@dev-workbench
```

## What is in it

| Component | Answers | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `authoring` (skill) | Why does this skill never fire — or fire on everything? | 109 | 1 143 |
| `model-routing` (skill) | Which tier, how much effort, and is this fan-out worth it? | 115 | 1 250 |
| `plugin-feedback` (skill) | That went wrong — how do I record it now and send it later? | 115 | 1 120 |
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
| `A4` | A backticked `plugin:name` that does not resolve — **or that names a plugin the manifest declares no dependency on** |

`A4` is the machine form of a rule worth stating on its own: **a backticked cross-plugin name is a promise that it resolves at install time.** If a component cannot make that promise, it names the role in prose instead. Every dependency edge in this marketplace is an application of that rule, and this check is what stops one from being forgotten.

**Resolving inside the repository is not resolving at install time**, which is the half the check originally missed. A component naming another plugin's skill passed as long as both directories happened to sit side by side — and would have failed for anyone installing that plugin on its own. `A4` now reads the manifest, so the promise has to be backed by a declared dependency and not by co-location. `evals/fixtures/undeclared-edge` is a set with exactly that fault.

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

## The feedback log

The failures worth reporting happen mid-task, when nobody intends to stop and write a bug report — and by the evening the detail that made it reproducible is gone. So `plugin-feedback` records it in one line now and leaves the decision to send it for later.

```sh
scripts/feedback.sh collect                     # scan local transcripts — nothing to compose
scripts/feedback.sh usage                       # what fired, how often, out of how many sessions
scripts/feedback.sh record <plugin> <verdict>   # worked | misfired | did-not-fire
scripts/feedback.sh list
scripts/feedback.sh export-issue <id>           # a body for the GitHub issue form
scripts/feedback.sh export-case <id> <dir>      # prompt.md + graders/criteria.md, for a pull request
```

**Nothing touches the network.** The log is local and moves only when someone exports an entry and pastes it themselves. Adding telemetry to prose-ware would breach [docs/security.md](../../docs/security.md) and would deserve an uninstall.

**`collect` is the half that actually happens.** Claude Code already writes a transcript per session; it reads them for structural facts only — component names, invocation counts, turn counts, token totals — and never prompt text, output text or file contents. It asks nothing of a busy person, which is the only reason it will still be running in three weeks.

It also produces the number that is unavailable without telemetry: **how often a component fired out of sessions actually run.** A maintainer cannot have it, because there is no denominator across other people's machines. For your own usage there is.

**For the general version of that question, use `session-report` in the official marketplace instead** — same source, wider window, richer breakdowns, an explorable HTML report. `collect` here is narrower on purpose: it writes into this log, so usage sits beside the failures recorded by hand, and *"this fired twelve times and here are the three entries where it went wrong"* is a sentence neither half produces alone. If you are not using the manual half, you do not need this one.

**A component at 0% is the finding**, and nothing else can see it: it is charging its description on every turn and returning nothing. An empty report is a finding too — either nothing is installed, or the descriptions are not matching the work being done.

Two of the three manual verdicts exist for reasons that are easy to miss:

**`did-not-fire` is the one to bother with.** Nobody reports it spontaneously — nothing visibly breaks, you do the work yourself and move on — so from a maintainer's seat it is indistinguishable from success. It is also the expensive failure: a component that never fires is pure always-on cost.

**`worked` is not flattery.** It is the only evidence a component earns its cost. Without it the log is a list of complaints, and a list of complaints argues for deleting everything.

**`export-case` is what closes the loop.** It writes the case skeleton straight into this marketplace's layout, so a report can arrive as a pull request carrying its own regression test — which is a thing a maintainer would otherwise have to write themselves, from a description of something they cannot see.

### Where it lives, and the catch

Default is `${CLAUDE_PLUGIN_DATA}`, which Claude Code **deletes when the plugin is uninstalled from its last scope** — so the log explaining why someone uninstalled something vanishes exactly when they uninstall it. Set `PLUGIN_FEEDBACK_DIR` to a path you own, or export before uninstalling.

The default stays there anyway, because writing outside the project uninvited is what [docs/security.md](../../docs/security.md) forbids. The constraint produced the better design: the log is a staging area and export is a deliberate act.

## Dependencies

None. It is about writing skills and agents, so depending on any would be circular in spirit if not in the manifest.

## Compatibility

Claude Code >= 2.1.110. The audit script needs Python 3.10 or newer and nothing else — no YAML library, deliberately, so it runs in the environments it is most useful in.
