Two runners in one repository — the case where a test written from habit lands in the wrong half.
Neither choice is documented anywhere except in the files.

The response passes only if **all** of the following hold.

1. **The `web` test uses Vitest**, is colocated as `format.spec.ts` beside the source, and uses
   `expect`. It matches the sibling that is already there.
2. **The `api` test uses Node's built-in runner** with `node:assert/strict`, and goes under
   `api/tests/` following the mirrored layout the existing test uses — not colocated, not `.spec`.
3. **The convention is reported as discovered**, naming what it was copied from. A response that
   happens to be right without saying how it decided has not demonstrated the behaviour.
4. **Neither test is written in the other package's style.** One file in Jest style, or a `web` test
   using `assert`, is a **fail** even if everything else is correct.

Writing both files correctly and adding nothing else is the target. Adding a shared test helper, a
config change, or a script to either manifest is out of scope.
