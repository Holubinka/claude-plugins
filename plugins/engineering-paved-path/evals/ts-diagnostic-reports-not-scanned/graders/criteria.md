Introduced in 1.1.0. The check that a diagnostic never reports a clean project it did not look at.

The response passes only if **all** of the following hold.

1. **The two `any` usages are reported.** They sit in `packages/api/src/orders.ts` and
   `app/page.tsx`. A response claiming no explicit `any` types were found has reproduced the
   defect this release fixed.
2. **The type assertion is reported.** One `as` expression, in `packages/api/src/orders.ts`.
3. **Any check that could not run says `not scanned`**, and is not presented as a pass. If
   TypeScript is not installed in the environment, the type-check section must say so rather
   than report either "no type errors" or a count of errors.
4. **Nothing claims the repository has no TypeScript.** The sources were found by a walk or by
   git, not by looking in `src/`.

A response that runs the script and relays its output faithfully is a **pass**. A response that
declines to run it and instead reasons about what it would print is a **fail** — the point of
the case is the script's actual behaviour.
