# refactor-safely

Cleaning code up without changing what it does — by **pinning the current behaviour in tests before any structure moves.**

```sh
/plugin install refactor-safely@dev-workbench
```

Installing this pulls in `engineering-paved-path` and `test-discipline`.

## What is in it

| Component | For | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `refactor-triage` (skill) | Which of these changes may I actually apply? | 104 | 1 331 |
| `refactor-planner` (agent) | What has to be pinned before this starts? | 67 | 861 |
| `refactor-implementer` (agent) | Pin it, then restructure under green tests | 69 | 925 |

The skill is useful alone. The two agents are a chain: plan, then execute.

## Three tiers, decided before anything is touched

| Tier | Test | Examples |
| :--- | :--- | :--- |
| **Apply directly** | No caller can observe the difference | Genuinely unreachable code, a local rename, a redundant cast the type already guarantees |
| **Apply after reading the callers** | Safe *given what the callers do* — so you have read them all | Renaming an export, narrowing a return type, extracting a helper used twice |
| **Propose only** | It changes behaviour, even for the better | An N+1 fix, a missing `await`, a clearer error message, a tightened validation |

**The changes that look most obviously safe are the ones that quietly leave the definition of a refactor.** The standing example is the one people apply by reflex: **fixing an N+1 by batching changes the order results come back in.** Some caller depends on that order, and neither of you knows which one. So it gets a marker comment and a line in the report, not an edit.

## Stop after five applied changes

A hard limit, and not caution — **reviewability**. A refactor of thirty small changes cannot be reviewed as a refactor: the reviewer either trusts it entirely or re-derives all thirty, and an unrelated behaviour change hides comfortably in the noise between them.

**"While I'm here" is the smell.** Every additional change was individually reasonable; the aggregate is unreviewable.

## The question the planner exists to answer

For every behaviour in scope: **if this silently changed, would any existing test go red?**

If no, it needs a characterisation test before any structure moves. The plan's coverage column takes a test path or the word **nothing** — "probably covered by the integration tests" is not an answer, and if you did not open the test and see the assertion, it is nothing.

Two rules keep the plan honest:

**Pin the observable, not the implementation.** "Returns rows sorted by date descending" is a behaviour. "Calls `sortRows` before returning" is an implementation detail — and pinning that means the characterisation test fails on exactly the refactor that was the point.

**The frozen surface is a list of names**, not the phrase "the public API". Whatever is on it may not move. If the cleanup requires moving one, **that is a feature with a compatibility story, not a refactor** — the planner says so and stops, rather than planning a deprecation shim nobody asked for.

## A red characterisation test is a finding

Phase 1 writes tests for what the code does *now*, and gets them green. Nothing structural moves until they are.

**A characterisation test that fails before any refactoring has started is telling you the behaviour is not what the plan thought.** The implementer stops and reports it. It is a finding, not a test to fix — and it is the most valuable thing that phase can produce, because it means someone's model of the code was wrong before anyone touched it.

Once restructuring begins, **red means revert that change** — never "fix the test". Loosening an assertion converts a caught regression into a shipped one, and afterwards it is indistinguishable from a correct fix.

## An unverified refactor says so, prominently

If Phase 1 produced no characterisation tests — because the module has none and none could be written without changing source — **the report says that at the top, not in a footnote.**

A refactor with nothing pinning it is unverified. It may still be the right thing to hand back. What it must not do is read like a verified one, because the whole reason to do this in two phases is to be able to tell the difference.

## `refactor-implementer` must run alone

It writes to the working tree, and Phase 1 deliberately runs tests against a tree it is editing. Anything reading files or running a gate beside it measures that edit rather than the branch, and cannot detect it from the inside.

Nothing in this marketplace dispatches it as one lane of a parallel fan-out. A boundary review afterwards is the right shape; a boundary review beside it is not.

## What it will not do

| Not this | Why |
| :--- | :--- |
| Restructure before the tests are green | That is the entire technique. Without it this is just editing |
| Fix a bug it found | That is a behaviour change. It reports it and someone decides |
| Mix a refactor with a behaviour change in one commit | The behaviour change goes first, alone, where it can be reviewed as one |
| Move a public surface "compatibly" | A deprecation shim is a feature with its own review |
| Loosen a test to get past red | That is the regression the test just caught |
| Apply more than five changes | The sixth is a second pass |
| Invent a verify command | It comes from `engineering-paved-path:project-commands`. If none is discovered, the refactor is reported unverified |
| Commit, push, or open a pull request | Ending a refactor with a commit nobody asked for makes it irreversible before it has been read |

## Evals

Four behaviour cases under `evals/`, three of them refusals. See [evals/README.md](evals/README.md), including the note that `claude plugin eval` is currently early access.

## Dependencies

```
refactor-safely@1.0.0
├── engineering-paved-path@^1.1.0     project-commands, for the verify command
└── test-discipline@^1.0.0            testwrite, for the characterisation tests
    └── engineering-paved-path@^1.1.0
```

The `test-discipline` edge is the interesting one. `refactor-implementer` writes characterisation tests, and the rule it needs — *behaviour broken, fix the source; assertion encoded the old behaviour, fix the test; unsure, read the function first* — is bit for bit what `testfix` already says. **Restating it inline is the duplication this marketplace exists to avoid**, so it invokes the skill instead.

## Compatibility

Claude Code >= 2.1.110 — the floor for version-constrained plugin dependencies. **`git`**, and a test runner it can discover.
