# Measuring whether these plugins work

Everything here is unproven. Ten plugins, thirty-four components, forty-three eval cases that
have not run — and prose that sounds right, which is the least reliable signal there is.

This is how that changes. [COST-BASELINE.md](COST-BASELINE.md) answers *did a change make a run
cheaper without breaking it*. This answers the prior question: **does a component do its job on
real work, and how would you know if it stopped.**

## The problem with measuring prompt-ware

Almost every obvious metric rewards the wrong behaviour, and each one is easy to move in the
wrong direction without noticing.

| Metric | What it actually rewards |
| :--- | :--- |
| Findings per review | Padding. A reviewer that files three weak findings scores higher than one that files one real one and says the rest is clean |
| How often a skill fires | Greedy descriptions. Widening a trigger until it matches everything raises the number and charges every other skill for it |
| Eval pass rate | Writing easy cases. You wrote them; a suite you can always pass is measuring your case-writing |
| Output length, or number of sections | Verbosity |
| "It felt better" | Recency. The last run is always the most vivid |

So the measurements below are built to be **falsifiable in the direction that flatters you**.
Every one of them has a paired negative, and the negative is the half that matters.

## Tier 1 — three things that predict everything else

### A. Did it fire when it should, and stay quiet when it should not?

A skill's `description` is loaded on every turn whether or not it ever fires. **A skill that
never fires is pure cost; a skill that always fires is worse**, because it also displaces the
one that should have.

Collect two sets of real requests — ten each is enough to be informative:

- **Positives:** requests where this skill is the right one. How many loaded it?
- **Negatives:** requests that are *close but wrong* for it. How many loaded it anyway?

**Precision is the number to defend.** Recall is easy to buy — widen the description and it goes
up — and the price is paid on every turn by everything else. A component that fires on eight of
ten positives and zero of ten negatives is in better shape than one that fires on ten and four.

Record the misses individually rather than as a rate. *Which* request failed to load it tells you
what vocabulary the description is missing; a percentage tells you nothing you can act on.

### B. Did the boundary hold?

Every component here is defined by **what it refuses**. That is checkable in a way that "was the
review any good" is not.

Each component's `## Never` list and each plugin's negative eval cases are already the list. The
measurement is: on a real run, did it do any of them?

**A violation is a defect, not a percentage.** List them individually and never summarise them
into a rate — the same rule [COST-BASELINE.md](COST-BASELINE.md) applies to critical failures.
One boundary breach in fifty runs is a bug with a reproduction, not a 98% score.

The per-plugin table below names the single breach that would matter most for each.

### C. Did it change the outcome?

The question a plugin has to answer to earn its always-on cost: **would this task have gone
differently without it?**

Two ways to find out, one rigorous and expensive, one cheap and nearly as useful:

**The paired run.** Same task, same starting commit, two worktrees — one with the plugin enabled,
one without. Compare what each caught, what each cost, and how many turns each took. This is the
only ablation that means anything on real work, and it costs double. Do it for a handful of
representative tasks, not routinely.

**The intervention log.** Far cheaper and higher signal than it looks: after each real session,
write one line for every time you had to correct the plugin. Not what it did well — only the
corrections. Three weeks of that tells you more than any dashboard, because the corrections
cluster, and the cluster is the thing to fix.

## Tier 2 — the honest counters

Worth recording, not worth optimising on their own.

| Counter | Where it comes from | What it tells you |
| :--- | :--- | :--- |
| Cost per task, and `reread_ratio` | `sdd-engineering:workflow-retro`'s `stats.sh` | Whether a run's bill is output or re-reading. It is almost always re-reading |
| Turns to done | `stats.sh` — `agents[].turns` | Whether a component converges or loops |
| Fix rounds used | the run's own report | Two is the cap; hitting it every time means the reviews and the implementer disagree systematically |
| Lanes skipped by the fan-out | `review-diff`'s `## Lanes` section | Whether the size gate is doing anything. If nothing is ever skipped, the gate is not tuned |

## What "working" means, per plugin

For each, the single observable worth watching, and the failure that would matter most.

| Plugin | Working when | The breach that would matter most |
| :--- | :--- | :--- |
| `engineering-paved-path` | `project-commands` reports a lane as having no command rather than inventing one; `ts_diagnostic.py` prints `not scanned` on a repository it cannot scan | A gate reported green that was never run |
| `research-tools` | Structural questions go to `investigator` and cost a fraction of a `researcher` run | `researcher` answering a "which modules import X" question at ten times the price |
| `architecture-review` | It returns empty findings tables on clean diffs, with the clean section filled in | Reporting its own rules as your repository's, where your repository has none |
| `review-lenses` | You act on most of what it files, and it files few | A `critical` that nobody could reproduce — the first one teaches people to bypass the gate |
| `test-discipline` | Regression tests are observed red before the fix | A loosened assertion, which is indistinguishable from a correct fix afterwards |
| `refactor-safely` | Characterisation tests are green before any structure moves | An N+1 "fixed" during a cleanup, changing result ordering |
| `change-docs` | Drift mode fixes the false sentence and nothing else | A `CLAUDE.md` quietly edited, overwriting a deliberate record |
| `sdd-engineering` | Every acceptance criterion becomes a numbered requirement or is named under out-of-scope | A plan-verifier report of all-`MET` rows for a feature missing something a human approved |
| `agent-authoring` | The audit fails on a set that has drifted | It passing a set with a backticked cross-plugin name that resolves to nothing |
| `hook-guardrails` | `selftest.sh` stays green, and the push guard has blocked at least one real push | It blocking a harmless command — the first false refusal is when people disable it |

**The right-hand column is the more useful one.** A component that has never exhibited its worst
failure has either not been used enough or is working; a component that exhibits it once has a
bug with a reproduction attached.

## Testing on real tasks

### Use real work

A fixture measures whether the fixture was plantable. Real work has the property fixtures cannot
fake: **you do not know the answer in advance**, so you cannot unconsciously grade toward it.

Pick tasks you were going to do anyway. The measurement is a side effect of doing them, which is
the only way it survives past the second week.

### Change one thing

The rule from [COST-BASELINE.md](COST-BASELINE.md) applies here unchanged: a run that differs in
two ways answers no question, and the answer it appears to give is the one you were hoping for.

### Enough runs to not be an anecdote

Three runs per configuration for anything you intend to quote, and report the median. One run is
a story. Two runs that agree are a coincidence you have not tested.

For boundary breaches (Tier 1B), one is enough — you are looking for existence, not frequency.

### The log entry

One line per session, written at the end while it is still true:

```
<date> <plugin/component> <task in five words>
  fired: yes/no — should it have?
  corrected: <what you had to fix, or "nothing">
  would it have gone differently without: yes/no/unknown
```

The third line is the one people skip and the one that decides whether the plugin stays.

### When to stop measuring something

When two consecutive weeks of the log show no corrections for a component, stop logging it and
spend the attention on one that still produces them. **A measurement that always comes back clean
is costing you attention and telling you nothing** — which is the same argument these plugins make
about a review lane that never fires.

## When other people are using it

Everything above assumes you are the user and can watch your own sessions. Once other people
install these, almost none of it is available: their sessions are local, their transcripts are
their code, and nothing here calls the network — [security.md](security.md) forbids it without an
explicit justification, and prose-ware that phones home would deserve to be uninstalled.

So the question changes from *what do I measure* to **what will people actually tell me, and what
will they never tell me.**

### The asymmetry that decides everything

**Nobody files an issue saying a skill correctly stayed quiet.** Nobody files one saying it fired
at the right moment either. What arrives unprompted is a narrow slice: it did something visibly
wrong, or it got in the way.

Which means the incoming signal is biased entirely toward **false fires**, and you will hear almost
nothing about the opposite failure — the skill that should have loaded and did not. That one costs
more: the person did the work themselves, got a worse result than they could have, and moved on
with nothing to report. It looks exactly like success from where you are sitting.

The only fix is to ask for it directly, which is why `.github/ISSUE_TEMPLATE/did-not-fire.yml`
exists as its own form and opens by saying please file these. A silent failure has to be solicited
or it does not arrive.

### The statistic worth keeping

Not installs, not stars, not issue volume. **Distinct reproduced failures per component.**

A report becomes a number only once someone has reproduced it and written a case. Until then it is
an anecdote — and for prose-ware, an unreproduced anecdote is often a description of a different
model version, a different prompt, or a plugin that was not actually enabled.

| What to count | Why |
| :--- | :--- |
| Distinct reproduced failures, per component | The only thing that means a component has a real defect |
| Reports that could **not** be reproduced | A rising number here means the reports lack detail — fix the form, not the component |
| Time from report to case | The case is the artefact. A report that never becomes one has taught nothing |
| Components with zero reports over a long period | Ambiguous, and worth naming as ambiguous: unused, or working. Do not read it as working |

**Issue volume per component is not a quality signal.** The most-used component collects the most
reports, and a component nobody has installed collects none. Divide by nothing and you learn
nothing; there is no denominator available without telemetry, and inventing one is worse than
having none.

### Make the report an eval case, or it will not survive

The two issue forms are built backwards from the case format: the request becomes `prompt.md`, and
*what it should have done, and how you would tell* becomes `graders/criteria.md`. That last field is
doing the real work — it asks for the same thing rule 1.2 in [evals.md](evals.md) asks of every
case, in the reporter's own words:

> If two people read your answer, would they agree on whether a given response passes?

A report that cannot answer that is not actionable, however clearly it describes frustration. A
report that can is already half a regression test.

**Ask for the version of both the plugin and Claude Code.** Behaviour here is model-dependent, and a
report against an unknown pair cannot be reproduced or closed.

**Ask for redaction, and say why.** People will paste their code. Say in the form that the shape of
what happened is what matters, and give them placeholders to use.

### What a maintainer owes back

The suite is the shared record. When a reported failure is reproduced, [evals.md](evals.md) §6.3
requires a case in the same change as the fix — and that case is what the reporter gets in return:
a permanent guarantee that this specific thing will not come back quietly.

Say so in the issue when you close it. It is the difference between a report feeling like a
complaint and feeling like a contribution, and it is the only reason anyone files a second one.

## What this does not measure

**Whether the advice is any good.** Every metric here is about behaviour — did it fire, did it
refuse, did it change the outcome. None of them can tell you that a boundary rule is *wrong*, only
that it was followed. That judgement stays yours, and it is the reason nothing here is automated
into a gate.

**Whether a component is better than not having it at all.** Tier 1C gets closest, and it is the
expensive one. Run it on the two or three components you rely on most and accept not knowing for
the rest.
