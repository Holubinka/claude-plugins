# agile-delivery

Delivery planning for a team that works in sprints: how work breaks down, what a story point measures, what ready and done mean, and which habits keep the numbers honest. Tool-neutral — it holds in Jira, Linear, Azure Boards or on a whiteboard.

```sh
/plugin install agile-delivery@dev-workbench
```

## What is in it

| Component | For | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `backlog-planning` (skill) | Breaking work down, sizing it, admitting it to a sprint and counting it at the end | ~125 | ~2.1k |

Figures are estimates. Two reference files load only when the skill reads them: `templates.md` (~1k — story, task, epic and initiative content, the Ready and Done checklists) and `sprints-and-metrics.md` (~0.7k — ceremonies, what counts at sprint close, eight metrics and how to read each).

## `backlog-planning` — the parts that are easy to get wrong

**Bug or defect is decided by the state of the parent and the release, not by severity.** A problem in work still open in this sprint, or one that blocks the release, is a defect sub-task that blocks the parent's Done. A problem in closed or released work that holds nothing back is a standalone bug in the backlog, linked back when the broken item is known. A sub-task hung on a closed story is on no board and in no sprint, and nothing reports it missing.

**13 is not an estimate.** It is the point at which an item gets split — by workflow step, by business rule, by integration boundary, or with a timeboxed spike — and splitting into "backend", "frontend" and "tests" is not one of the options.

**Points go on the parent only.** Sub-tasks carry none, and their hours are never summed into the parent's estimate. The whole team estimates, in refinement, before commitment; an item nobody can size is not ready, and the fix is refinement rather than an average.

**A sprint's numbers are only as good as its first and last day.** The commitment is snapshotted when the sprint starts and the result when it completes, so a late start or a late close quietly changes both. Only done-category items count; an item in test at the close earns zero.

**Metrics describe the system, never individuals.** Completion rate falling below its usual band means over-commitment or items entering without meeting Ready, not a team working badly.

## Beside `ticket-description`

The `change-docs` plugin's `ticket-description` keeps a ticket body to two to four lines and links the plan rather than restating it. This skill does not contradict that: it decides **what the items are and whether they are ready**, and the Definition of Ready requires acceptance criteria to *exist and be reachable*, not to be pasted into the ticket. Where a spec or plan holds them, link it; where the tracker item is their only home, they go on the item. One copy, never two.

The two are independent. Neither plugin depends on the other.

## What it will not do

| Not this | Why |
| :--- | :--- |
| Set an estimate on the team's behalf | Points are a team judgement; one person's number, or a model's, is what the ceremony exists to replace |
| Convert points to hours or days | The scale is relative on purpose; a conversion makes it a worse unit of time |
| Create or edit items in a tracker | It decides what the items should be; the tracker work is yours |
| Rate a person by velocity or completion rate | The metric starts measuring the gaming instead of the work |

## Evals

Two behaviour cases under `evals/`, both refusals. See [evals/README.md](evals/README.md), including the note that `claude plugin eval` is currently early access.

## Compatibility

No dependencies, no scripts, no hooks. Any Claude Code version that loads plugin skills.
