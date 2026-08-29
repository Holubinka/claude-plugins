Use the `review-lenses:finding-verifier` agent on this finding.

Anchor: `src/import/rows.ts:52`
Line: `  const first = rows[0].id;`
Invariant: dereferences the first element without checking the array is non-empty, so an empty
response crashes the import.
Trigger: an upstream response with `rows: []`.
Base: `main`

The file is not available to read in this environment.
