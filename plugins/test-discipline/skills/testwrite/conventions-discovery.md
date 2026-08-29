# Discovering a repository's test conventions

Reference for `testwrite`. The rule is *copy the nearest sibling test*; this is what to look at when
there is no obvious sibling, and how to tell one runner from another.

## The order to look

1. **The nearest test file** — same directory, then the same package, then the closest ancestor with
   tests. This answers suffix, location, assertion style and fixture style in one read, and it is
   right by construction because it is what the repository does.
2. **The test configuration** — a runner config file at the package or repository root. It states the
   include globs, which *is* the naming convention, written down.
3. **The manifest's test script.** Its value names the runner and often the glob.
4. **The CI workflow.** What it runs is what is expected to pass.

Stop at the first that answers. Only guess when all four are silent, and then say you guessed.

## Telling runners apart

| Signal | Runner |
| :--- | :--- |
| `vitest.config.*`, `vitest` in the manifest, `import { describe, it, expect } from "vitest"` | Vitest |
| `jest.config.*`, `jest` key in the manifest, a global `expect` with no import | Jest |
| A test script that is `node --test`, imports from `node:test` and `node:assert` | Node's built-in runner |
| `pytest.ini`, `[tool.pytest]`, `conftest.py`, `test_*.py` | pytest |
| `#[test]` attributes, `cargo test` | Rust's built-in |
| `_test.go`, `func TestX(t *testing.T)` | Go's built-in |
| `spec/` with `_spec.rb`, `.rspec` | RSpec |
| `phpunit.xml`, `tests/` with `*Test.php` | PHPUnit |

**A dependency in the manifest is not proof the runner is used**, and neither is a config file left
behind by a migration. The test script's value and an actual test file agree with each other; trust
those two over the dependency list.

**Watch for two runners in one repository.** A backend on one and a frontend on another is common,
and it is exactly the case where a test written from habit lands in the wrong half. Resolve per
package, not once for the repository.

## Where files go

There is no universal answer, and repositories are frequently inconsistent with themselves. The
patterns you will actually meet:

- **Colocated** — `orders.ts` and `orders.test.ts` in the same directory.
- **Mirrored** — `src/orders.ts` and `tests/orders.test.ts`, the tree duplicated.
- **A sibling directory** — `__tests__/` beside the source.
- **Both**, in different packages of the same repository, usually for historical reasons.

Suffixes vary the same way: `.test.*`, `.spec.*`, `_test.*`, `Test.*`, and project-specific forms
that encode a tier — a unit suffix and an integration suffix, where the integration one is gated by
an environment variable and does not run by default.

**If you find a tier suffix, respect it.** Writing a test that needs a database and giving it the
unit suffix makes the default suite fail for everyone who has no database, and the failure will be
blamed on the change rather than on the file name.

## Fakes: copy the local style

How a repository fakes its boundaries is the part most likely to be inconsistent between one package
and the next, and the part where introducing a second pattern does the most damage — the next reader
has to learn both to change either.

Look at how the nearest sibling test fakes the same boundary: the database client, the HTTP layer,
the queue, the clock. Match it exactly, even if you prefer another way. **If the sibling's approach
genuinely cannot express what this test needs, that is worth one line in the report** — it is a
finding about the test setup, not a licence to start a third pattern.

## When the package has no tests at all

Write the first one, and say so prominently. Three things are being decided at once, and all three
are decisions a human should see once rather than discover later:

- where test files go in this package
- which runner it uses, and whether the manifest needs a script it does not have
- whether the package's dependencies allow a test to run at all

If a test cannot be made to run without adding a dependency or a script, **stop and report that**.
Adding test infrastructure is its own change, with its own review — and it is out of scope for a
skill whose remit is one change's worth of tests.
