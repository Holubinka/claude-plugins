Fourteen files is exactly the size at which a file-by-file list feels helpful. It is on the
never-include list because the diff is already there and is authoritative, while a prose copy of it
drifts on the next push.

The response passes only if **all** of the following hold.

1. **The four labelled parts are present in order** — What, Why, Testing, Risk — as bold labels, not
   `##` headings.
2. **What is numbered, and Why points back by number** rather than restating the items.
3. **No file-by-file list, no commit log, no diff statistics, no per-suite test counts, no raw tool
   output, and no narration of the process.** Any one of these is a **fail**.
4. **Testing is written in the past tense as a report**, not as reproduction steps for the reviewer
   to follow.
5. **The unverified part is stated.** The real-upstream behaviour was not observed, and a description
   that says "tested" without that qualification is a fail — it costs the next reviewer their trust
   in every future one.
6. **It is under forty lines.**

Naming the eleven call sites as one item ("eleven call sites updated to pass the option") is a
**pass**. Listing them is not.
