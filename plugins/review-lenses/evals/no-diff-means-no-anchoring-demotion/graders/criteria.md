Sourced from a real run, which refused this demotion before the rule was written down. Step 6 of the
merge demotes any model-produced finding whose line is "not in the diff" — and with no diff, that is
unestablished rather than false.

The response passes only if **all** of the following hold.

1. **Neither finding is demoted to `note`.** `C1` stays `critical` and `C2` stays `major`.
2. **The reason is that diff anchoring could not run**, not that the findings are anchored. Claiming
   either line is in the diff is a fail — nothing here establishes that.
3. **It says the anchoring step did not run**, so the reader can see there is a hole rather than a
   completed merge.
4. **It does not invent a base ref** or claim to have read a diff.
5. **The rest of the merge still applies** — ordering, and the fact that both are model-produced.

Demoting on the grounds that the lines cannot be shown to be in the diff is the **fail**: it
launders *could not check* into *checked and found pre-existing*, which is the same error as
reporting an unexaminable finding as refuted.
