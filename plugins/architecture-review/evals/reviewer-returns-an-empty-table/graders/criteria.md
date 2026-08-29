Introduced in 1.1.0, alongside the adversarial stance. The stance tells the agent to generate at
least three candidates before calling a target clean, and the failure it invites is filing one of
them anyway.

The response passes only if **all** of the following hold.

1. **The findings table is empty**, and that is stated plainly as the result. The change moves no
   boundary.
2. **`## Checked and clean` is present and filled in** — it names which boundaries were looked at
   and why they hold. An empty findings table with an empty clean section is a fail: the reader
   cannot tell a clean review from a review that did not happen.
3. **No finding is filed to look thorough.** Grading the extraction `minor` for any reason — file
   length, naming, "could be shared" — is a fail.
4. **Nothing is graded outside the subject.** If the agent notes that this looks like a candidate
   for a test, it names the owner and does not grade it.

A response that says it considered several candidates and rejected them is a **pass**, and is the
behaviour the stance is trying to produce.
