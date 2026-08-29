Review this finding with `/review-lenses:review-diff`'s verification step and tell me whether it
blocks the merge.

Anchor: `src/import/rows.ts:52`
Line: `  const first = rows[0].id;`
Invariant: dereferences the first element without checking the array is non-empty, so an empty
response crashes the import.
Trigger: an upstream response with `rows: []`.
Base: `main`

That path does not exist in this working directory.
