# Behaviour evals

Four cases. Two are refusals, and between them they cover the two ways this plugin can fail
usefully-looking: making red go away without finding out what it meant, and producing a test file
that has never run.

| Case | The boundary it tests |
| :--- | :--- |
| `testfix-fixes-the-source-not-the-assertion` | A test asserting the intended contract is not loosened to match broken behaviour |
| `testwrite-copies-the-nearest-sibling` | Two runners in one repository, and each test lands in the right half |
| `test-writer-reports-an-untestable-file` | A test that needs a source change is a finding, never a task |
| `testwrite-writes-nothing-without-a-runner` | With nothing to discover, nothing is installed and nothing is written |

The first case is the one the plugin exists for. **A loosened assertion is indistinguishable from a
correct fix** in the diff, in CI and in the commit message — the only difference is that the defect
ships — so a suite that could not tell them apart would be scoring the wrong thing entirely.

`fixtures/two-runner-repo` deliberately documents its conventions nowhere except in its own files: an
`api` package on Node's built-in runner with mirrored `tests/`, and a `web` package on Vitest with
colocated `*.spec.ts`. A skill that carried a runner table instead of discovering one would get
exactly half of this case right.

## Running them

```sh
claude plugin eval ./plugins/test-discipline --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without running
anything. These cases were authored against the documented `prompt.md` + `graders/*.md` shape and
have not been executed here.

## What is deliberately not tested

**Test quality as prose.** Whether a test is well named or well factored is a judgement, and a
grader for it would score wording rather than behaviour. What is scored is where the file went, which
runner it used, what it asserted on, and what the report admitted it could not cover.
