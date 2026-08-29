---
name: refactor-triage
description: "Sorts a cleanup into what is safe to apply now, what needs the callers read first, and what may only be proposed. Use when asked to clean something up, when a function has grown too large, when duplication or dead code turns up, or when an N+1 or an unsound cast is spotted while doing something else. Consult it before editing: the changes that look most obviously safe are the ones that quietly alter behaviour."
metadata:
  version: "1.0.0"
keywords: [refactoring, cleanup, behaviour, triage]
---

# refactor-triage

A refactor is a change that **does not change what the code does**. Everything that follows is about
staying inside that definition, because the changes that look most obviously safe are the ones that
quietly leave it.

## Three tiers

Sort every proposed change into one of these before touching anything.

### Apply directly

Mechanical, and a no-op for every caller. Deleting genuinely unreachable code. Renaming a local
variable. Removing a redundant cast the type already guarantees. Collapsing an `if` that returns in
both branches. Deleting a commented-out block.

**The test: could a caller observe the difference?** If the answer needs thought, it is not this tier.

### Apply after reading the callers

Safe *given what the callers do*, which means you have to have read them. Renaming an exported symbol.
Changing a parameter's order or making one optional. Narrowing a return type. Extracting a helper used
in two places.

**Read every call site first, not a sample.** "It is probably the same everywhere" is how a refactor
becomes a bug in the one place it was not.

### Propose only — do not apply

Anything that changes behaviour, even for the better. Leave a marker comment naming the reason, and
report it:

```
// REFACTOR(n+1): batches per row; fixing this changes result ordering — see <where you reported it>
```

The standing example, because it is the one people apply by reflex: **fixing an N+1 by batching
changes the order results come back in.** Some caller depends on that order, and neither of you knows
which one. Same for making an error message clearer when something parses it, for changing what a
function returns on an empty input, and for tightening a validation that has been quietly accepting
bad data for a year.

## The categories worth looking for

| Category | Usually | Watch for |
| :--- | :--- | :--- |
| Dead code | apply | Reflection, dynamic imports, a test-only export, a public API |
| Duplication of five lines or more | apply after reading | **Two copies that drifted are not duplicates** — read both call sites |
| A function over ~80 lines, or nesting over four deep | apply after reading | Extraction changes stack traces and error messages |
| Type-safety holes — `any`, an unsound cast, a non-null assertion | apply after reading | Narrowing a type can make a real caller stop compiling. That is information |
| Async hygiene — a missing `await`, `await` in a loop | **propose** | Both change timing, and timing is behaviour |
| Resource leaks — an unclosed handle, a timer never cleared | apply after reading | Closing something a caller still uses |
| An N+1, or a query in a loop | **propose** | Ordering, and the load pattern the database was tuned for |
| Naming | apply after reading | A name that appears in a log line someone greps for, or in a serialised payload |

## Stop after five applied changes

**Hard limit.** Five applied changes, then stop and report.

Not caution — reviewability. A refactor of thirty small changes cannot be reviewed as a refactor; the
reviewer either trusts it entirely or re-derives all thirty, and both of those are worse than reading
five. Beyond that, an unrelated behaviour change hides comfortably inside the noise.

**"While I'm here" is the smell.** Every additional change was individually reasonable, and the
aggregate is unreviewable.

## Never

- **Never mix a refactor with a behaviour change in one commit.** If both are needed, the behaviour
  change goes first, on its own, where it can be reviewed as one.
- **Never refactor code with no test coverage without pinning it first.** See
  `refactor-safely:refactor-planner` and `refactor-safely:refactor-implementer`, which do exactly that:
  characterisation tests for the current behaviour, green, before any structure moves.
- **Never move a public surface** — an exported symbol, a route, a schema, a serialised shape — as part
  of a cleanup. That is a feature with a compatibility story, not a refactor. Say so and stop.
- **Never loosen a test that goes red.** Red means revert the change that turned it red. Loosening the
  assertion converts a caught regression into a shipped one.

## Report

```
Applied:    <change — file — tier>
Proposed:   <change — file — why it may not be applied — the marker comment left>
Stopped at: <n> of <total identified>
Verified:   <the command that ran, discovered how, and its result>
```

The verify command comes from `engineering-paved-path:project-commands` — the task's own instruction,
then a convention file, then CI, then the manifest's scripts. **If no command can be discovered, say
that the refactor is unverified.** An unverified refactor is a legitimate thing to hand back; one
presented as verified is not.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Fixing an N+1 as part of a cleanup | It changes result ordering. Propose it |
| Merging two near-identical functions | Read both call sites. Drift is often the point |
| Extracting a helper and moving on | Extraction changes stack traces; check nothing parses them |
| Thirty small improvements in one pass | Stop at five. The rest is a second pass |
| Refactoring untested code, carefully | Careful is not a verification. Pin it first |
| Loosening the test that went red | That is the regression the test just caught |
