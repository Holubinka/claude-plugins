# sdd-engineering

Spec-driven development as a pipeline: **a specification, then a plan, then code, then a check that the code is what the plan asked for.** Four agents, three skills, and one rule holding it together — every stage reads what the previous stage wrote to disk, never the conversation.

```sh
/plugin install sdd-engineering@dev-workbench
```

Installing this pulls in `engineering-paved-path`, `research-tools` and `architecture-review`.

## Why the artefacts are files

Every agent here starts with a **clean context window**. It did not see the conversation that produced its input, the files the previous stage read, or the alternatives that were rejected on its behalf.

That is the design, not a limitation. A plan step that only makes sense to someone who watched it being written is not finished, and the cold reader is what proves it. It is also the cost model: a run's bill is re-reading context, so the cheapest thing you can do is write a fact down once, in the place the next agent already has open.

## The pipeline

| Stage | Who | In | Out |
| :--- | :--- | :--- | :--- |
| 1 | `spec-creator` | an idea, a design, sources | one spec: what is being built, for whom, how anyone checks it |
| 2 | *a human* | the spec | approval — the one step no agent takes |
| 3 | `implementation-planner` | the approved spec | one plan: steps, boundaries, skills, gates |
| 4 | *a human* | the plan | approval |
| 5 | `run-plan` | the plan path | orchestrates 6 through 9 |
| 6 | `implementer` | the plan, or one work package | code, and gate output it pastes |
| 7 | `plan-verifier` | the plan and the branch | item-by-item verdicts with evidence |
| 8 | `/code-review` + `architecture-reviewer` | the diff | findings |
| 9 | fix rounds | the findings, triaged | at most two rounds, then stop |

**Stages 2 and 4 are people, and they are the point.** The spec exists so a human can approve requirements before anything is built; the plan exists so a human can approve an approach before code is written. `spec-creator` will never write `approved`, and nothing in this plugin commits, pushes, or opens a pull request.

Typical use:

```
Use the spec-creator agent to specify <the feature>.
      ↓ read it, edit it, approve it
Use the implementation-planner agent to plan specs/SPEC-03-digest.md
      ↓ read it, approve it
/sdd-engineering:run-plan plans/03-digest.md
```

## The agents

**`spec-creator`** — writes requirements, never implementation. Acceptance criteria in EARS (`WHEN` / `WHILE` / `IF…THEN` / `WHERE` / plain `shall`), each traced back to a goal, each naming something observable. It hunts what the design left out — the empty state, the error, the limit nobody stated — and asks instead of inventing.

It is the only agent here with an **enforced** boundary: a `PreToolUse` hook refuses every write outside the specs folder. It may dispatch exactly one subagent, `research-tools:researcher`, and only because that agent physically cannot write, so the gate survives the dispatch.

**`implementation-planner`** — turns requirements into steps a cold agent can execute. It checks the requirements before planning against them, and marks each `clear` / `ambiguous` / `conflicting` / `assumed`. It asks which execution mode is wanted — one implementer or several — every time the dispatch does not say.

The rule that earns its place: **every acceptance criterion in the spec must become a numbered requirement in the plan, or be named by number under `## Out of scope`.** Renumbering `AC-N` to `R#` is the one crossing in this pipeline where a requirement can vanish silently — nothing downstream reads the spec again, so a dropped criterion leaves a report of all-`MET` rows describing a feature that is missing something a human approved.

**`implementer`** — executes the plan and stops at its boundary. It does not design, review, commit or push. It runs the gates the plan lists, character for character, and pastes real output. A refactor it decided was necessary is a finding, not a task.

**`plan-verifier`** — grades the branch against the plan, item by item. It enumerates every item verbatim *before* opening any code, decomposes compound criteria into one row each, answers each with a `path:line` or pasted command output, and then adversarially re-checks everything it was about to call `MET`. It writes nothing, and it never touches the status row it is grading.

## The skills

**`/sdd-engineering:run-plan`** — the orchestrator. Six stages: preflight, build, run it, verify, review, fix rounds, close. It refuses to start when the plan still carries open questions or unconfirmed `assumed` requirements, and it never authors a spec or a plan.

Two of its rules are worth knowing before you use it:

- **Stage 2 exercises the feature through its real entry point** — a `curl`, the page, the CLI command. Gates prove the code compiles and the fakes returned their fixtures. They prove nothing about a real provider, a real database or a real browser, and that is exactly where the defects that survive review live.
- **At most two fix rounds.** Not caution — measurement. One session ran eleven review rounds; the feature stopped producing findings at round seven, and rounds 8–10 were reviewing the fixes to rounds 7–9. That was 2.8M subagent tokens, 42 % of the session, for six minor findings.

**`/sdd-engineering:workflow-retro`** — what the orchestration cost, from the transcripts it left. A bundled script reads the billed `usage` figures; the judgement is yours. Its most useful output is not a number but a sentence: **what a resume said**, because that sentence belonged in the first brief.

**`/sdd-engineering:engineering-insights`** — records what a session learned into the nearest `INSIGHTS.md`, so the next session starts with it. An insight is a record, not a rule; promoting one to the other is a separate, deliberate act.

## Configuration

Everything is optional. Defaults work in a repository with no configuration at all.

`sdd.config.json` at the repository root:

```json
{
  "specsDir": "specs",
  "plansDir": "plans",
  "modules": ["server", "client"],
  "gates": ["npm run typecheck", "npm test"],
  "scratchDir": ".sdd",
  "reportLanguage": "English"
}
```

| Key | Default | Used by |
| :--- | :--- | :--- |
| `specsDir` | `specs` | `spec-creator`, and the write gate that enforces it |
| `plansDir` | `plans` | `implementation-planner` |
| `modules` | discovered | which packages may hold their own `<module>/specs/` |
| `gates` | discovered | what `implementation-planner` writes into the plan's gates section |
| `scratchDir` | `.sdd` | fix briefs, progress notes, retrospective reports |
| `reportLanguage` | `English` | the prose inside report headings; headings themselves never change |

**Add `scratchDir` to `.gitignore`.** Fix briefs and progress notes are scaffolding for one round, and any gate that fingerprints the working tree will otherwise see them and refuse a push while pointing at an edit nobody made.

## What happens when the repository has nothing configured

This is the case the plugin is built for, so it is worth stating exactly:

| Missing | What happens |
| :--- | :--- |
| No `sdd.config.json` | Defaults apply. Agents say which they used |
| No `specs/` or `plans/` folder | Created by the agent that writes the first file |
| No status table in either folder | None is created. The agents skip the row and say so |
| No architecture documentation | `architecture-reviewer` reports that as its first finding and reviews only what is visible from the code — it will not import rules from a skill and present them as yours |
| No boundary gate | The architecture skills apply their rules as a **proposal**, explicitly labelled, never as a finding about your repository |
| **No test, lint or typecheck command** | The planner writes `_None found._` into the plan's gates section and names what it looked at. The implementer **does not invent one, does not install anything, and does not run a package-manager script on the chance that it exists** — it reports plainly that the change could not be verified automatically. A green gate table that was never earned is the one failure this pipeline cannot recover from |

## Dependencies

```
sdd-engineering@1.0.0
├── engineering-paved-path@^1.0.0     6 skills the agents route to
├── research-tools@^1.0.0             the researcher spec-creator dispatches
└── architecture-review@^1.0.0        the reviewer run-plan dispatches at stage 4
    └── engineering-paved-path@^1.0.0
```

Cross-plugin references are namespaced: `engineering-paved-path:onion-architecture`, `research-tools:researcher`, `architecture-review:architecture-reviewer`.

`/code-review` is built into Claude Code and is not a dependency.

## Evals

Six behaviour cases under `evals/`, one per boundary the workflow depends on — all of them refusals rather than quality judgements. See [evals/README.md](evals/README.md), including the note that `claude plugin eval` is currently early access.

## Requirements

- **Claude Code >= 2.1.110** — see [COMPATIBILITY.md](COMPATIBILITY.md).
- **`jq`**, for `spec-creator`'s write gate. Without it the gate refuses every write and says why, which is the correct failure direction but stops the agent.
- **`git`**. `plan-verifier` and `architecture-reviewer` both decide things from `git diff` against the base.

## What is deliberately not here

**A test-writing stage.** The tests a plan asks for are the implementer's, shipped beside the code. What is lost is gap coverage for code that shipped untested and that nobody has since asked to cover — cover it by hand, and never beside another agent: a test writer that proves a test can fail leaves a deliberate defect in the tree between mutating a file and reverting it, so anything reading files or running gates in that window measures the mutation.

**Anything that commits, pushes or opens a pull request.** Ending a run with a commit nobody asked for makes a stage's output irreversible before it has been read.
