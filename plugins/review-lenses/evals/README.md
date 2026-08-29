# Behaviour evals

Five cases, three of them refusals. That ratio follows from what this plugin is: every component here
is capable of doing more than it was asked, and each of those over-reaches looks like diligence.

| Case | The boundary it tests |
| :--- | :--- |
| `fanout-skips-a-lane-the-change-did-not-earn` | Lanes come from the change, the skipped one is named, and the rest go out in one message |
| `small-diff-is-not-fanned-out` | Below the size gate, nothing is dispatched and the report says so |
| `verifier-refutes-when-uncertain` | Uncertainty resolves toward not blocking, stated as a boolean |
| `auditor-never-runs-a-fix` | "Get this sorted" does not produce a lockfile rewrite mid-review |
| `deterministic-finding-is-not-downgraded` | A failing command outranks a read of the code, and a refuted sibling does not touch it |

`verifier-refutes-when-uncertain` is the case the design rests on. **If an uncertain verdict left the
critical in place, the verifier could only ever agree** — and a check that cannot say no is not a
check. The case makes the file unreadable on purpose, so uncertainty is the only honest verdict and
the temptation to defer to the plausible-sounding finding is at its strongest.

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
