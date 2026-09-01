# Skill or agent

Reference for `authoring`.

A skill is knowledge loaded into the current context. An agent is a **separate context with its own
permissions and its own budget**. Reach for an agent when you need isolation or restriction — not
when you need instructions.

## An agent needs all four, or it is a skill

1. **Repeatable work.** The same job has come up three or more times. Not "this would be a nice
   role".
2. **Distinct permissions.** A `tools` allowlist that differs from the main session's, *and a reason*
   — a read-only reviewer, a writer scoped to test paths. If it would carry the same tools you
   already have, isolation is the only benefit, and isolation alone is rarely worth a fresh context
   that has to re-read everything.
3. **A defined output format.** A fixed report shape the caller can act on without re-reading the
   work. **An agent's final text is data, not an essay.**
4. **A real handoff.** A named In, a named Out, and a named Next. If nothing consumes its output, it
   does not belong in a chain.

Failing any one of them, write a skill. A skill costs a description line; an agent costs a context.

## Two things that are only true of agents

**Omitting `tools` inherits everything.** That is the wrong default for anything described as
read-only, and it is a silent wrong default — the agent behaves correctly right up until the run
where it does not.

**A `tools` allowlist cannot make an agent read-only on its own.** Withholding `Write` and `Edit`
still leaves `Bash`, which writes through a redirect, an in-place edit, a `tee`, or a commit. Say so
in the body as a rule, and know that the rule is a convention rather than a wall. Where a real wall is
required, it has to come from outside the agent — a hook, or not granting `Bash` at all.

## Distinctness is what actually rots

Check a proposed role against the ones you already have on **criteria, evidence and output format** —
never on its name.

**Two agents that would read the same input and produce the same shape of finding are one agent with
two names**, and they cost twice as much for the same answer. This failure is invisible: nothing
errors, no check fires, the reports just quietly duplicate and the reader stops reading the second
one.

The question that settles it: *what would one of them find that the other would miss?* If you cannot
answer with a concrete example, they are the same lane.

**A role that has not been used in a month should be deleted.** Carrying it costs a description line
on every turn and a decision every time you fan out. Re-adding it later is cheaper than either.

## Where a lane is one of several

If the agent runs beside others, two things belong in its body:

- **What the other lanes own**, by subject, so it does not report what someone else is already
  reporting. Overlap between parallel agents is the single largest source of waste, and it is only
  fixable at dispatch time — parallel contexts cannot see each other.
- **Whether it is safe beside a writer.** An agent that mutates the tree, even temporarily, makes
  every sibling's reads describe the mutation rather than the branch. Readers are safe beside each
  other; a writer is safe beside nothing.
