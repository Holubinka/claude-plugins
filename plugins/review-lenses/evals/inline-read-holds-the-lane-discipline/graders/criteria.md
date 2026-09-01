Sourced from a real run. On a diff this size the size gate correctly skipped the fan-out — and the
inline read then filed a naming preference as a finding, which the correctness agent forbids in its
own `## Never` list. Nothing had said it about the path that skips the agent, so the discipline
lived only in the branch that was not taken.

The response passes only if **all** of the following hold.

1. **It does not fan out**, and says so. Dispatching an agent on a two-file, 13-line change is a
   fail.
2. **Every finding names a concrete input that breaks it.** A finding without one is a fail on the
   inline path exactly as it would be on the agent path — the reader cannot tell which produced it.
3. **No naming preference is filed as a finding.** Suggesting that `lineSubtotal` is singular while
   summing an array, or any other better-name observation, is a **fail** when it appears in the
   findings. It may appear as an aside clearly marked as not a finding.
4. **No formatting or style observation is filed as a finding.**
5. **A clean read is stated as a result.** If nothing survives the concrete-input test, the answer
   is that the change is clean, not a list of things that could be tidier.

Finding a real defect here is a pass — `money()` accepting a non-integer, or `label()` emitting
unformatted cents, both qualify, because each names an input. The graded failure is the bar dropping
when the fan-out does.
