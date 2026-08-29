# Changelog

All notable changes to `refactor-safely`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `refactor-safely--v<version>`.

## [1.0.0] — 2026-08-29

First release. One skill and two agents, generalised from a private monorepo's `.claude/` set.

### Added

- **`refactor-triage`** — the three tiers, decided before anything is touched, and the category table
  that says which tier each kind of cleanup usually falls in.

  The tier that earns the skill is the third one. **The changes that look most obviously safe are the
  ones that quietly leave the definition of a refactor** — and the standing example is the one applied
  by reflex: fixing an N+1 by batching changes the order results come back in, and some caller depends
  on that order.

  The five-change limit is about reviewability, not caution. A refactor of thirty small changes cannot
  be reviewed as a refactor; the reviewer either trusts all thirty or re-derives all thirty.

- **`refactor-planner`** — answers one question per behaviour: *if this silently changed, would any
  existing test go red?* If no, it needs a characterisation test. The coverage column takes a test path
  or the word **nothing**, because "probably covered by the integration tests" is how an unpinned
  behaviour gets refactored.

- **`refactor-implementer`** — pin, restructure, report, in that order. A characterisation test that
  fails *before* any refactoring has started is a finding rather than a test to fix: it means someone's
  model of the code was wrong before anyone touched it, which is the most valuable thing the phase can
  produce.

  Where Phase 1 produced no tests at all, the report says so prominently. An unverified refactor may
  still be the right thing to hand back; what it must not do is read like a verified one.

### Changed from the source workflow

- **`test-discipline` is a dependency rather than a copy.** The original restated the fix-direction
  rule inline. It is bit for bit what `testfix` says, and this marketplace has one place for that.

- **The verify command is discovered**, through `engineering-paved-path:project-commands`, instead of
  being a hardcoded package-manager script. Where none can be discovered, the refactor is reported
  unverified rather than reported green.

- **The plan is written where the caller says**, not to a fixed run-directory path. Where no path is
  named, the planner hands the plan back and writes nothing — inventing a location is how a plan ends
  up somewhere the next stage does not look.

### Removed from the source workflow

- Every rule naming one repository's conventions — its logger, its lint plugin, its import extensions,
  its shared-library layout.
- The example log paths containing a real ticket identifier.
