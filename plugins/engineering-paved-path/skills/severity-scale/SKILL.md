---
name: severity-scale
description: "Grades a review finding as critical, major, minor or note by what each level stops, rather than by how bad it feels. Use when writing up a bug, a boundary violation, a vulnerability or an audit result; when deciding whether something blocks a merge; when two reviewers graded the same problem differently; when a finding lands on a line the branch never touched; or when triaging a list of findings into fix-now and fix-later. Also use when tempted to lower a severity so a loop terminates."
metadata:
  version: "1.0.0"
keywords: [severity, review, findings, triage, verification]
---

# The four-level severity scale

Severity is not a feeling about how bad something is. **It is a claim about what this finding
stops.** Grade by answering that question, and two reviewers converge without negotiating.

| Level | What it stops | Test |
| :--- | :--- | :--- |
| `critical` | The merge | Shipping this causes incorrect behaviour, data loss, or an exploitable path, on inputs the code will actually get |
| `major` | The sign-off, not the branch | Real and worth fixing before this lands, but a competent reviewer could accept the branch with it recorded |
| `minor` | Nothing | Correct as written; worse than it needs to be. Fix while nearby |
| `note` | Nothing, and it is not a request | Something the next reader should know. Carries no obligation |

**The failure this scale prevents is grading by blast radius.** A path traversal in an endpoint
three people use is `critical`. Its blast radius is small; its class is not. Grade the class of
the defect and the reachability of the path, never the importance of the feature.

## Deterministic findings outrank model-produced ones

A finding whose evidence is a **command's exit code** — a failing typecheck, a failing test, a
lockfile advisory, a boundary gate refusing — is deterministic. Anyone can re-run it and get the
same answer.

A finding produced by reading code is model-produced. It may be entirely right, and it is not
reproducible the same way.

Three consequences, and they are the whole reason for the distinction:

1. **Nothing may downgrade a deterministic finding.** Not a reviewer, not a merge step, not a
   triage pass. If it is red, it is red.
2. **A model-produced `critical` must survive verification before it blocks anything.** See
   [`verification.md`](verification.md). Uncertain counts as refuted.
3. **When the two collide at one anchor, the deterministic one wins the severity** and the
   model-produced one is kept beside it, not merged into it.

Record which kind each finding is. A report where the two are indistinguishable cannot be
triaged by anyone who was not there.

## Anchor to the diff

**A model-produced finding on a line the branch did not touch is a `note`**, whatever its
content — it is a pre-existing condition someone chose to mention, not a consequence of this
change. Report it, mark it `pre-existing`, and let the author decide.

The exception needs proof, not an assertion: to grade a pre-existing problem above `note`, show
that the change *reaches* it — a new caller, a new input shape, a widened type. Then the finding
is about the change, and it anchors to the line that made the reach.

Do not resolve this by intuition about what "the branch touched". Check the file three ways: is
it tracked, does it exist, and does it differ from the base. `git diff --quiet` alone exits 0 for
a path that is untracked or absent, so on its own it reports a brand-new file as unchanged.

## Two rules about the report as a whole

**An empty report is a valid result.** A review that finds nothing and says so is information. A
review that manufactures a `minor` to look diligent has spent the reader's attention on nothing
and taught them to skim the next one.

**Lowering a severity so a loop terminates is not convergence.** If a fix round keeps failing on
the same `critical`, the finding is either real and unfixed, or wrong and should be refuted on
its merits. Re-grading it `major` to get past a gate converts a caught defect into a shipped one,
and leaves a record saying the opposite.

## Upstream labels are not this scale

A `high` from an advisory database, an ESLint `error`, a linter's `warning`, a CVSS score — none
of them is a level here. They are *evidence*. Map them deliberately:

- an advisory's severity describes the vulnerability in the abstract; this scale describes what
  it does **in this repository, on this dependency path**. A `high` in a devDependency that
  never ships is not a `critical` here, and saying so is not downgrading it — it is grading it.
- a linter `error` is deterministic and therefore ungradeable-downward, but its *level* is a
  configuration choice someone made, not a judgement about this change.

State the upstream label and this scale's level side by side. Collapsing them loses the one fact
a reader needs to disagree with you.
