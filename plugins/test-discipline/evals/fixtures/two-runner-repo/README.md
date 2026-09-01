# two-runner-repo

A fixture with two test runners in one repository — the common case, and the one where a test
written from habit lands in the wrong half. `api/` uses Node's built-in runner with
`node:assert/strict` and mirrors its sources under `tests/`. `web/` uses Vitest with colocated
`*.spec.ts`.

Neither choice is stated anywhere except in the files themselves. That is the point.
