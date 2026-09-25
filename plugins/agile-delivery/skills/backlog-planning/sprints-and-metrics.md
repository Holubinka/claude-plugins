# Sprints and metrics

Reference for `backlog-planning`.

## Cadence

Two-week sprints are the common default. Some organisations group sprints into multi-sprint planning
blocks; the work for a block is then made ready, estimated and scope-locked **during the block
before it**, so the first sprint does not open with refinement.

## Ceremonies

| Ceremony | When | What it is for | What it is not |
| :--- | :--- | :--- | :--- |
| Planning | Day one | A sprint goal, and refined items chosen by capacity and recent velocity | Refinement. An item that is not ready stays out |
| Daily | Every day, 15 minutes | Coordination and blockers | A status report to a manager |
| Refinement | Once or twice mid-sprint | Splitting, clarifying and estimating upcoming work, together | Solo estimation by whoever wrote the item |
| Review | Last day | Showing the working increment to stakeholders | Hiding what did not finish |
| Retrospective | After review | One or two actionable improvements, followed up next sprint | Blame |

**Do not overcommit to look ambitious.** A plan the team hits every sprint is worth more than one it
misses by a third.

## What counts at sprint close

- Parent items only — stories, tasks, bugs. Sub-task points never count; a defect counts through
  its parent.
- Only items in a **done-category** status. Anything in development, review or test earns zero.
- The commitment is whatever was in the sprint when it started; the result is whatever was done when
  it completed. Both depend on doing those two things on the right day.

## Metrics

| Metric | What it is | How to read it |
| :--- | :--- | :--- |
| Velocity | Points completed per sprint, parent items only | A **trend over several sprints**, used to size the next plan. One sprint is noise. Not comparable between teams |
| Completion rate | Points completed ÷ points committed | Roughly 70–90% is healthy. A sustained drop means over-commitment or items entering without meeting Ready — a system problem, not a team failing |
| Throughput | Items completed per sprint or per week | Useful where items are similar in size, and for teams on continuous flow |
| Burndown | Remaining work across the sprint | A flat line then a cliff means statuses are updated late, or items are too big |
| Burnup | Completed work against total scope | Shows scope added mid-sprint, which a burndown hides |
| Lead time | From request to delivered | What the requester actually experiences |
| Defect leakage | Defects found in a later phase ÷ (earlier + later) × 100 | Rising means testing is catching less before release |
| DoD compliance | Share of closed items that met every Done criterion | Items closed without it are debt counted as delivery |

**Metrics describe the system, never individuals.** The moment a number is used to rate a person,
it is optimised instead of the work — points inflate, items are closed early, bugs are filed as
tasks.
