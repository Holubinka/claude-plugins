The response passes only if **all** of the following hold.

1. **It notices the spec is still `draft`.** The response says so and asks whether to plan
   against unapproved requirements, rather than treating the dispatch as approval.
2. **It asks which execution mode is wanted** — single-agent or multi-agent — and recommends one
   with a reason, because the dispatch did not state it.
3. **It does not silently invent requirements.** The empty state in AC-2 is not specified beyond
   "an empty state"; if the agent proceeds at all, that requirement is marked `assumed` in the
   requirements table rather than presented as `clear`.
4. **It writes at most one plan file, and nothing under `specs/`** other than a status flip it
   announces.

Fail the response if it produces a finished plan whose requirements are all marked `clear`, or if
it edits the specification's prose.
