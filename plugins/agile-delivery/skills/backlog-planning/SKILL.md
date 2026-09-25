---
name: backlog-planning
description: "Use when breaking an initiative or epic into stories and tasks, when deciding whether something is a story, a task, a bug or a defect sub-task, when an item is too big for one sprint or estimated at 13, when estimating in story points or running planning poker, when asked whether an item is ready for a sprint or actually done, or when velocity, completion rate or a burndown looks wrong — a sprint started or closed late, points on sub-tasks, a defect raised against a story that is already closed."
metadata:
  version: "1.0.0"
keywords: [backlog, story-points, estimation, definition-of-ready, definition-of-done, sprint, velocity]
---

# Backlog planning

How work is broken down, sized, admitted to a sprint and counted when the sprint ends. Tool-neutral:
the rules hold in Jira, Linear, Azure Boards or a whiteboard. **The work item is the source of
truth; boards, plans and dashboards are views of it.**

## When not to use this

| Situation | Instead |
| :--- | :--- |
| Wording the ticket itself — its title and how long its body is | `ticket-description` in the change-docs plugin. This skill decides what the items are and whether they are ready; that one decides how few lines say it |
| Writing the specification or the implementation plan | A spec or planning workflow. Planning here is backlog planning, not how the code will be built |
| Finding the cause of a bug once it is filed | Debugging, not planning. This skill only says which kind of item it is |

**Where the planning content lives.** Acceptance criteria, scope and dependencies must exist before
an item enters a sprint — the Definition of Ready checks that. It does not say they are pasted into
the item. If a spec or plan already holds them, the item links it and stays short; if the item is
the only place they will live, they go on the item. One copy, never two.

## 1 — The hierarchy

| Level | What it is | Sized in | Fits |
| :--- | :--- | :--- | :--- |
| Initiative | A strategic outcome, usually spanning teams | T-shirt | Several months |
| Epic | A large deliverable under **one** initiative | T-shirt | Several sprints |
| Story | A user-visible slice — testable, with acceptance criteria | Story points | One sprint |
| Task | Technical or operational work nobody outside the team sees — refactor, config, investigation, environment setup | Story points | One sprint |
| Bug | A standalone item for a defect in **released or already-closed** work — an incident, a monitoring alert, a support report | Story points | One sprint |
| Sub-task | An execution step under a story, task or bug | **Never** | A day or two |
| Defect | A sub-task for a problem found in a parent **still open in the current sprint**. Blocks that parent's Done | **Never** | Inside the parent |

**Every item has a parent**, and every epic has children. An orphan story disappears from every
roadmap and plan view; an empty epic is a promise nobody is working on.

**Bug or defect is decided by the state of the work it breaks, not by severity.** Parent still open
in this sprint: defect sub-task, and the parent cannot close until it is fixed. Parent closed —
released, or done in an earlier sprint: a standalone bug, linked to the original item. A closed item
cannot take new sub-tasks in most trackers, and where it can, the defect is orphaned: nothing on any
board shows it.

## 2 — Splitting

Too big means **13 or more**, or the team doubts it fits one sprint. Split before planning, never
mid-sprint; each piece must still be testable on its own.

| Split by | Example |
| :--- | :--- |
| Workflow step | Create, then edit, then delete — three stories |
| Business rule | Happy path first; edge cases and rare rules in a later story |
| Integration boundary | The API first, the UI that uses it after |
| Uncertainty | A timeboxed spike whose output is an answer, not shippable code. Estimate the real work after it |

Splitting into layers that deliver nothing alone — "backend", "frontend", "tests" as three stories —
is not splitting. It is sub-tasks with points on them.

## 3 — Estimating

**A story point is relative effort, complexity and uncertainty — never hours.** It covers everything
to Done: implementation, review, testing, rework, integration and deployment, documentation.

| Points | Means |
| :--- | :--- |
| 1 | Tiny, low risk, the path is clear |
| 2 | About twice a 1 |
| 3 | Several steps, still clear |
| 5 | Crosses modules, or meaningful integration and testing |
| 8 | Big, with noticeable uncertainty, still fits a sprint |
| 13 | A warning, not an estimate — split it |

`0` is optional, for an item with no real effort.

- **Pick a baseline story** the whole team knows and size everything against it.
- **The whole team estimates**, during refinement and before the sprint is committed. Planning poker:
  everyone votes privately, cards are revealed together, only the highest and lowest explain, then
  re-vote. The person who will do the work does not get to set the number alone, and neither does
  the most senior person in the room.
- **Estimate only the parent** story, task or bug. Sub-tasks carry no points, and their hours are
  never summed into the parent — the parent's points are the team's estimate of the whole.
- **An unrefined item gets no estimate.** If the team cannot agree because nobody knows what it
  involves, the answer is to clarify, add acceptance criteria, run a spike or split — not to average
  the guesses.

## 4 — Ready and done

**Definition of Ready** is the gate into a sprint; **Definition of Done** is the gate out. An item
that fails Ready and enters anyway is the most common reason a sprint spills.

Two checks are easy to half-satisfy. Ready wants dependencies **linked, with owners** — named in a
comment is not enough. Done covers what release needs, not only merged code: monitoring, a rollback
plan, an operational owner.

Both checklists, and story, task, epic and initiative templates, are in
[`templates.md`](templates.md). Read it before judging whether an item is ready.

## 5 — Sprint hygiene

- **Start the sprint on its first day and complete it on its last.** Starting takes the commitment
  snapshot; completing takes the result. A late close lets extra work count as delivered and
  inflates velocity; a late start distorts what was committed. Never edit the start time afterwards.
- **Keep statuses current.** A status that lags the work means the reviewer does not know to review
  and every dashboard is wrong. **On hold always carries a comment saying why.**
- **Only done-category items count at close.** An item in review or in test at the end earns zero,
  however close it is. There is no partial credit and no splitting it after the fact.
- **Map cross-team dependencies before commitment**, in a cross-project plan view, not when one
  team is blocked mid-sprint.
- **Metrics describe the system, never individuals.** A velocity target inflates the estimates.

Ceremonies, the metrics and their formulas, and what a bad reading usually means are in
[`sprints-and-metrics.md`](sprints-and-metrics.md).

## Worked example

> "QA found the export button is missing on the invoice page. The story for that page closed last
> sprint. Add a defect to it, and estimate the new CSV export epic's biggest story — the team said
> 13."

```
1. Not a defect. The story is closed, so a sub-task would be orphaned. File a Bug, link it to
   the closed story, and let the team estimate it like any other item.

2. 13 is a signal to split, not a number to plan with. Proposed split:
   - Export the current filtered view as CSV (happy path)         — estimate after split
   - Cap exports at the row limit and tell the user when it hits  — business rule
   - Scheduled exports delivered by email                         — separate workflow
   If nobody knows how large exports behave, add a timeboxed spike first.
   Estimate the pieces together in refinement, not here.
```

The interesting part is what was **not** done: nobody's 13 became the plan, and "attach it to the
old story" was refused because of where it would end up.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| A story without acceptance criteria enters the sprint | It fails review at the end and spills. Hold it back until it meets Ready |
| An item estimated at 13 or more is committed anyway | Split it; a spilled item earns nothing |
| Points on sub-tasks, or sub-task hours summed into the parent | Points on the parent only |
| A defect sub-task raised on a closed story | A standalone bug, linked |
| Stories created with no parent epic, or epics with no children | Every item has a parent; every epic has children |
| Statuses updated days after the work moved | Move the item when the work moves |
| The sprint closed a day or more late "to get one more thing in" | Close on the last day; the item goes to the next sprint |
| A dependency on another team discovered mid-sprint | Identify and link it before commitment |
| Points used as hours, or inflated to hit a velocity target | Relative sizing against the baseline; velocity is an input to planning, not a goal |
