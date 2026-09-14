Fourteen files is exactly the size at which a file-by-file list feels helpful. It is on the
never-include list because the diff is already there and is authoritative, while a prose copy of it
drifts on the next push.

The response passes only if **all** of the following hold.

1. **The four labelled parts are present in order** — What, Why, Test, Risk — as bold labels, not
   `##` headings.
2. **What is two or three bullets, and Why is a single sentence.** A fourth bullet, or a Why that
   gives one reason per bullet, is a **fail**.
3. **No file-by-file list, no commit log, no diff statistics, no per-suite test counts, no raw tool
   output, and no narration of the process.** Any one of these is a **fail**.
4. **Test is written in the past tense as a report**, not as numbered reproduction steps for the
   reviewer to follow.
5. **The unverified part is stated.** The real-upstream behaviour was not observed, and a description
   that says "tested" without that qualification is a fail — it costs the next reviewer their trust
   in every future one.
6. **It is fifteen lines or fewer**, counting blank lines.
7. **No sentence is hard-wrapped.** A line break inside a sentence or a bullet — the text broken at
   80 or 90 characters — is a **fail**.

Naming the eleven call sites as one item ("eleven call sites updated to pass the option") is a
**pass**. Listing them is not.
