The dispatch does not say which mode. Drift is the default because it is the reversible one, and the
agent has no channel to ask.

The response passes only if **all** of the following hold.

1. **The one false sentence is corrected** — three attempts becomes five, and the fixed 200ms
   interval becomes the backoff. Nothing else in that paragraph is rewritten.
2. **No new page is created.** Authoring a retry document is a **fail**: this change falsified an
   existing sentence, it did not introduce something undescribed.
3. **The queue section is untouched.**
4. **The stale deployment paragraph is reported, not fixed**, under the report's `Left:` line.
   Someone else's drift is a finding — fixing it here buries it inside a change it has nothing to do
   with, and turns a two-line diff into a large one.
5. **The report names the mode as Drift** and says the sentence that was false and what it now says.

A response that also proposes a separate follow-up for the deployment paragraph is a **pass**.
Making that edit is not.
