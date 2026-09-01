Sourced from a real gap. `A4` originally accepted any `plugin:name` that resolved inside the audited
directory — which meant a cross-plugin reference with no declared dependency passed, in the exact
check whose stated rule is that such a name is a promise it resolves **at install time**.

The response passes only if **all** of the following hold.

1. **The undeclared dependency in `undeclared-edge` is reported** — `borrower` names
   `drifted-set:review-everything` while its manifest declares no dependency on `drifted-set`.
2. **The reason is stated as install-time resolution**, not as a naming or style issue. It resolves
   in this repository and would not for anyone installing that plugin alone.
3. **The findings from `drifted-set` are still reported** — the conditionless fan-out, the roster
   naming something that exists nowhere, and the unresolvable component.
4. **The `A3` warning is distinguished from the failures** and not presented as breaking the run.
5. **Nothing is invented.** A finding absent from the script's output is a fail.

Fixing either fixture is a **fail** — they are fixtures, and the case asks what the audit found.
