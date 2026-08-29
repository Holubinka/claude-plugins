---
name: testwrite
description: "Writes tests for code that was just added or changed, in the framework and file layout this repository already uses. Use when a function, endpoint, component or migration has landed with no test beside it, when behaviour changed and the existing assertions still encode the old contract, or when asked to cover something before a commit. Consult it before writing a test file by hand: naming, location and runner are per-package conventions, so a test written from habit often cannot run at all."
metadata:
  version: "1.0.0"
keywords: [tests, writing-tests, coverage, conventions]
---

# testwrite — tests for what this change did

Not a coverage campaign. **One change's worth of tests**, in the shape this repository already
writes them.

## When not to use this

| Situation | Instead |
| :--- | :--- |
| Tests exist and are failing | `test-discipline:testfix` |
| You want coverage for code this branch did not touch | Neither. That is a separate, deliberate piece of work with its own review |
| The gate that is red is typecheck, lint or format | Not a test problem. Fix the gate |

## 1 — Scope it from the diff

```sh
git diff --name-only <base>...HEAD    # the branch
git diff --name-only HEAD             # uncommitted
```

Resolve `<base>` from the repository, not from habit — the default branch it was cut from.

Skip: generated directories, build output, vendored code, lockfiles, and one-shot migration scripts
that run once against a real database and are gated by an environment variable. **Do not skip a
package because you assume it has no tests.** Check.

## 2 — Decide per changed file

| The change | The action |
| :--- | :--- |
| A new function, endpoint, component or template | A new test file |
| Behaviour changed in an existing unit | Update the matching test, and add a case for the new branch |
| Type-only, formatting-only, comment-only | Skip, and say you skipped it |
| A schema, contract or interface definition with no logic | No direct test. Check that the tests of its dependents still cover the new fields |
| **A bug fix** | A regression test that **fails before the fix** — see below |

## 3 — Discover the convention; do not derive it

**Open the nearest existing test to the file you changed, and copy its suffix, its location and its
style.** That is the whole rule, and it beats any table this skill could carry.

What "nearest" means: same directory first, then the same package, then the closest ancestor that
has tests. What to copy: the filename suffix, whether tests sit beside the source or mirror it under
a test directory, the assertion library, how a fixture is built, and how a boundary is faked.

If the package has no tests at all, look at the sibling package that does, and say in your report
that you are setting a precedent — that is a decision a human should see once, not discover later.

The runner comes from the repository, via `engineering-paved-path:project-commands`: the task's own
instruction, then a convention file, then CI, then the manifest's scripts, with the runner prefix
from the lockfile. Do not assume a framework because it is the popular one. A test written for the
wrong runner fails in a way that looks nothing like the real problem, and the time goes into the
wrong file.

[`conventions-discovery.md`](conventions-discovery.md) carries what to look at, in what order, and
the signals that distinguish one runner from another.

## 4 — Write them

- **One group per public unit; one test per behaviour branch** — the happy path, then each error and
  edge case that the change actually introduced.
- **Mock the external boundary only** — the network, the database driver, the queue, the clock, the
  filesystem. **Never mock the unit under test**, and never assert on which internal method was
  called in which order: that test breaks on every refactor and survives every real bug. A suite
  proving only that the mocks agree with each other is worse than no suite, because it reports green.
- **Use the exact symbol name from the source** in the group name, so searching by symbol finds the
  test.
- **No flakiness by construction**: no sleep-based waits, no real network, no real database, no
  dependence on wall-clock time or on test ordering.
- **No byte snapshots of generated output** — a CSV, a spreadsheet, a PDF, an image. Parse it and
  assert on the structure. A byte snapshot breaks on an unrelated library upgrade and tells you
  nothing about what changed.

## 5 — A bug fix gets a test that fails first

Write the regression test, **run it, watch it fail**, then apply or confirm the fix and watch it
pass. A regression test that has never been red proves only that it compiles.

Report both observations. "Added a regression test" and "added a regression test, confirmed red at
`<message>` before the fix" are different claims, and only the second one is evidence.

## 6 — Run the new tests first, then the package suite

The new file on its own, then everything around it. A new test that passes alone and breaks two
others has found something, and running the suite is how you learn that in this turn rather than in
CI.

On failure, follow `test-discipline:testfix`. Never `.skip`, never `.only`, never loosen an assertion
to make red go away.

## Report

```
Added:    <files>
Updated:  <files>
Skipped:  <files> — <why: type-only, generated, out of scope>
Runner:   <command>  (discovered from: <source>)
Result:   <pass/fail per package, with counts>
Precedent set: <anything this repository had not done before, or "none">
```

**A change spanning several packages gets tests in each affected package.** Do not consolidate them
into one file in one package: the next person to change one of those packages will not find it.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Deriving the file path and suffix from a rule | Conventions vary per package. Copy the nearest sibling test |
| Assuming the popular framework is the one installed | Discover it. A wrong-runner failure looks like a code problem |
| Mocking the function under test | Mock only boundaries, or the test asserts on the mock |
| Asserting that a mock was called, and nothing else | Assert on the observable result. Call-order assertions break on refactors and survive bugs |
| Backfilling coverage while you are in the file | Out of scope. One change's worth of tests |
| A regression test that was never red | Run it before the fix, or it proves nothing |
| Snapshotting a generated buffer | Parse and assert on the structure |
