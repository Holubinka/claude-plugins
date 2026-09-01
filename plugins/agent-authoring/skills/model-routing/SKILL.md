---
name: model-routing
description: "Chooses the model tier and the reasoning effort for a subagent, and decides where a fan-out is actually costing more than it saves. Use when dispatching an agent and picking a model, when a multi-agent run cost far more than expected, when deciding whether to fan out at all, or when writing the model and effort frontmatter for a new agent. Covers the two knobs, what each one actually reduces, and why making agents cheaper is rarely where the savings are."
metadata:
  version: "1.0.0"
keywords: [cost, model-tier, effort, dispatch, fan-out]
---

# Model routing — match the tier to the work, not to the role

## The two knobs save different things

**Model tier** — a cheaper tier lowers **cost per token and latency**. It does *not* reduce how many
tokens get produced.

**Reasoning effort** — lower effort produces **fewer output tokens**. This is the knob that shrinks
token *count*.

Conflating them is the common mistake, and it produces the specific failure of a cheap model being
handed work it has to redo: the same tokens, several times, at a lower price each. **A subagent's
model is fixed at spawn and cannot change mid-run**, so the decision is made before you dispatch or
not at all.

## Route by the shape of the work

| Work shape | Tier | Effort |
| :--- | :--- | :--- |
| Cross-cutting design, an architectural verdict, adversarial verification, ambiguous requirements, subtle logic | the session's own model | high |
| Implementation, writing tests, ordinary review, tracing a dependency | mid | medium |
| Run-and-report, format and lint checks, a single-fact lookup, a mechanical rename sweep, a deterministic gate | small | low |

The bottom row is where a cheap tier genuinely wins: the output is short by construction, so the only
variable left is price per token. A gate that runs four commands and reports pass or fail is the ideal
case — it is the cheapest context in the run to put a long log into.

## Difficulty is per task, not per role

Start from the role's default, then move it for this instance.

**Downgrade** a clearly easy one: a single-file rename, a run-and-report, a lookup with a known
answer. An agent with two modes should carry the *expensive* mode's default in its frontmatter and be
downgraded at dispatch for the cheap one — frontmatter holds one value, and the safe direction to be
wrong in is the one that costs money rather than correctness.

**Upgrade** a clearly hard one: subtle cross-module logic, a finding whose exploitability is genuinely
unclear, an ambiguous design call.

**Never downgrade the correctness-critical steps** — a schema migration, authorization wiring, the
adversarial check on a finding that would block a merge, the actual fix for a red gate. A wrong answer
there costs more than the tier ever saved.

**The concrete trigger worth writing down** is scope, not subject: when a single dispatch's own scope
exceeds roughly ten distinct changes, or spans more than one module, upgrade it. The arithmetic is not
about quality — a cheap tier does not reduce token *count*, and an over-scoped agent pays the
fresh-context restart tax on every correction round. One measured run went through nine correction
rounds on one task; nine rounds at the cheap tier cost more than two would have at the expensive one.

Splitting the work smaller usually makes this trigger stop firing. **The two levers are the same
lever.**

## Where the real savings are

Cost comes from **not duplicating work**, not from making agents cheaper. In order of impact:

1. **Partition the scope, and name the other lanes.** Fanning out several agents: give each a disjoint
   slice *and* tell it what the others own. Overlap is the largest waste, and it is only fixable at
   dispatch — parallel contexts cannot see each other.
2. **Point them at a map before they search.** A tracer that reads an existing architecture document
   and then verifies one fact costs a fraction of one that rediscovers the structure by grepping.
3. **Ask for a compact, structured return.** An agent's output is data. A fixed table costs a fraction
   of an essay and is more useful to the caller.
4. **Do not fan out when one agent suffices.** Three agents on a two-file diff cost three context
   loads to produce one small answer. Size the fan-out to the change.
5. **Choose the lanes from the change, never from a fixed roster.** A roster that always runs
   everything is a roster nobody reads the output of.
6. **Send a follow-up to a running agent rather than spawning a fresh one.** A new context re-reads
   everything the first one already had.

## Two things that do not save money

**Making subagents talk to each other.** They run in isolated contexts with no shared channel, so
"collaboration" is implemented as messages plus each one re-reading the others' output. It adds
tokens in exchange for the appearance of coordination.

**Nesting fan-outs deeply.** Each level multiplies context loads, and the results have to be merged by
something that has read all of them. Two levels is usually the honest limit; past that, the merging
turn becomes the expensive one.

## Writing the frontmatter

Declare both keys on every agent, and treat the file as the conservative default rather than the
answer — the dispatch overrides it, and an override at dispatch beats a value in a file.

Where a project's tooling offers five effort levels, **use three**. Five means the next person has to
choose between five, and the two extremes are better reached for deliberately at dispatch than
selected by habit in a file.
