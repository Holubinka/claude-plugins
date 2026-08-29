Introduced in 1.1.0. Every report closes with what the answer cost.

The response passes only if **all** of the following hold.

1. **A `## Cost` section is present**, spelled exactly that way, as the last section of the
   report.
2. **It carries three counts** — files opened, searches run, pages fetched — and they are
   counts of work actually done in this turn, not round numbers or estimates.
3. **Nothing else about the report changed.** The findings are still separated from the
   evidence, every claim is still addressed to a `path:line` or a URL, and
   `## What I could not establish` is still present.
4. **The question is still answered.** A report that reports its cost and not the answer has
   failed at the only thing it was dispatched for.
