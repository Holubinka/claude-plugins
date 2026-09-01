Two findings landed on `src/api/orders.ts:41`. The typecheck exits 2 there with
`error TS2532: Object is possibly 'undefined'`. The correctness lane separately flagged the same line
as a crash on an empty response, and the verifier came back `refuted: true, confidence: "uncertain"`.

Merge them and tell me what blocks the merge.
