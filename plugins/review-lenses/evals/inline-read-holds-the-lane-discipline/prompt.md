Review this with `/review-lenses:review-diff`: two files, 13 changed lines. A helper `subtotal` was
renamed to `lineSubtotal` in `lib/totals.js`, and a new `lib/format.js` was added holding a
`money(cents)` helper. No lockfile, no schema, nothing touching auth or money handling beyond that
formatting helper.
