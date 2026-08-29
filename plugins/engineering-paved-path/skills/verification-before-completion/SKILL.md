---
name: verification-before-completion
description: "Requires fresh evidence before any claim that work is done, fixed, passing or ready. Use before saying a task is complete, before reporting a gate green, before opening a pull request, and whenever about to write that something works. Also use when a check was skipped, could not run, or scanned nothing — because a check that did not run is not a check that passed, and the two look identical in a report."
metadata:
  version: "1.0.0"
keywords: [verification, evidence, completion, gates, honesty]
---

# Verification before completion

**Evidence before claims, always.**

The rule in one line:

> If you have not run the command **in this turn**, you cannot say it passes.

Not "it passed earlier". Not "it should pass". Not "the code looks right". Those are predictions,
and a prediction reported as a result is the one mistake nothing downstream can recover from —
every later stage takes it as settled.

## The gate

Before claiming any status, or expressing satisfaction with a piece of work:

1. **Identify** — what command or observation would prove this claim?
2. **Run it** — fully, freshly, not a subset and not a remembered result.
3. **Read the output** — including the exit code, and the count of failures.
4. **Compare** — does what you just read actually support the claim?
5. **Then claim it, with the evidence attached.**

Skipping a step is not a shortcut, it is a different activity. Deciding a claim is true and then
looking for support is the shape of every false green report ever written.

## Three outcomes, not two

This is the part most reports get wrong. A check has **three** possible results:

| Result | Means | May be reported as |
| :--- | :--- | :--- |
| **Passed** | It ran, and the output supports the claim | done |
| **Failed** | It ran, and the output contradicts the claim | not done, with the output |
| **Not run** | It could not run, found nothing to look at, or was skipped | **never as either of the above** |

"Nothing found" and "nothing looked at" produce the same silence and mean opposite things. A
linter with no files to lint, a suite that collected zero tests, a scan of a directory that does
not exist, a gate the repository never defined — each exits 0, and each proves nothing.

**Say `not run`, and say why.** A reader can act on a hole they can see.

## What each claim actually requires

| Claim | Requires | Not sufficient |
| :--- | :--- | :--- |
| The tests pass | The runner's own output, with the count of failures | An earlier run, "should pass", the code compiling |
| The linter is clean | Its output and exit code, over the files in scope | A partial check extrapolated to the rest |
| The build succeeds | Exit 0 from the build itself | The typecheck passing, logs that look fine |
| The bug is fixed | The original symptom, reproduced and now absent | The code changed in the way you intended |
| It works end to end | The real entry point exercised, and its effect read | Unit tests green — they prove the fakes agree |
| Nothing else broke | The wider suite, run after the change | The changed file's own tests |

**The bug row is the one that catches people.** Changing the code that you believe caused a defect
is not evidence the defect is gone. Reproduce the symptom first, so that its absence means
something.

## Never read a verdict through a pipe

```sh
<command> | tail -20      # reports tail's exit status, and tail always succeeds
```

A shell pipeline's exit status is the **last** command's. Piping a gate into `tail`, `head` or
`grep` to shorten the output throws away the exit code — and the exit code is the verdict. The
output that remains still looks like evidence, which is what makes it dangerous.

Redirect to a file, capture the status, then read back what you need:

```sh
<command> > <log> 2>&1; echo "exit=$?"
```

## When you cannot verify

Say so plainly, in the same place you would have made the claim. **"I could not verify this, and
here is what I looked at"** is a useful report. An unqualified "done" that turns out to mean "it
compiled" costs the reader their trust in every later report you make.

Where no command exists to run — the repository defines no gate — that is a finding about the
repository, not a licence to assume. Discovery is `engineering-paved-path:project-commands`; do not
invent a command, and do not install one to have something to run.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| "Tests pass" from a run before the last edit | Fresh, after the change. That is the whole rule |
| Reporting a skipped check as a pass | Three outcomes. `not run` is one of them |
| Piping a gate through `tail` to keep the report short | Redirect, capture `$?`, then read the file |
| A green table with no output pasted under it | The table is the claim; the output is the evidence |
| "Fixed" because the intended change was made | Reproduce the symptom, then show it gone |
| Extrapolating from one file to the package | Run the scope you are claiming |
