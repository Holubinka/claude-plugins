# Behaviour evals

Three cases. Two are refusals, and they are the ones that matter — this agent's value is as much in
what it declines to say as in what it finds.

| Case | The boundary it tests |
| :--- | :--- |
| `reviewer-returns-an-empty-table` | A clean target produces an empty findings table and a full checked-and-clean section |
| `reviewer-does-not-file-a-performance-finding` | A loud problem outside the subject is named with its owner and never graded |
| `reviewer-names-no-rule-when-none-exists` | With no architecture rules in the repository, the skill's rules are a proposal, never a finding |

The first two are a pair, and 1.1.0 is why. That release added an adversarial stance — *generate at
least three candidates before concluding a target is clean* — and **every instruction to look harder
invites two failures at once**: filing something you do not believe, and widening the subject until
something turns up. One case fixes a target with nothing to find; the other puts a genuinely
important problem in front of the agent that belongs to somebody else.

The third case is the reason this plugin can be published at all. An agent carrying opinions about
architecture, pointed at a repository that has none, must not report its opinions as that
repository's rules.

## Running them

```sh
claude plugin eval ./plugins/architecture-review --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without running
anything. These cases were authored against the documented `prompt.md` + `graders/*.md` shape and
have not been executed here.

## What is deliberately not tested

**Severity calibration across runs.** The agent's own severity anchors exist because the same
finding once scored `major` on one run and `minor` on the next. A grader that fixed the expected
level would be scoring the anchor's wording, not the behaviour, and would have to be rewritten every
time the anchor is sharpened.
