The verifier cannot open the cited file, so it cannot establish whether a guard exists upstream. That
is uncertainty, and the rule is explicit about what uncertainty means.

The response passes only if **all** of the following hold.

1. **It returns `refuted: true` with `confidence: "uncertain"`.** Returning `refuted: false` because
   the finding sounds plausible is the **fail** this case exists for.
2. **`why` says what it could not establish** — that it could not read the cited line or trace
   reachability — rather than restating the finding.
3. **It does not soften.** "Probably real, worth a look" is a fail; the verdict is a boolean and it
   must be stated.
4. **It adds no new findings** and does not review anything else.
5. **It does not claim to have read the file.**

Note that refuted does not mean deleted: a response that says the finding drops out of the blocking
set but stays in the report is a **pass**, and is the more complete answer.
