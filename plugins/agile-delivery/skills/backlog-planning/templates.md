# Templates and checklists

Reference for `backlog-planning`. The templates are the **content** an item needs before it is ready,
not a layout to paste. Where a spec or plan already holds a section, link it instead of copying it.
Leave out a section that does not apply; an empty heading is noise.

## Story

| Part | What goes in it |
| :--- | :--- |
| Title | Short and action-oriented |
| User story | As a *role*, I want *capability*, so that *value* — plus the problem it solves and any background the team does not already have |
| Success measure | How anyone will know it worked, if that is not obvious |
| Scope | In scope and **out of scope**. The second list prevents more arguments than the first |
| Acceptance criteria | Given / When / Then, one behaviour each, numbered so a review can point at one |
| Non-functional criteria | Only those that apply — performance (a number, e.g. p95 latency), security and privacy (access, audit, retention), reliability (retries, idempotency), accessibility, compliance |
| Dependencies | Other teams, systems, APIs, data — each linked, each with an owner |
| Constraints and risks | Technical, legal, timeline. Every risk paired with its mitigation |
| UX | The flow or design link, the exact copy (labels, messages, emails), and edge cases with their expected behaviour |

```
As a support agent, I want to resend an invoice email, so that a customer who lost it does not
need a new invoice.

In scope: resend from the invoice page. Out of scope: bulk resend, changing the recipient.

1. Given a sent invoice, when I click "Resend", then the same PDF is emailed to the original address.
2. Given a draft invoice, when I open it, then "Resend" is not shown.
3. Given a resend, when it completes, then the invoice history records who resent it and when.

Depends on: the mail service's attachment support (owner: platform team, linked).
```

## Technical task

| Part | What goes in it |
| :--- | :--- |
| Intro | One line: what changes and why |
| Components in scope | The modules, services or files it touches |
| Changes required | Per component, what changes |
| Acceptance criteria | Checkable statements — including "code reviewed and approved" and whatever proves nothing regressed |

## Epic

A business goal, epic-level acceptance criteria, links to the design and any requirements document,
known dependencies and risks, a parent initiative, a T-shirt size, a target date — and child items.

## Initiative

The goal, the problem it answers, the outcomes and how they are measured, a link to the requirements
document, a T-shirt size, a priority, a business owner — and child epics.

## Definition of Ready

An item enters a sprint only when **all** of these hold:

- [ ] A clear goal — the user story statement for a story, the one-line intro for a task
- [ ] Acceptance criteria as Given / When / Then
- [ ] Non-functional criteria, where relevant
- [ ] Scope in **and** out
- [ ] Dependencies identified, **linked**, and owned
- [ ] Technical approach agreed
- [ ] Test approach understood — what will be tested, and how
- [ ] Estimated by the team
- [ ] Parent linked, priority set
- [ ] Design and copy linked, if it has a UI
- [ ] Security and compliance reviewed, where it touches them
- [ ] Fits one sprint

If an item cannot be made ready in refinement, do not force it in: clarify, spike or split.

## Definition of Done

Per item:

- [ ] Every acceptance criterion met
- [ ] Automated tests pass in CI; manual tests done where they apply
- [ ] Code reviewed and merged
- [ ] Integrated and deployed to the environment the team calls done
- [ ] Documentation updated where behaviour changed

Before release, additionally:

- [ ] Every child item meets its Definition of Done
- [ ] Release notes written
- [ ] Deployment checklist complete
- [ ] Monitoring and alerting in place
- [ ] A rollback plan exists
- [ ] An operational owner is named

**Shift left.** Developers own unit and integration tests and a green pipeline before an item moves
to test. Testing that begins only when development ends is where sprints spill.
