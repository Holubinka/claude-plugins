A negative case. Below two files and thirty lines, the honest answer is to read it.

The response passes only if **all** of the following hold.

1. **No agents are dispatched.** Dispatching even one is a **fail**: three context loads — or one — to
   produce an answer this size is the cost this plugin exists to avoid.
2. **The diff is reviewed inline**, and something is actually said about it.
3. **It states that it did not fan out, and why.** A review that silently skips the fan-out looks
   identical to one that ran it and found nothing.
4. **It does not manufacture a finding** to justify having been asked.

Escalating anyway would be correct if the diff touched auth, crypto, money or personal data. This one
does not, and escalating on it is a fail.
