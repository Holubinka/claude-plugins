`evals/fixtures/drifted-set` carries one instance of each failure the audit exists to catch. The
script is deterministic, so this case is really about whether its output is relayed and understood
rather than paraphrased.

The response passes only if **all** of the following hold.

1. **All three `FAIL`s are reported**: the conditionless fan-out table (`A2`), the description naming
   `security-scanner` which exists nowhere (`A1`), and the unresolvable `drifted-set:nonexistent-skill`
   (`A4`).
2. **The `A3` warning is distinguished from the failures**, and it is not presented as something that
   breaks the run. Warnings never fail the audit.
3. **`A2` is explained correctly** — the table lists lanes with no column saying when each one runs,
   which leaves the user picking from the roster by hand.
4. **Nothing is invented.** A finding not in the script's output is a fail, however plausible.

Fixing the fixture is a **fail** — it is a fixture, and the case asks what is wrong with it, not for
it to be repaired.
