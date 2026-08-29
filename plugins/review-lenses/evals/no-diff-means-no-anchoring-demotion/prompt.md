Merge these two findings with `/review-lenses:review-diff`'s rules and tell me the resulting
severities.

- `C1` critical, model-produced, `src/api/orders.ts:41` — dereferences a possibly-undefined value.
- `C2` major, model-produced, `src/api/orders.ts:88` — an unbounded read of the orders table.

There is no diff available in this environment and no base to compare against.
