Use the `review-lenses:finding-verifier` agent on this finding.

Anchor: `evals/fixtures/unsettleable-anchor/src/import/rows.ts:12`
Line: `  const first = rows[0].id;`
Invariant: dereferences the first element without checking the array is non-empty, so an empty page
crashes the import.
Trigger: an upstream response whose page is empty.
Base: `main`
