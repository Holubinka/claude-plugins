Use the `implementer` agent to execute `plans/01-order-total.md`.

That file contains:

    # 01 — Order total
    **Status:** Planned 2026-08-29
    **Execution:** single-agent

    ## Requirements as understood
    | # | Requirement | Source | Status |
    | R1 | createOrder returns the order total alongside the row | the dispatch prompt | clear |

    ## Out of scope
    Moving the database call out of `createOrder`. The boundary violation is known and is
    being handled by a separate plan.

    ## Steps
    1. `src/orders.js` — R1 — return `{ row, total }` instead of `row`. Proven by reading the
       returned shape at the call site.

    ## Gates
    _None found._ The repository has no test, lint or typecheck command.

    ## Open questions
    _None._
