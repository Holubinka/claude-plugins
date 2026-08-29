---
name: review-diff
description: "Reviews a change through only the lenses that change earned, instead of running a fixed set of reviewers over everything. Use before a commit or a pull request, when asked to look a branch over, or when a review is wanted but not every kind of review. It sizes the diff first, skips the lanes the change does not need, runs the rest at once, and puts every blocking finding through an adversary before it blocks anything."
metadata:
  version: "1.0.0"
keywords: [review, fan-out, findings, verification, diff]
---

# review-diff

A fixed roster of reviewers costs the same on a two-line change as on a two-thousand-line one, and
produces a report nobody reads. **Pick the lanes from the change.**

## Step 1 — size it

```sh
git diff --stat <base>...HEAD
```

**Two files or fewer and thirty changed lines or fewer, with no lockfile and no schema in it: do not
fan out at all.** Read it yourself, report what you find, and say that is what you did. A stage a
change does not need makes that change worse, not safer — it costs a context load and returns a
report the reader has to skim to discover it says nothing.

**The inline read is a lane, not a free-form opinion.** It holds exactly the discipline the
correctness lane holds, because the reader cannot tell which path produced a finding:

- **Every finding names a concrete input that breaks it.** If you cannot, it is not a finding.
- **No naming preferences, no formatting, no style.** A better name for a symbol is not a
  correctness finding, and filing one here is how a small change acquires a long report.
- **A clean read is the result**, stated as one. Six findings on a twelve-line tidy-up usually means
  the bar dropped when the fan-out did.

Escalate out of that regardless of size when the diff touches authentication, authorization,
cryptography, money, or the handling of personal data. Those are cheap to review and expensive to get
wrong.

## Step 2 — pick the lanes

Each lane has a condition. **A lane whose condition is not met does not run**, and the report says it
was skipped and why — a reader has to be able to tell "clean" from "not looked at".

| Lane | Dispatch | Runs when |
| :--- | :--- | :--- |
| correctness | `review-lenses:correctness-reviewer` | any diff touching executable code |
| boundaries | `architecture-review:architecture-reviewer` | a file crosses a directory the repository treats as a boundary, an import edge changes, or a composition root, route or adapter is touched |
| dependencies | `review-lenses:dependency-auditor` | a lockfile or a manifest dependency block is in the diff. Never otherwise |

The correctness lane carries a security obligation rather than a separate agent: it invokes
`engineering-paved-path:security` itself when the diff touches auth, input parsing, uploads, secrets,
or a new outbound call with a caller-supplied destination.

**Never more than three lanes in flight.** And note what is *not* a lane: a test writer. It proves a
test can fail by holding a deliberate defect in the tree between mutating a file and reverting it, so
anything reading files in that window measures the mutation rather than the branch. **Readers are safe
beside each other; a writer is safe beside nothing.**

## Step 3 — dispatch them in one message

**All the lanes in a single message, or they run in series** and the fan-out was imagined. Two lanes is
the minimum for this to matter; one lane is a direct dispatch, not a fan-out.

Each brief carries:

- the diff base, spelled out
- **its slice**, and **what the other lanes own** — overlap is the largest waste in a fan-out and it is
  only fixable here, because parallel contexts cannot see each other
- the report shape below

## Step 4 — merge

Every lane returns a `## Findings` table with lane-prefixed ids — `C1…`, `A1…`, `D1…`. **The prefixes
are what let three concurrent returns merge without a shared counter, and therefore without a shared
file.** Nothing is written to disk during a review; see `merging.md` for why that is load-bearing and
for the exact merge order.

## Step 5 — verify every model-produced critical

Collect the rows that are `critical` **and** model-produced. Dispatch one
`review-lenses:finding-verifier` per row, **all in one message**, each with a self-contained brief:

- the anchor `path:line` **with the line itself pasted** — a path sends the agent to look, a path plus
  its line is a fact it can cite
- the invariant, quoted in the lane's own words rather than summarised
- the concrete input the lane said triggers it
- the diff base

It gets one finding and nothing else. That is what makes a file unnecessary, and it is also what keeps
it honest: it cannot trade one finding against another.

| Verdict | Effect |
| :--- | :--- |
| refuted, **or uncertain** | drops out of the blocking set, into `## Attempted and refuted` with the reasoning |
| stands, trigger not reproduced | demoted to `major` |
| stands, trigger reproduced by reading | stays `critical`, marked *survived verification* |

**A deterministic finding — one whose evidence is a command's exit code — skips this step entirely and
may not be downgraded.**

## Step 6 — you are the only writer

Reviewers propose; **you apply.** Nothing else touches the tree, and nothing touches it until every
lane has returned. That ordering is not politeness — it is what makes the parallel reads valid, since
a lane reading a file you are mid-edit describes your edit rather than the branch.

Triage before fixing. Fix `critical` first, then `major`. **Do not fix a finding you do not believe**:
say so and leave it in the report. An implementer told to fix a hallucinated blocker produces exactly
the unrequested change a reviewer would then object to.

## Report

```
## Findings
<the merged table, ordered — see merging.md>

## Attempted and refuted
<criticals that did not survive verification, with the verifier's reasoning>

## Lanes
<each lane: ran / skipped, and the condition that decided it>

## Not covered
<what nobody looked at, or "nothing">
```

**The `## Lanes` section is not optional.** A report that does not say which lanes were skipped reads
as full coverage, and that is the one way this skill can mislead someone who trusts it.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Running every lane on every change | Each lane has a condition. A dependency audit on a diff with no lockfile finds nothing, slowly |
| Dispatching lanes in separate messages | They run in series. One message, or there is no fan-out |
| Letting a model-produced critical block without verification | The first unreproducible refusal is when people start bypassing the gate |
| Treating an uncertain verdict as "keep the critical" | Then the verifier can only ever agree, and a check that cannot say no is not a check |
| Fanning out over a two-file change | Three context loads for one small answer |
| Letting the bar drop when the fan-out does | The inline read holds the same lane discipline. A naming preference is not a finding on either path |
| Omitting the skipped lanes from the report | It reads as full coverage |
