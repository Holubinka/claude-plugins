# Changelog

All notable changes to `test-discipline`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `test-discipline--v<version>`.

## [1.0.0] — 2026-08-29

First release. Two skills and an agent, generalised from a private monorepo's `.claude/` set.

### Changed from the source workflow

- **The runner table is gone, and discovery replaced it.** The originals carried a per-package table
  of test runners, file suffixes and flags for one company's repository. That table was the most
  useful part of them there and the least portable part of them anywhere else.

  What replaced it is an order to look in — the nearest existing test, then the runner config, then
  the manifest's test script, then CI — plus the signals that distinguish one runner from another.
  The rule it comes down to is **open the nearest sibling test and copy it**, which is right by
  construction because it is what the repository already does.

- **"There is no Jest in this repository" became a discovery step.** A repository-specific fact
  stated as a rule is exactly the shape that does not survive extraction.

- **The run command comes from `engineering-paved-path:project-commands`**, not from a hardcoded
  package-manager invocation. Where no runner can be discovered, no tests are written and nothing is
  installed — a test file that cannot run is worse than no test file, because it looks like coverage
  in a diff.

### Removed from the source workflow

- Every example anchored to one company's packages, services and report types.
- The assertions specific to one document-generation library and one ORM's mocking style. What
  survived is the general form: mock the boundary, never the unit, and never assert on the mock.

### Added

- **A regression test must be observed red before the fix.** The original said to write one; it did
  not say to watch it fail. `test-writer` now records what it saw, and where the fix was already in
  the tree it says so in those words rather than implying an observation it did not make.

- **The write-scope-as-concurrency argument, stated in the agent.** `test-writer` writes test paths
  only, and the reason is that it may be running beside a reviewer reading the source diff — an
  overlap that would make every sibling's reads describe its edit rather than the branch. A test that
  needs a source change is therefore a finding it reports, never a task it takes on.

- **An uncovered behaviour is a row in the coverage table with `no` and a reason.** A coverage table
  with no `no` rows on a change that has any is the shape a reader trusts most and the shape that is
  easiest to produce dishonestly.
