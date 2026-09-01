# The always-on half

A skill fires when its description matches the request. Some of this discipline has to be true on
**every** turn — including the turns where nothing in the request hints at it, which are exactly the
turns where over-building happens.

That cannot be a skill, and a plugin should not pretend otherwise. It belongs in the repository's own
`CLAUDE.md`, which is in context on every turn.

## Copy this in

```markdown
## Scope

- Build what was asked, and nothing beyond it. No abstraction for a single use, no option nobody
  requested, no "flexibility" that has no named second case.
- Change what the task needs and nothing adjacent. Do not improve, reformat or refactor code you
  are only passing through. Do remove what your own change orphaned.
- Match the existing style, even where you would do it differently.
- Where a request has two readings, name both and say which you took.
- Before saying something is done, run the thing that proves it and paste what it printed.
```

Six lines. Keep it that short: a `CLAUDE.md` section long enough to skim past is a section that gets
skimmed past, and this competes for attention with everything else on every turn.

## Why not a hook

Some plugins inject their methodology at session start so it is guaranteed to be in context. It
works, and it is the wrong trade here for two reasons.

**It spends context on every session whether or not the session writes code.** A `CLAUDE.md` section
is the user's own budget, spent knowingly.

**It is not the user's decision.** A plugin that installs its opinions into every turn has taken a
choice that belongs to whoever owns the repository — and this marketplace's own
[security policy](../../../../docs/security.md) prefers a skill to a hook for exactly that reason.

The honest arrangement is: the plugin provides the text and the reasoning, the repository decides
whether to carry it.

## What is already covered elsewhere

Two of the four failure modes this comes from do not need anything new here:

- **Not asking when uncertain** — the agents in this marketplace return a clarification block as
  their whole output and stop, rather than guessing. That is enforced by their prompts, not by advice.
- **No success criteria** — `engineering-paved-path:verification-before-completion` holds it, and
  `sdd-engineering` turns acceptance criteria into the thing a plan is graded against.
