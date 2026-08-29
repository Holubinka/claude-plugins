A negative case. The SDD workflow is expensive and must stay out of the way of ordinary work.

The response passes only if **all** of the following hold.

1. **No SDD agent is dispatched.** Not `spec-creator`, not `implementation-planner`, not
   `implementer`, not `plan-verifier`.
2. **`run-plan` does not fire.** A one-line CSS problem is explicitly the case its own
   instructions tell it to refuse: "Do not run this to make a one-file change, a rename, or a
   fix."
3. **No specification and no plan is written.** Nothing appears under any `specs/` or `plans/`
   directory.
4. **The actual question is engaged with** — the response looks at the CSS problem, or asks
   what it needs to. Refusing to help because no plan exists is as wrong as over-engineering.

Loading an architecture or frontend skill is acceptable if the response goes on to use it.
Fail the response if any SDD agent is dispatched, or if the answer is a proposal to write a
spec first.
