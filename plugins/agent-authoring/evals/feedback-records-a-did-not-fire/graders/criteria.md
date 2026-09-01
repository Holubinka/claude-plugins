The failure nobody reports spontaneously, phrased the way it actually arrives: as an aside, after the
fact, with the user explicitly saying nothing broke.

The response passes only if **all** of the following hold.

1. **The verdict recorded is `did-not-fire`**, not `misfired` and not `worked`. Nothing behaved
   wrongly; something failed to behave at all.
2. **An entry is written to the log** via `feedback.sh record`, not merely described in chat.
3. **The entry names the component that was expected** and the request that should have loaded it.
4. **It does not treat "nothing broke" as a reason to skip recording.** Dismissing this as not worth
   logging is the **fail** — it is the expensive failure and the one that never gets reported.
5. **Nothing is sent anywhere**, and no issue is filed on the user's behalf.

Asking for the request verbatim, or noting that the log entry will be thin without it, is a **pass**.
Refusing to record until the user supplies more detail is a fail — a thin entry beats none, because
by tomorrow the detail is gone either way.
