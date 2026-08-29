# Changelog

All notable changes to `review-lenses`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `review-lenses--v<version>`.

## [1.0.0] — 2026-08-29

First release. One skill and three agents, generalised from a private monorepo's `.claude/` set.

### Added

- **`review-diff`** — the conditional fan-out. Every lane declares the condition under which it runs,
  and a lane whose condition is not met does not run. **A roster with no conditions is a roster the
  user has to select from by hand**, which is the thing the fan-out was supposed to do for them.

  The report names the skipped lanes and why. A report that omits them reads as full coverage, which
  is the one way this skill can mislead someone who trusts it.

- **`correctness-reviewer`** — the lens nothing else in a review owns. Its discipline is the
  three-line finding: the expression at `path:line`, the invariant it violates, and **a concrete input
  that breaks it**. If you cannot name the input, you have not found a bug; you have found something
  you do not like.

- **`finding-verifier`** — one finding in, a refutation attempt out, and **uncertain counts as
  refuted**. Two measured failures make it worth its cost, and they pull opposite ways: a reviewer
  given only the four severity names once graded a real path traversal `minor`, and separately,
  plausible findings that were simply wrong cost whole turns to chase. The second is the one that kills
  a gate — the first unreproducible refusal is when people start bypassing it.

  No `Bash`, deliberately. A critical it cannot refute by reading is a critical that survives, and a
  verifier that could run a suite would be reading files in a window the orchestrator may be writing
  in.

- **`dependency-auditor`** — five checks, and its own rule that a new dependency duplicating one the
  repository already has is a `major` finding with no advisory involved. It never runs a fix: an
  automatic upgrade from inside a review rewrites the lockfile, so every later lane describes a tree
  nobody chose.

### Notes

- **The inline read holds the same lane discipline as the correctness lane**, stated explicitly in the
  skill. Found by running the skill against a two-file, thirteen-line tidy-up: the size gate worked and
  no agents were dispatched, but the inline read then filed a naming preference as a finding — which
  the correctness agent forbids in its own `## Never` list and which nothing had said about the path
  that skips it. A reader cannot tell which path produced a finding, so the bar cannot differ.

### Changed from the source workflow

- **The findings file is gone, and nothing is written during a review.** In the original, reviewers
  appended to a JSON file because a shell hook enforced write scopes and a hook can only read a file.
  Without that hook the file has no remaining job — and three lanes appending to one file are three
  tree mutators, which breaks the very property that makes parallel review safe.

  Lane-prefixed ids (`C1…`, `A1…`, `D1…`) replaced it. Three concurrent returns merge without a shared
  counter, therefore without shared state, therefore without a file.

- **The merge is specified rather than assumed.** Arrival order is a function of which agent finished
  first, so the original's implicit ordering made two reports of the same diff incomparable. The order
  is now anchors normalised, collisions within ±2 lines, agreeing invariants folded at the highest
  severity, disagreeing ones kept as a flagged pair, then a deterministic sort.

- **The severity scale is a dependency, not a copy.** All three agents grade through
  `engineering-paved-path:severity-scale`. Six components across this marketplace use it, and copying
  it into each is the duplication that plugin exists to prevent.

- **The security lane became an obligation on the correctness lane.** A fourth context reading the same
  diff, for a subject that is a checklist rather than an open question, is a lane that reports nothing
  on most runs — and a lane that reports nothing on most runs stops being read on the run where it
  matters.

### Removed from the source workflow

- The size gate's package-manager-specific audit and typecheck commands, replaced by discovery through
  `engineering-paved-path:project-commands`.
- Every example naming a real service, package or vendor.
- The stage-marker protocol and the write-scope hook the original depended on. What replaced them is
  tool grants plus phase ordering: lane agents ship without `Write` and `Edit`, and the orchestrator's
  write set is non-empty only after every lane has returned.
