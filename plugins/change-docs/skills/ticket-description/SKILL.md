---
name: ticket-description
description: "Writes a ticket — an issue, task or story in Jira, Linear, GitHub Issues or any other tracker — and the update that goes on it once the pull request is open. Use when asked to create, file or raise a ticket or an issue for a piece of work, to break a plan into tickets, or when a PR has just been opened and its ticket needs test steps and screenshots for whoever checks the change."
metadata:
  version: "1.0.0"
keywords: [ticket, issue, tracker, test-steps, screenshots]
---

# Ticket description

A ticket says **what to do**. The plan says how. Whoever picks the ticket up, triages it or checks it
later needs the first; the second already has a home, and a copy of it in the ticket goes stale on
the plan's first edit.

A ticket is written in two moments: **short, when it is created**, and **test steps plus screenshots,
once the PR is open**.

## When not to use this

| Situation | Instead |
| :--- | :--- |
| The body of the pull request itself | `change-docs:pr-description` |
| Capturing and annotating the screenshots | `change-docs:annotated-screenshots` — this skill only says when they are taken and where they go |
| Writing the plan or the spec | Not this. The ticket points at the plan; it never becomes one |

## 1 — When the ticket is created

```
Title: Stream the order export instead of buffering it

Exports over roughly 50 000 rows run the worker out of memory and return a 502. Make the export stream rows to the response, and cap it at 100 000 rows.

Plan: docs/plans/order-export-streaming.md
```

- **The title is the task, in the imperative.** Someone scanning a board reads nothing else.
- **The body is two to four lines saying what to do**, and why when the what does not make it obvious.
  That is the whole ticket.
- **The detail lives in the plan.** If the plan is somewhere the ticket's readers can open, link it
  in one line. Never paste it, summarise its steps or restate its acceptance criteria.
- **Do not hard-wrap.** One sentence is one line, however long — trackers render a single newline as
  a visible break, so text wrapped at 80 or 90 characters shows up as ragged half-lines.

| Never at creation | Why |
| :--- | :--- |
| Implementation steps, file names, the chosen approach | That is the plan. Two copies drift, and nobody updates both |
| Background on how the system works | The people reading the ticket work here |
| Section headings for a four-line ticket — Context, Scope, Out of scope, Notes | A filled-in template makes a ticket look thorough and makes it longer than the work |
| Test steps or screenshots | Nothing exists to test yet. They arrive with the PR |

## 2 — Once the PR is open

Add a comment to the ticket, so the short body stays as it was written:

```
PR: <link>

Test steps
1. Sign in as a user with the orders:export permission.
2. Open Orders → Export and pick a date range with more than 100 000 orders.
3. Click Export CSV. Expected: the download starts at once and stops at 100 000 rows.

Screenshots
<attached: 1-export-dialog.png, 2-export-capped.png>
```

Use the tracker's own formatting — Markdown where it renders, the tracker's markup or editor where it
does not. The three parts matter, not the syntax.

**Test steps**

- **Starting state first** — who is signed in, which flag is on, what data has to exist. Steps that
  begin at "click Export" fail for whoever lacks the permission.
- **One action per step.** Put `Expected:` on the step where the result becomes visible; steps with
  no expected result are a walk, not a test.
- **Name controls exactly as the screen labels them**, not as the code names them.
- **Only what this change touches.** Not a regression pass over the whole application.
- **Walk the steps yourself in the running app before posting them.** Steps written from reading the
  code name a menu that is labelled something else and skip the permission nobody remembered.

**Screenshots**

- **Take them while walking the steps**, with `change-docs:annotated-screenshots`, at the step where
  the result is visible. Name the files by step so they read in order.
- **Attach the files to the ticket.** A local path means nothing to someone on another machine. If
  the tools at hand cannot upload, say so and give the absolute paths — never drop them silently.
- **If nothing visible changed, write "No UI change"** under Screenshots. Do not photograph a
  terminal or a JSON response to fill the slot.

## Before it is sent

The write rules are the same as for a PR description, because the failures are the same:

- **Show the draft and stop.** Do not create the ticket or post the comment until whoever asked has
  read it.
- **Send the text from a file**, never through a shell heredoc. Nested quoting has silently produced
  empty bodies.
- **Read it back.** Fetch the ticket or the comment and check that the text and every attachment
  arrived. A successful-looking response is not evidence.
- **When editing an existing ticket, fetch it first** and send back every field you are not changing.
  Many tracker update APIs clear what you omit.
