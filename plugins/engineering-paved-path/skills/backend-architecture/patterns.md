# Patterns — the signal that one is warranted, and the commoner signal that it is not

Reference for `backend-architecture`. Sources in [`references.md`](references.md).

**The rule of three governs all of them.** Copy once. On the third occurrence, abstract — because
with two examples you do not know the shape yet, or whether there is one. A wrong abstraction costs
more than the duplication it removed and is harder to reverse, since every caller now depends on its
shape.

| Pattern | Warranted when | Usually reached for when |
| :--- | :--- | :--- |
| **Repository** | Two storage backends exist, or the domain must be testable without a database and the ORM cannot be faked cheaply | There is one database and there always will be. The ORM is already the abstraction |
| **Factory** | Construction genuinely varies by input, and the variants exist | One product, and `new` would have done |
| **Strategy** | Two or more algorithms are selected at runtime, today | One algorithm and a belief that a second may arrive |
| **Adapter** | An external contract does not match yours and you do not control it | Wrapping a library you chose, whose interface you already like |
| **Observer / event bus** | Several unrelated consumers must react, and the producer must not know them | Two functions that could call each other directly |
| **Decorator** | Behaviour composes in combinations you can name | One cross-cutting concern, where a function would do |
| **Singleton** | Almost never. A module already is one | A shared instance, which module scope already gives you |
| **DI container** | Wiring has become the hard part, at real size | Three dependencies, where the composition root would have been fifteen lines |

## The three questions before any of them

**What is the second case, and does it exist?** Named and present is a requirement. Named and
hypothetical is a guess about the future, usually wrong in a direction the abstraction cannot bend.

**What does this stop me doing?** Every pattern trades directness for flexibility along one axis. If
you cannot say which axis, the trade has not been made — it has been assumed.

**What does the next reader traverse?** An interface with one implementation is one hop between a
reader and the code that does the work, forever, in exchange for nothing yet.

## Wrapping a library

**Know what the wrapper gives you before writing it.** A wrapper added by reflex reimplements a
subset of the library badly, still leaks the library's types through its own signatures, and now has
to be maintained alongside it.

Legitimate reasons: the library's surface is far larger than your use of it and you want the smaller
one enforced; you have a second implementation; the library's errors need translating into your own
failure model at one place. "In case we swap it" is not one — a swap rewrites the wrapper too.

## Where a pattern is already in the repository

**Use the one that is there, even if you would have chosen differently.** A second way to do one
thing costs every reader who must learn both and every author who must choose. If the existing
pattern genuinely cannot express what you need, that is worth one line in your report — it is a
finding about the codebase, not a licence to start a third.
