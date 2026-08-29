# Merging concurrent lanes

Reference for `review-diff`. Why the review writes nothing, and the exact order the merged table
comes out in.

## Nothing is written during a review

Findings are **return values**. The orchestrating turn's context is the store, and no file is created,
appended to, or read.

Four reasons, in order of force:

1. **Three lanes appending to one file are three tree mutators.** The reason parallel review is safe at
   all is that every lane's write set is empty while it reads. A findings file breaks that for the sake
   of a file nobody needs — and the failure is silent, because what each lane reports is still correct,
   it is just describing a tree that was moving.
2. **It is a lost-update race** with no locking primitive available to a subagent.
3. **A gate that fingerprints the working tree stops matching**, and refuses while pointing at an edit
   nobody made. A review that writes nothing cannot trip one, needs no ignore entry, and needs no
   cleanup.
4. **It is unnecessary.** Parallel agents already hand structured output back to the dispatching turn.
   A file only becomes necessary when something that cannot read a return value — a shell hook — has to
   see the findings, and nothing here is a shell hook.

The escape valve is a request, not a protocol: if someone asks for the findings written to a path, the
orchestrator writes that path, after every lane has returned.

## Lane-prefixed ids

Each lane numbers its own findings with its own prefix — `C1, C2…` correctness, `A1…` boundaries,
`D1…` dependencies.

**That is the whole trick.** Three concurrent returns merge without a shared counter, so they need no
shared state, so they need no file. It also means every row in the merged report says which lane found
it, without a separate column being maintained by hand.

## The merge, in order

**1 — Normalise the anchor** to `(repository-relative path, line)`. A finding with no line normalises
to `(path, 0)`.

**2 — Collide within ±2 lines**, not on exact equality. Three lanes reading one expression will
naturally cite the statement, the call and the declaration, and those are the same problem.

**3 — Agreeing invariants become one row**, at the highest severity of the group, with every
contributing lane listed. Three lanes agreeing is one problem, not three, and reporting it as three is
how a report gets its length from its redundancy.

**4 — Disagreeing invariants at one anchor stay as a flagged pair**, marked *same anchor, different
invariant*. **That pair is signal, not noise** — it usually means the line is doing two things.

**5 — Deterministic outranks model-produced, and the merge may not downgrade it.** A finding whose
evidence is a command's exit code — a failing typecheck, an advisory — wins the severity at its anchor,
and the model-produced finding is kept beside it rather than folded into it. Between two model-produced
findings the higher severity survives, carrying that one's verification outcome.

**6 — Diff-anchor before sorting.** Any model-produced finding whose line is not in the diff drops to
`note`, marked pre-existing.

**7 — Sort deterministically:**

```
severity descending, then deterministic before model-produced,
then path ascending, then line ascending, then lane id ascending
```

Arrival order is a function of which agent finished first, so a report ordered by arrival is
unreproducible and a diff of two reports is meaningless. **Two runs over the same diff must produce the
same report.**

## Counting

Say how many criticals you verified, not just how many survived. A run that raised four and verified
three has a hole in it, and the count is the only place that shows.
