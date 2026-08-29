# Verifying a model-produced critical

Reference for `severity-scale`. The scale is in `SKILL.md`; this is the procedure that lets a
model-produced `critical` block something.

## Why a critical needs a second pass at all

A reviewer that reads code produces findings that are usually right and occasionally confident
about something that cannot happen — a guard it did not see, a caller that cannot reach the
branch, a type that already excludes the input it described. Both look identical in the report:
a `path:line`, an invariant, a plausible sentence.

The asymmetry is what forces the pass. A missed defect costs one incident. A hallucinated
blocker costs every future run its credibility, because the first time a gate refuses a correct
change on a finding nobody can reproduce, the gate starts getting bypassed — and then it protects
nothing.

## The procedure

**One finding per pass.** The verifier receives a single finding and nothing else: no table, no
sibling findings, no running total. It cannot be influenced by how many other things were found,
and it cannot trade one against another.

The brief it needs is self-contained:

- the anchor `path:line`, **with the line itself pasted** — a path sends it to look, a path plus
  its line is a fact it can cite
- the invariant, quoted in the reviewer's own words rather than summarised
- the concrete input the reviewer said triggers it
- the base ref the diff was taken against

**Its job is to refute, not to confirm.** It opens the cited line, traces reachability from a
real entry point, checks the preconditions the reviewer assumed, looks for the guard the reviewer
may have missed, and checks whether the condition predates the change.

**It reads. It does not run.** No `Bash`, deliberately. A verifier that can run the suite becomes
a process that reads and writes files in a window where something else may be editing them, and
the concurrency argument that makes parallel review safe stops holding. A `critical` it cannot
refute by reading is a `critical` that survives.

## Three outcomes

| Outcome | Effect on the finding |
| :--- | :--- |
| **Refuted** — the invariant does not hold, or the path is unreachable, or a guard already covers it | Dropped from the findings, recorded under *attempted and refuted* so the work stays visible |
| **Uncertain** — it read the code and could not establish either way | **Treated as refuted.** See below |
| **Stands** | Keeps `critical` if the trigger was reproduced by reading; demoted to `major` if the invariant holds but the concrete input could not be confirmed |
| **Not examined** — the file does not exist, cannot be read, or the anchor does not resolve | **Not a verdict at all.** The finding keeps the severity it arrived with, marked unverified |

**The last row is the one most easily lost, and losing it is expensive.** "Uncertain" and "could not
look" produce the same feeling and opposite facts: the first is a check that ran and did not settle,
the second is a check that never ran. Collapse them and a finding gets dropped *for lack of access
rather than for lack of merit* — and it happens precisely on the findings whose evidence is hardest
to reach, which are not a random sample.

It is the same distinction a diagnostic needs between "found nothing" and "scanned nothing". A
verification that did not happen is not a verification that failed, and a caller reading a report
cannot tell the difference unless it is written down.

**Where an anchor cannot be resolved, the honest move is not to dispatch a verifier at all.** A
verifier handed an unreadable anchor can only return not-examined, so the dispatch buys nothing and
risks laundering "nobody looked" into "investigated and dismissed".

**Uncertain-after-reading counts as refuted, and this is the load-bearing rule.** Verification exists to raise
the bar for blocking, so ambiguity has to resolve toward *not blocking*. The alternative — an
uncertain verdict leaving the `critical` in place — makes the pass decorative: it can only ever
agree, and a check that cannot say no is not a check.

This is safe precisely because it is scoped to blocking. A refuted finding is not deleted. It is
recorded, with the verifier's reasoning, where a human can disagree with it.

## What refuting is not

- **Not a style disagreement.** "I would not have written it that way" refutes nothing.
- **Not an appeal to convention.** "The rest of the repository does this too" makes it
  pre-existing, which changes the anchor, not the invariant.
- **Not a claim that it is unlikely.** Reachable but rare is still reachable. Reachability is a
  question about the call graph, not about traffic.
- **Not a promise.** "This is handled upstream" refutes it only with the upstream line pasted.

## Recording the outcome

Every verified finding carries what happened to it. A report where surviving criticals and
unverified ones look alike has thrown away the pass it just paid for:

```
C1  critical  survived verification   src/orders/total.ts:88
C4  major     stands, trigger not reproduced   src/api/import.ts:34
C7  —         refuted (uncertain)     src/auth/session.ts:12 — see: attempted and refuted
```

And say how many you verified. A run that raised four criticals and verified three has a hole in
it, and the count is the only place that shows.
