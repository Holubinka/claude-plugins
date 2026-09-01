Two findings came back on my branch. One is that `npm run typecheck` exits 2 with
`src/api/orders.ts(41,7): error TS2532: Object is possibly 'undefined'`. The other is a reviewer
saying that same line could crash on an empty response, but a second pass could not confirm any
caller that reaches it with an empty body.

Grade both, and tell me which of them blocks the merge.
