Create the ticket for this work. The plan is committed at `docs/plans/invoice-reminders.md`, and
this is what it says:

```markdown
# Plan: overdue invoice reminders

## Goal
Customers with an invoice more than 7 days overdue get one reminder email per week, until the
invoice is paid or 4 reminders have been sent.

## Steps
1. Add `reminder_count` and `last_reminded_at` columns to `invoices` (migration, default 0 / null).
2. New job `OverdueInvoiceReminderJob` in `src/jobs/`, scheduled daily at 09:00 UTC.
3. Query: status = 'unpaid', due_date < now() - 7 days, reminder_count < 4,
   last_reminded_at is null or older than 7 days.
4. Send through the existing `Mailer` with a new `invoice-overdue` template.
5. Increment `reminder_count` and set `last_reminded_at` in the same transaction as the enqueue.
6. Feature flag `invoice_reminders`, off by default.

## Acceptance criteria
- WHEN an invoice is 8 days overdue and has never been reminded, THE system SHALL send one email.
- WHEN an invoice has 4 reminders, THE system SHALL send no further email.
- WHEN the invoice is paid, THE system SHALL stop reminding.

## Out of scope
SMS reminders, per-customer reminder settings.
```
