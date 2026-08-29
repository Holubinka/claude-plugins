# unsettleable-anchor

A fixture whose anchor is readable and whose answer is not. `src/import/rows.ts:12` dereferences
the first element of whatever `fetchRows` returns. `fetchRows` comes from a package that is not
vendored here, and no type in this repository says whether its result can be empty.

Reading the code settles the *shape* of the claim and not its *truth*. That is uncertainty after
examination, which is the state the verifier is supposed to resolve toward not blocking — and it is
deliberately different from an anchor that cannot be read at all.
