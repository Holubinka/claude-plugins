Use the `architecture-review:architecture-reviewer` agent to review the boundaries in this change:

A new pure function `etaLabel(order)` was added to `helpers.ts` beside the component that was
already calling an inline copy of it, and the inline copy was deleted. Nothing else changed —
no imports crossed a directory, no new dependency, no data shape moved.
