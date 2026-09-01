# test-discipline

Tests for the change in front of you, in the framework this repository already uses. Two skills and one agent, holding a single rule: **when a test and the code disagree, decide which of them is wrong before touching either.**

```sh
/plugin install test-discipline@dev-workbench
```

Installing this pulls in `engineering-paved-path`, for the rule that finds your test command instead of guessing it.

## The decision the whole plugin is built around

A failing test is information, and the only way to lose it is to make the red go away without finding out what it meant.

| What happened | What to fix |
| :--- | :--- |
| The behaviour is broken | **The source.** The test is doing its job |
| The assertion encoded the old behaviour, and the new behaviour is intended | **The test.** Update it, and say the contract changed |
| You are not sure which | **Neither, yet.** Read the function end to end first |

The third row is the one that earns its place. Guessing there is how a real bug gets "fixed" by loosening an assertion — and **a loosened assertion is indistinguishable from a correct fix** in the diff, in CI, and in the commit message. The only difference is that the defect ships.

## What is in it

| Component | Answers | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `testwrite` (skill) | This change has no tests. What do I write, and where does it go? | 124 | 1 482 |
| `testfix` (skill) | The suite is red. Which side is wrong? | 99 | 1 031 |
| `test-writer` (agent) | Write them for me, and tell me what is still uncovered | 91 | 1 277 |

## It discovers your conventions; it does not carry a table of them

**Open the nearest existing test and copy its suffix, its location, its assertion style and the way it fakes a boundary.** That is the rule, and it beats anything this plugin could assert about your repository.

The version of this skill it was extracted from carried a table of runners and file suffixes for one company's monorepo. That table was the most useful part of it there and the least portable part of it anywhere else, so it is gone. What replaced it is an order to look in — the nearest test, then the runner config, then the manifest's test script, then CI — and the signals that tell one runner from another.

Two consequences worth knowing:

- **Two runners in one repository is expected**, not an anomaly. A backend on one and a frontend on another is the common case, and it is exactly where a test written from habit lands in the wrong half. Both skills resolve per package, never once for the repository.
- **If no runner can be discovered, no tests get written.** Nothing is installed and nothing is invented. A test file that cannot run is worse than no test file, because it looks like coverage in a diff.

The run command comes from `engineering-paved-path:project-commands`, which reads the task, then your convention files, then CI, then the manifest — and takes the runner prefix from the lockfile.

## A bug fix gets a test that fails first

Write the regression test, **run it, watch it fail**, then confirm the fix and watch it pass. A regression test that has never been red proves only that it compiles.

Where the fix is already in the tree and red cannot be observed without editing source, the agent says exactly that — `regression test added; not observed red — the fix was already in the tree` — rather than implying an observation it did not make.

## The agent's write scope, and why it is narrow

`test-writer` writes test files. Not source, not configuration, not the manifest, not CI.

That is not tidiness. **It is what makes the agent safe to run in parallel with a reviewer reading the source diff** — its write set and that reviewer's read set do not overlap. The moment it edits a source file, every sibling agent reading files or running a gate is measuring that edit rather than the branch, and none of them can detect it from the inside.

So a test that cannot be written without a source change is **a finding it reports**, naming the file, what is untestable about it, and what shape of change would fix that. Never a task it takes on. The same goes for test infrastructure: a missing setup file, a runner config that needs changing, a dependency that is not installed — each is its own change with its own review.

## What it will not do

| Not this | Why |
| :--- | :--- |
| `.skip` or `.only` a failing test | A skipped test is a silent regression with a comment on it |
| Loosen an assertion to make red go away | That converts a caught defect into a shipped one |
| Touch a test unrelated to the change | Pre-existing failures are reported and left, so the branch is not blamed for them |
| Assert that a mock was called | That test breaks on every refactor and survives every real bug. Assert on the observable result |
| Mock the unit under test | Then the suite proves only that the mocks agree with each other |
| Snapshot a generated buffer — CSV, spreadsheet, PDF | It breaks on an unrelated upgrade and tells you nothing about what changed |
| Backfill coverage for untouched code | One change's worth of tests. Gap coverage is separate work with its own review |
| Commit, push, or open a pull request | Ending a run with a commit nobody asked for makes it irreversible before it has been read |

## One scheduling constraint

**`test-writer` must run alone.** Proving a test can fail means holding a deliberate defect in the working tree between mutating a file and reverting it — so anything reading files or running a gate in that window measures the mutation rather than the branch. This is the same constraint `architecture-review`'s reviewer states from the other side, and it is why no review orchestrator in this marketplace dispatches a test writer as one lane of a parallel fan-out.

Read-only reviewers are safe beside each other. A writer is not safe beside anything.

## Evals

Four behaviour cases under `evals/`, two of them refusals. See [evals/README.md](evals/README.md), including the note that `claude plugin eval` is currently early access.

## Dependencies

```
test-discipline@1.0.0
└── engineering-paved-path@^1.1.0     project-commands, for the runner
```

`^1.1.0` and not `^1.0.0`: `project-commands` arrived in 1.1.0, and it is the only thing standing between this plugin and a hardcoded `npm test`.

## Compatibility

Claude Code >= 2.1.110 — the floor for version-constrained plugin dependencies.
