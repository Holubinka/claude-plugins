# Behaviour evals

Two cases, both refusals. Each hands over a request whose easiest answer is the one the skill exists
to stop, because that answer looks cooperative.

| Case | The boundary it tests |
| :--- | :--- |
| `backlog-planning-splits-instead-of-estimating` | An unrefined 13 with votes and sub-task hours attached gets a split, not a number |
| `backlog-planning-files-a-bug-not-a-defect` | A problem in closed, released work becomes a linked bug, not a sub-task on the closed story |

The first case offers three ways to produce a number — average the votes, take the highest, sum the
sub-tasks — and each is a different rule broken. A grader that only checked for "13" would pass a
response that converted two days of backend into points.

## Running them

```sh
claude plugin eval ./plugins/agile-delivery --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without running
anything. These cases were authored against the documented `prompt.md` + `graders/*.md` shape and
have not been executed here.

## What is deliberately not tested

**The metric formulas and the templates.** They are reference material, and a grader checking that a
completion rate was computed correctly would be testing arithmetic, not the skill.
