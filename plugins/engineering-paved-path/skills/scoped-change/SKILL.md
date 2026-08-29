---
name: scoped-change
description: "Keeps a change to what was actually asked for. Use when a request arrives with flexibility, configurability or extensibility attached, when tempted to add an abstraction, an option or a layer nobody requested, when about to tidy code adjacent to the one line that needed changing, and when a request has two readings that would produce different work. Consult it before starting, not after — the cost of a change nobody asked for is paid by whoever reviews it and everyone who maintains it."
metadata:
  version: "1.0.0"
keywords: [scope, simplicity, minimal-change, over-engineering]
---

# Scoped change

Two failures, and they are the same failure pointed in different directions: **building more than
was asked**, and **changing more than was needed**.

Both feel like care while you are doing them. Both are read as noise by whoever reviews the diff,
because a reviewer cannot tell a deliberate improvement from an accident without asking.

## Build only what was asked

- **No feature beyond the request.** Not the obvious next one, not the one that would be trivial
  while you are here.
- **No abstraction for a single use.** An interface with one implementation, a factory with one
  product, a strategy with one strategy — each is a layer a reader must traverse to reach the code
  that does the work.
- **No configurability nobody requested.** An option is a promise to support every value of it,
  forever, and a branch nobody tests.
- **If two hundred lines could be fifty, write fifty.** Then check the fifty do the whole job.

**"Flexible", "extensible" and "future-proof" in a request are worth one question**, not an
architecture: *what is the second case?* A named second case is a requirement. An unnamed one is a
guess about the future, and the guess is usually wrong in a direction the abstraction cannot bend.

## Change only what you must

- **Do not improve adjacent code**, its comments, or its formatting while you are in the file.
- **Do not refactor what is not broken** as part of a change that is about something else.
- **Match the existing style, even where you would do it differently.** A file written in a style
  you dislike, consistently, is easier to read than one in two styles.
- **Do remove what your own change orphaned** — an import, a variable, a function that nothing
  reaches now because of what you did. That is part of the change, not a tidy-up.

The test for anything else: *would this line be in the diff if the request had never arrived?* If
yes, take it out. It belongs to a separate change with its own review. There is a plugin in this
marketplace for what that change looks like when you do make it; it is named in prose here rather
than linked, because it depends on this one and the reverse edge would be a cycle.

## Say which reading you took

When a request has two readings that lead to different work, **name both and pick one out loud**
rather than choosing silently:

> "This reads two ways — a per-user setting or a global one. I am taking per-user because the
> request mentions the profile screen. Say if you meant the other."

A silent choice looks identical to a decision that was thought about, right up until it turns out
to be the wrong one, and by then the work is built on it. Naming it costs one sentence and makes the
correction cheap.

**Push back when a simpler approach exists.** That is not obstruction; it is the cheapest moment to
change direction.

## Where this cannot help you

**It fires on a request, not on an impulse.** A request that says "make it configurable" reaches
this skill. The urge to add a factory while implementing something perfectly well-specified does
not, because nothing in the request signals it.

That half is always-on behaviour rather than a trigger, and it belongs in the repository's own
`CLAUDE.md` where it is in context on every turn. [`always-on.md`](always-on.md) carries a short
version to copy in.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Building the general case for one caller | One caller is one function. Generalise on the second |
| Adding an option because a value might change | Change it when it changes. An option is a permanent branch |
| Reformatting the file you edited | The diff should show the change, not the formatter |
| "While I'm here" | The clearest signal that a second change is starting |
| Rewriting to your preferred style | Consistency beats preference, and the file was here first |
| Silently picking one reading of an ambiguous ask | Name both, take one, say which |
| Leaving imports your change orphaned | That cleanup *is* the change. Only that one |
