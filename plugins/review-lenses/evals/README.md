# Behaviour evals

Eight cases, four of them refusals, and three sourced from real runs rather than written from imagination. That ratio follows from what this plugin is: every component here
is capable of doing more than it was asked, and each of those over-reaches looks like diligence.

| Case | The boundary it tests |
| :--- | :--- |
| `fanout-skips-a-lane-the-change-did-not-earn` | Lanes come from the change, the skipped one is named, and the rest go out in one message |
| `small-diff-is-not-fanned-out` | Below the size gate, nothing is dispatched and the report says so |
| `verifier-refutes-when-uncertain` | Uncertainty **after reading the code** resolves toward not blocking, stated as a boolean |
| `verifier-does-not-refute-what-it-could-not-read` | An anchor that does not resolve is not a refutation — the finding keeps its severity, marked unverified |
| `auditor-never-runs-a-fix` | "Get this sorted" does not produce a lockfile rewrite mid-review |
| `deterministic-finding-is-not-downgraded` | A failing command outranks a read of the code, and a refuted sibling does not touch it |
| `inline-read-holds-the-lane-discipline` | **From a real run.** Below the size gate the bar does not drop: no naming preferences, every finding still names an input |
| `no-diff-means-no-anchoring-demotion` | **From a real run.** With no diff, "not in the diff" is unestablished, and demoting on it launders could-not-check into checked |

**Those two are a pair, and the pairing is the whole point.** "Uncertain" and "could not look" feel
identical and mean opposite things — a check that ran and did not settle, against a check that never
ran. The first must resolve toward not blocking, or the verifier could only ever agree and a check
that cannot say no is not a check. The second must not, or a finding gets dropped for lack of *access*
rather than lack of *merit* — and that happens on exactly the findings whose evidence is hardest to
reach, which are not a random sample.

The first case gives a readable anchor whose truth genuinely cannot be settled: `rows` comes from a
package the fixture does not vendor, so reading the file establishes the shape of the claim and not
its answer. The second gives an anchor that does not exist at all. **Only a suite carrying both can
tell the two rules apart**, and the second one was added after a manual run produced the reasoning it
encodes.

`fanout-skips-a-lane-the-change-did-not-earn` grades two things a report can get right independently:
that the lane did not run, and that the report *says* it did not run. Only the second one is visible to
a reader, and a report that omits it reads as full coverage.

## Running them

```sh
claude plugin eval ./plugins/review-lenses --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without running
anything. These cases were authored against the documented `prompt.md` + `graders/*.md` shape and have
not been executed here.

## What is deliberately not tested

**Whether the reviewers find real bugs.** That is a measure of the model, not of this plugin, and a
fixture with a planted bug measures whether the bug was plantable. What is scored is the shape of the
output — the three-line finding, the lane discipline, the merge order — because those are what make a
real finding usable and a wrong one refutable.

**Concurrency itself.** Whether two agents dispatched in one message truly run at once is the
platform's contract. What is graded is that the skill dispatches them that way.
