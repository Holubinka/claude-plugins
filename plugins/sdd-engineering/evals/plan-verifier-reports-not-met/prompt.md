Use the `plan-verifier` agent to check the current change against `plans/01-order-total.md`.

The plan asks for two things: `createOrder` returns `{ row, total }`, and an empty state is
handled. Only the first was implemented — `src/orders.js` still returns `row` alone for the
empty case.
