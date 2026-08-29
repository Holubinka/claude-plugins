# Cost baseline

What an SDD run costs, measured rather than estimated, so that a change to the prompts can be
shown to have made it cheaper — or shown not to have.

**Status: the protocol below is fixed; no run has been recorded yet.** The table is empty on
purpose. An invented saving is worse than no baseline, because it is quoted later.

## What blocks the first measurement

`claude plugin eval` is in early access. On an account without it the command exits without
running anything, so the eval-set half of the protocol cannot execute here yet. The
scenario half can run today — it needs no harness, only a real dispatch and the transcripts
it leaves.

## The rule that makes a comparison mean anything

**Change one thing.** Not the model and the routing together, not the prompts and the eval set
together. A run that differs in two ways answers no question, and the answer it appears to give
is the one you were hoping for.

Everything below is held fixed between the baseline and the comparison: the model, the eval
set, the scenario, the repository the scenario runs against, and the plugin versions of
everything except the one under test.

## What to record

One row per run, at least three runs per configuration — a median of three is the smallest
thing that is not an anecdote.

| Field | Where it comes from |
| :--- | :--- |
| Plugin and version | `plugin.json` |
| Commit SHA | `git rev-parse --short HEAD` — the tree the run saw, not the branch name |
| Model | the dispatch, per agent; agents declare their own tier in frontmatter |
| Input / output / cache-read tokens | `sdd-engineering:workflow-retro`'s `stats.sh`, which reads the `usage` block Claude Code writes on every assistant message. Billed figures, not estimates |
| API calls, tool calls | `stats.sh` — `agents[].turns` and `agents[].scout_calls` |
| Latency | wall clock, and `agents[].first_ts`/`last_ts` for what actually overlapped |
| Pass rate | `claude plugin eval --json`, once available |
| Critical failures | listed individually, never summarised into a rate |

**`reread_ratio` is the number to watch.** A multi-agent run's bill is re-reading context, not
producing output: one measured run produced 386 k output tokens against 477 M cache-read. An
optimisation that cuts output and leaves re-reading alone has changed nothing that matters.

## The scenario

Fixed, and written down so a later run is the same run:

1. A single feature request of one paragraph, with no design attached.
2. `spec-creator` → a human approves → `implementation-planner` → a human approves →
   `/sdd-engineering:run-plan`.
3. Single-agent execution, against a repository with a test command and no boundary gate.
4. Stop after stage 4. The fix rounds are excluded from the baseline: what they cost depends on
   what the reviews happen to find, which is not a property of the prompts.

## Baseline

| Date | Plugin | Version | SHA | Model | Input | Output | Cache read | Turns | Median latency | Pass rate | Critical |
| :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| — | — | — | — | — | — | — | — | — | — | — | — |

## The change under test

**Remove instructions duplicated between an agent prompt and a skill, and leave the detail in
the skill reference that loads on demand.**

This is the right first candidate for one reason: an agent prompt is paid on every dispatch,
whether or not the passage is used, while a skill body is paid only when the skill fires and a
reference file only when the agent opens it. Duplication there is the one cost that is charged
unconditionally.

Known duplication to work from, found while writing these plugins:

- `run-plan` §11 restates the model tier and `effort` for agents whose frontmatter already
  declares both. The frontmatter is the source of truth; the skill should keep only what
  frontmatter cannot express.
- `implementer` and `implementation-planner` both carry a skills routing table, and both repeat
  what the skills themselves say about when to load.
- Every agent restates the same clarification-block format. It is short, but it is in six files.

**Do not touch the model tiers in the same experiment.** They are a cost decision already made
on different grounds — `implementer` and `plan-verifier` stay on `opus` because their failures
are silent — and moving them would make the prompt change unmeasurable.

## The gate the optimisation must pass

All three, or the change does not ship:

1. The eval set is still green — the same cases pass.
2. No new critical false negative. A cheaper run that stops catching a missing acceptance
   criterion is not cheaper, it is broken.
3. Cost or latency actually fell, by more than the spread between the three baseline runs.

**If the difference is inside the noise, record that.** A null result is a result, and it is
the one most often quietly replaced with a favourable number.

## Comparison

| Date | Change | SHA | Input | Output | Cache read | Δ cost | Δ latency | Pass rate | Verdict |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| — | — | — | — | — | — | — | — | — | — |
