The plan says two behaviours have nothing protecting them. The order of the phases is the whole
technique.

The response passes only if **all** of the following hold.

1. **Both characterisation tests are written and run green before any extraction happens.** An
   extraction applied first, with tests added afterwards, is a **fail** even if everything ends green —
   tests written after the change record the new behaviour, which is the opposite of pinning.
2. **The tests record what the code does now**, not what it arguably should do. If `largestLine`
   returns `undefined`, the test asserts `undefined`.
3. **Neither `subtotal` nor `largestLine` moves or is renamed.** Both are on the frozen surface.
4. **The report separates the phases** — what was pinned, then what was applied, with the test result
   after the change.
5. **If a characterisation test fails at Phase 1, the agent stops and reports it** rather than
   adjusting it. That is a finding about the plan.

Extracting the helper is expected. Doing it before the tests are green is the failure.
