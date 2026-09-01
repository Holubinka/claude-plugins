---
name: testfix
description: "Makes a red test suite green by fixing whatever is actually wrong. Use when a test run just failed, when assertions broke after a change, when a suite that passed yesterday is failing today, or when tempted to skip, loosen or delete a failing test. Its whole content is the call that decides whether a real bug gets fixed or quietly loosened away: whether the source is wrong or the assertion is."
metadata:
  version: "1.0.0"
keywords: [tests, failing-tests, debugging, regression]
---

# testfix — fix the cause, never the symptom

A red suite is information. The only way to lose it is to make the red go away without finding out
what it meant.

## The decision this skill exists for

For every failure, one of three things is true. Deciding which is the entire job:

| What happened | What to fix |
| :--- | :--- |
| The behaviour is broken | **The source.** The test is doing its job |
| The assertion encoded the old behaviour, and the new behaviour is intended | **The test.** Update it to the new contract, and say in your report that the contract changed |
| You are not sure which | **Neither, yet.** Read the function end to end first |

The third row is the one that matters. **Guessing here is how a real bug gets "fixed" by loosening
an assertion** — and the result looks identical to a correct fix in the diff, in CI, and in the
commit message. The only difference is that the defect ships.

A useful tie-break: ask what the test was *for*. If you can state the contract it was protecting and
that contract has genuinely changed, the test is out of date. If you cannot state it, you do not yet
know enough to change either side.

## Never

- **Never `.skip` or `.only`.** A skipped test is a silent regression with a comment on it. Fix it,
  or report it unresolved and leave it red.
- **Never loosen an assertion to make red go away.** Widening a type, accepting `undefined`,
  comparing loosely, deleting the awkward case — each converts a caught defect into a shipped one.
- **Never delete a failing test** unless the behaviour it asserts has been deliberately removed, and
  say so explicitly when you do.
- **Never touch a test unrelated to the change.** Tests that were already red before your change are
  out of scope: report them, leave them, and say they were pre-existing.
- **Never re-run hoping for green.** A test that passes on the second run is a flaky test, which is a
  finding in its own right, not a pass.
- **Never report a result you did not just observe.** The rules for what a claim needs are
  `engineering-paved-path:verification-before-completion`; the one that bites here is that a check
  which could not run is neither a pass nor a failure.

## The loop

1. **Run the suite** for the target. Get the command from
   `engineering-paved-path:project-commands` rather than typing one from habit — a wrong runner
   produces a failure that has nothing to do with the code.
2. **Read the first failure completely** before acting. Not the summary line: the assertion, the
   values, and the stack.
3. **Decide the cause** by the table above, and fix that.
4. **Re-run.** Repeat until green, or until you have a failure you have decided not to fix — in which
   case stop and report it, rather than continuing to change things around it.

**Fix one failure at a time when they are related.** Ten failures with one cause become zero after
one fix, and a batch of edits made against ten symptoms usually contains several that were never
needed.

## When the suite is red before you start

Establish that first, and separate the two sets. Run the suite on the base commit, or read what CI
last said about it. A branch blamed for failures it did not cause is a long detour, and it is very
easy to arrive at by assuming a red suite is yours.

Report them apart:

```
Pre-existing failures (on <base>): <n> — <names>
Failures introduced by this change: <n>
```

## Report

```
Changed:  <files>
Cause:    <source | assertion> — <one line saying why that side was wrong>
Result:   ✓ <n> passing | ✗ <n> failing — <first failure>
Unfixed:  <anything left red, and why>
```

The `Cause:` line is not decoration. It is the one field that lets a reviewer see whether the fix
went in the right direction, and it is the field that is uncomfortable to write when it went in the
wrong one.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Editing the test because it is the smaller diff | Decide by which side is wrong, not by which is easier to change |
| `.skip` on a stubborn failure | A skipped test is a silent regression. Fix it or report it unresolved |
| Fixing unrelated tests that were already red | Out of scope. Report them, leave them |
| Changing the assertion to match observed output | That is not a fix. It is a recording of the bug |
| Treating a second-run pass as a pass | Flakiness is a finding. Say so |
