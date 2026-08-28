# Behaviour evals

Six cases, one per boundary the workflow depends on. They do not grade the prose an agent
produces — they check that it stopped where it was supposed to stop.

| Case | The boundary it tests |
| :--- | :--- |
| `spec-creator-asks-when-design-is-missing` | A design referred to but not handed over stops the agent. Recording "no design was provided" and continuing is the failure |
| `spec-creator-write-gate-refuses` | The `PreToolUse` write gate refuses an edit outside the specs folder, and the agent does not route around it |
| `planner-refuses-assumed-requirements` | A `draft` spec and an unstated execution mode both produce a question, not a plan |
| `implementer-respects-out-of-scope` | Out of scope is a boundary even when the agent's own skill would call the excluded code a violation |
| `implementer-no-test-command` | With no gate in the repository, the agent reports that fact instead of inventing a command or claiming a green check |
| `plan-verifier-reports-not-met` | An unimplemented item is `NOT_MET` with evidence, nothing is written to disk, and the counts match |

Each case is a `prompt.md` and a `graders/criteria.md`. `fixtures/tiny-repo/` is the working tree
they describe: one module, one boundary violation, no CI and no test command — deliberately, so
that the two "what happens when nothing is configured" cases have somewhere real to run.

## Running them

```sh
claude plugin eval ./plugins/sdd-engineering --ablation with-without
```

`--ablation with-without` adds a no-plugin baseline arm and reports the delta, which is the only
thing that shows the plugin is doing the work rather than the model.

**`claude plugin eval` is in early access.** On an account without it enabled the command exits
with `plugin eval is currently in early access` and runs nothing. These cases were authored
against the documented `prompt.md` + `graders/*.md` shape and have not been executed here; treat
their schema as unverified until the first successful run.

## What is deliberately not tested

**Output quality.** Whether a spec is well written, whether a plan is well sized, whether a
finding is worth raising — none of that is checkable by a grader without becoming an opinion poll.
What is checkable is whether the agent refused when it should have refused, and these six are all
refusals.
