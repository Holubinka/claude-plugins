---
name: systematic-debugging
description: "Finds the cause of a defect before changing anything. Use when there is an observed symptom to point at — a crash, a test failing for a reason you do not understand, output that disagrees with the code, a slowdown, a build that breaks on one machine and not another. Consult it before proposing a fix, especially under time pressure or after a first fix did not work. Not for reading code to judge whether it looks correct when nothing has actually gone wrong: that is a review."
metadata:
  version: "1.0.0"
keywords: [debugging, root-cause, defects, investigation]
---

# Systematic debugging

**No fix before the cause is known.**

A change that makes a symptom disappear without an explanation has done one of two things, and you
cannot tell which from the outside: fixed the defect, or moved it. The second is worse than leaving
it, because the next person inherits a bug with a comment above it saying it was handled.

**It starts from a symptom you can point at.** No observed failure means there is nothing to find
the cause of — "read this and tell me whether it is right" is a review, and reviewing is a different
activity with a different lens. Come back here the moment something actually misbehaves.

**This applies hardest when it feels least affordable.** Under an outage, on a second attempt after
a first fix failed, when the change is one line — those are exactly the conditions under which
guessing feels faster and is not. A wrong fix costs a full cycle plus the time spent trusting it.

## Four phases, in order

### 1 — Establish what actually happens

Not what is reported. What you can observe.

**Reproduce it**, and write down the smallest input that does. If you cannot reproduce it, that is
the finding, and the work is to make it reproducible — an intermittent defect chased by guesswork
produces fixes nobody can evaluate.

Then read the evidence completely: the whole error, the whole stack, the exit code, the surrounding
log lines. **The first line of an error is a summary someone else wrote**, and the useful detail is
usually three lines down.

Record what is *not* happening, too. A narrowed absence is as informative as a presence.

### 2 — Locate the cause

**Change one thing at a time, and predict the result before you run it.** A prediction that comes
true confirms a model; a change made without one teaches nothing whichever way it goes.

Bisect the distance between what is true and what is false — in the input, in the call chain, in
history. `git bisect` is the version of this people forget they have.

Read the code between the last point you know is correct and the first you know is wrong. **Read
it, do not skim for the mistake** — the defect is usually in the part that looks fine, since the
part that looks wrong has already been read by everyone who came before you.

### 3 — State the cause, then fix it

Before touching anything, write the cause in one sentence with this shape:

```
<what the code does> causes <the symptom> when <the condition>
```

If you cannot fill in the third clause, you have a suspicion rather than a cause. Go back to
phase 2.

Then fix **that**, not the place the symptom appeared. A null check at the point of the crash where
the real cause is a caller passing the wrong thing moves the defect one frame up and hides it.

### 4 — Prove it

Reproduce the original symptom and watch it stop — the reproduction from phase 1 is what makes this
possible, which is why it comes first. Then check that nothing near it broke.

Grading and evidence rules are `engineering-paved-path:verification-before-completion`. A bug
reported as fixed without the symptom re-run is a prediction.

## The shapes that look like causes and are not

| Looks like a cause | Usually is |
| :--- | :--- |
| The line the stack trace points at | Where it surfaced, not where it went wrong |
| The most recent commit | Where it became visible. A latent defect surfaces on an unrelated change |
| "A race condition" | An unexamined ordering assumption. Name the two things and the order |
| "It is flaky" | A dependency on time, ordering, or shared state that has not been found yet |
| "The library is broken" | Almost never. Check your call first, and check your version |
| The thing you changed most recently | Availability, not evidence |

## Stopping

**Stop and say so when three attempts have not narrowed it.** More attempts after that are the same
attempt with variations, and the value at that point is in what you learned — the reproduction, what
you ruled out, and where the next person should start. Hand over that, not a fourth guess.

**Stop when the fix requires a decision, not an edit** — changing a contract, a boundary, or
behaviour someone depends on. That is a change with a review, not a debugging outcome.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Fixing at the point the error appeared | Fix where it went wrong. The trace shows the surface |
| Several changes at once, then re-running | One change, one prediction, one observation |
| Skipping reproduction because the cause seems obvious | Then reproduction costs a minute and settles it |
| Adding a guard so the symptom stops | That is concealment unless the guard *is* the cause |
| "It works now" with no explanation | You do not know what changed. It will return |
| Escalating effort instead of stopping | Three attempts, then hand over what you learned |
