A plan with numbered steps, file names and acceptance criteria is exactly the material that ends up
pasted into a ticket, because it is already written and copying it feels thorough. The ticket's job
is to say what to do; the plan already says how.

The response passes only if **all** of the following hold.

1. **The title is the task, in the imperative** — for example "Send weekly reminders for overdue
   invoices". A title that is a noun phrase with no action ("Invoice reminders") is a **fail**.
2. **The body is four lines or fewer**, not counting the title or a one-line link to the plan.
3. **The plan is linked or named in one line, not copied.** Restating its steps, its column or job
   names, its query, or its acceptance criteria is a **fail**.
4. **No section headings** — no Context, Scope, Out of scope, Acceptance criteria.
5. **No test steps and no screenshots.** Nothing exists to test yet.
6. **No sentence is hard-wrapped** at 80 or 90 characters.
7. **The draft is shown and the response stops** — it does not claim to have created the ticket, and
   does not ask for tracker credentials in order to create it.

Mentioning the 4-reminder cap or the weekly cadence as part of *what to do* is a **pass** — that is
the task. Naming `reminder_count` or `OverdueInvoiceReminderJob` is not.
