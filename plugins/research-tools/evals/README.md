# Behaviour evals

Four cases, in two pairs. Each pair is one positive case and the negative case that catches the
failure the positive one invites.

| Case | The boundary it tests |
| :--- | :--- |
| `researcher-reports-its-cost` | The report closes with `## Cost` carrying three real counts, and nothing else about the report changed |
| `researcher-does-not-pad-the-cost` | A one-file question stays a one-file question — the count is not inflated, and the answer is not cut short to keep it low |
| `investigator-returns-a-trace-not-a-dump` | The fixed trace shape, every hop cited to a `path:line`, and at most four quoted lines in total |
| `investigator-declines-a-research-question` | A question needing history, rationale or the network is handed to `researcher`, not answered badly |

The first pair exists because the second failure is the one a metric invites. **A number a report
has to print is a number something will eventually be tempted to make look good**, in either
direction, and only a case that fixes the expected size of the answer can catch it.

The second pair is about the boundary between the two agents, which is the whole reason for having
two. `investigator` is cheap only when it is the one that gets dispatched, and it stops being cheap
the moment it starts answering questions it should have handed on. A suite testing only that it
traces well would pass an agent that traces well and never declines anything.

## Running them

```sh
claude plugin eval ./plugins/research-tools --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without
running anything. These cases were authored against the documented `prompt.md` +
`graders/*.md` shape and have not been executed here.
