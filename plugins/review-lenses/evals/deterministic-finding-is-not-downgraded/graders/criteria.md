A collision at one anchor between a deterministic finding and a model-produced one that did not
survive verification.

The response passes only if **all** of the following hold.

1. **The typecheck failure keeps `critical` and is what blocks the merge.** Its evidence is a command's
   exit code; the merge may not downgrade it, and the verifier's verdict has no bearing on it.
2. **The verifier's verdict is applied only to the model-produced finding**, which drops out of the
   blocking set into `## Attempted and refuted`.
3. **The two are not merged into one row.** They share an anchor; a deterministic finding and a model
   one are kept beside each other, not folded together.
4. **The refuted finding is not deleted.** It appears with the verifier's reasoning.
5. **Nothing suggests re-verifying the typecheck failure.** It does not go through the verifier at all.

A response that treats the uncertain verdict as grounds for keeping the critical is a **fail** — that
inverts the rule the verification step is built on.
