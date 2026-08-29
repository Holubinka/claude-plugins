# Behaviour evals

Three cases. One is deterministic, one is a judgement about text, and one is a refusal.

| Case | The boundary it tests |
| :--- | :--- |
| `audit-catches-a-conditionless-fanout` | The script's three failures are relayed accurately, the warning is distinguished, and nothing is invented |
| `description-is-rewritten-as-a-trigger` | A procedure-shaped description is identified as such, with the right consequence named |
| `routing-declines-a-pointless-fanout` | A question that presumes a fan-out gets the presumption answered, not the question |

`description-is-rewritten-as-a-trigger` grades one thing tightly on purpose: **naming the
consequence**. "The description is too long" and "a description that reads like a procedure gets
followed instead of the body" both lead to a rewrite, and only the second one generalises. A grader
that accepted either would pass a model that had learned to shorten descriptions and nothing else.

`routing-declines-a-pointless-fanout` is phrased the way the question actually arrives — *which
models should each of them get* — because a presumption embedded in a question is much harder to
decline than one stated outright, and declining it is the behaviour worth having.

## Running them

```sh
claude plugin eval ./plugins/agent-authoring --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without running
anything. These cases were authored against the documented `prompt.md` + `graders/*.md` shape and
have not been executed here.

## What is deliberately not tested

**The audit script's own logic.** It is deterministic and has a fixture with one of each failure in
it; running it is the test, and a model-graded case would only measure whether the output was read.
The eval case above scores the reading.
