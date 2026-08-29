# Behaviour evals

Seven cases, one per boundary this plugin's shared rules depend on. Three are refusals, and they are the ones that matter most.

| Case | The boundary it tests |
| :--- | :--- |
| `ts-diagnostic-reports-not-scanned` | A diagnostic never reports a clean project it did not look at |
| `security-fires-outside-its-sample-stack` | The security guidance applies where its code samples do not |
| `severity-keeps-a-deterministic-finding` | A failing command outranks a read of the code, and neither erases the other |
| `project-commands-refuses-to-invent-a-gate` | A gate that does not exist is reported missing, never green |
| `verification-reports-not-run` | Silent output is not a pass — a check that looked at nothing is its own outcome |
| `scoped-change-refuses-unrequested-flexibility` | A request that asks for flexibility gets one question, not an architecture |
| `debugging-refuses-without-a-symptom` | **From a routing probe.** No observed failure means review, not a root-cause investigation |

The last two are a pair. `severity-scale` and `project-commands` both exist to make one thing
impossible — **a green result that was never earned** — and each does it at a different point:
one when a finding is graded, the other when a command is chosen. A suite that only checked the
positive direction would pass a plugin that had lost both.

`ts-diagnostic-reports-not-scanned` runs against `fixtures/no-src-repo`, whose TypeScript lives
in `packages/api/src/` and `app/`. That shape is not incidental — it is the exact layout that
made the pre-1.1.0 script print two green ticks for a file with an `any` and an unchecked
assertion in it.

## Running them

```sh
claude plugin eval ./plugins/engineering-paved-path --ablation with-without
```

`claude plugin eval` is in early access; on an account without it the command exits without
running anything. These cases were authored against the documented `prompt.md` +
`graders/*.md` shape and have not been executed here.

## What is deliberately not tested

**Whether a skill announces itself.** Every case grades the content of the answer, never a
sentence saying a skill loaded. A model that names the skill and then answers from memory has
failed the case; a model that never mentions it and answers correctly has passed.

**The architecture skills' placement advice.** It is a judgement against a repository's own
conventions, and a fixture small enough to score is too small to have any.
