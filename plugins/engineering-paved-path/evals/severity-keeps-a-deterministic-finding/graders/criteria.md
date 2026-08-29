Introduced in 1.1.0, with the `severity-scale` skill. The case is a collision at one anchor
between a deterministic finding and a model-produced one.

The response passes only if **all** of the following hold.

1. **The failing typecheck is graded `critical` and is not downgraded.** Its evidence is a
   command's exit code; nothing in the scale permits lowering it, and the fact that the reviewer
   could not reproduce a caller is irrelevant to it.
2. **The reviewer's finding is treated as model-produced and demoted**, because the second pass
   could not confirm the trigger. Uncertain counts as refuted for the purpose of blocking.
3. **Both are kept.** The model-produced one is recorded beside the deterministic one, not
   merged into it and not deleted.
4. **The answer says the typecheck failure is what blocks the merge**, and gives the reason as
   what it stops rather than as how bad it sounds.

A response that grades both `critical` because they describe the same line is a **fail**: it has
lost the distinction the scale exists for.
