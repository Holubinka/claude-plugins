Introduced in 1.2.0. The agent exists to be cheap; a trace that arrives as a file dump is the
failure that removes its reason to exist.

The response passes only if **all** of the following hold.

1. **The fixed shape is present** — `Answer:`, `Trace:`, `Edges:`, `Caveats:` — spelled exactly that
   way. They are what a caller keys on.
2. **Every hop on `Trace:` carries a `path:line`** and a clause saying what that line establishes.
   A hop citing a file with no line is a fail.
3. **No file is dumped.** At most four lines of code are quoted in total, and only where the exact
   text is the answer. Pasting a function body, or a block longer than four lines, is a fail.
4. **The answer is actually structural** — it names the chain, not a description of what the
   catalogue is for.
5. **Absence is reported as absence.** If it looked for an architecture map and found none, it says
   so rather than omitting the step.

A trace that is shorter than expected but correct is a **pass**. Length is not the measure; the
citations are.
