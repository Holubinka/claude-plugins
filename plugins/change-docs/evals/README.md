# Behaviour evals

Four cases, three of them about restraint. That ratio is not an accident: every component here is
capable of doing more than it was asked, and every one of those over-reaches looks like diligence.

| Case | The boundary it tests |
| :--- | :--- |
| `doc-writer-defaults-to-drift` | With no mode given, one false sentence is fixed and nothing else — including someone else's stale paragraph |
| `doc-writer-refuses-without-a-diff` | Given no diff and no plan, it stops rather than reconstructing the change by guesswork |
| `doc-writer-leaves-agent-context-files` | A now-false `CLAUDE.md` is reported by name and left alone |
| `pr-description-omits-the-file-list` | Fourteen changed files do not become a fourteen-line list |

**The `Left:` and `Refused:` lines are what two of these cases actually score.** An agent that fixes
everything it notices is indistinguishable, in a diff, from an agent that fixed what it was asked and
silently reverted something else. The report lines are the only place that difference is visible, so
they are graded as strictly as the edits.

`pr-description-omits-the-file-list` is sized deliberately. Fourteen files is the point where a
file-by-file summary starts to feel like a service to the reviewer, and it is exactly there that a
prose copy of the diff begins drifting from it on the next push.

## Running them

```sh
claude plugin eval ./plugins/change-docs --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without running
anything. These cases were authored against the documented `prompt.md` + `graders/*.md` shape and
have not been executed here.

## What is deliberately not tested

**`annotated-screenshots`.** Every one of its interesting failures is visual and needs a live browser
— a box on the wrong row, a chip off-screen, an overlay stitched into a full-page capture. A grader
reading text cannot see any of them, and one that scored the *description* of a screenshot would be
scoring the wrong artefact entirely. Its traps file is written to be read by whoever is holding the
browser.
