---
name: run-plan
description: "Executes an approved plan end to end — dispatches the implementer, exercises the feature through its real entry point, verifies it against the plan, reviews it for bugs and for boundaries, and runs a bounded fix loop over what the reviews returned. Use when the user runs /sdd-engineering:run-plan, when they hand over a plan path and ask to build it, or when they ask to carry out or execute a plan that already exists. It never authors a spec or a plan — spec-creator and implementation-planner are dispatched by hand before it. It never commits or pushes."
metadata:
  version: "1.0.0"
  tags: pipeline, orchestration, plan-execution, spec-driven, subagents, fix-rounds
---

# run-plan — an approved plan, carried out end to end

```
/sdd-engineering:run-plan <path-to-plan> [P1]
```

The plan path, plus a work-package id when the plan's `**Execution:**` is `multi-agent` and only that package is wanted. Nothing else is an argument.

You are the orchestrator. You dispatch, you carry the thread between stages, and you stop where this file says stop. Every agent starts with a **clean context window** and knows only what the previous stage left on disk — that is why the plan is a file, and why a fix round gets one too.

## Navigation

| Read | For |
|---|---|
| **This file** | When it runs, the six stages, the boundary with the sibling skills, what is deliberately absent |
| [fix-rounds.md](fix-rounds.md) | What to do with what the reviews returned: the three triage filters, the brief format, and why the cap is two |

## 1. When it runs, and when it must not

Run when: the user invokes this skill; they hand over a plan path and ask for it to be built; they ask to execute or carry out a plan that already exists.

**The spec and the plan are not this skill's business.** `spec-creator` and `implementation-planner` are dispatched by hand, so that a human sees the requirements and then the plan before any code exists. By the time you run, both decisions are made.

Stop before stage 1, having dispatched nothing, when:

- no plan path was given, or it does not resolve. Ask for one; never plan the work yourself;
- the plan still carries an **unanswered entry under** `## Open questions`, or `## Requirements as understood` rows whose `Status` is `assumed` and which nobody confirmed. That is a planning problem, and building on it is how a whole feature is thrown away. The heading itself is always present — the planner's template mandates it — so read the body: `_None._` is the passing value, and refusing on the heading alone would refuse every plan;
- the working tree is on the repository's default branch. Branch first, or the work has nowhere to land.

Do **not** run this to make a one-file change, a rename, or a fix. A stage a change does not need makes that change worse, not safer.

## 2. Stage 0 — preflight

1. **Read the plan's header, `## Out of scope` and `## Verification`** — not the steps. You need the boundary and what success looks like; the steps belong to the implementer, which reads them in its own context.

2. **`rg` the nouns of the plan.** Repositories carry scaffolding for work that never landed — tables that migrate but stay empty, contracts nobody constructs, registry entries with zero callers. One grep separates "how would this work" from the far cheaper "what is already wired". **Paste the output** into every agent you dispatch — the matched lines, not your summary of them — so none of them pays to rediscover it.

   Measured: the brief that pasted its evidence bought its first write after **4** scout calls; the brief that described the same class of thing took **39**. Hand it over as **shapes, not names**: "`formatCost` exists" saves a search; "`Agent` has `description` and no icon field" saves a decision round-trip after the component is written.

3. **Every factual claim you put in a dispatch is read from the file as you write it**, and carries its `path:line`. Not from an `INSIGHTS.md` entry, not from the spec's summary of a file, not from a grep over one directory — those are the three stale sources that produced five false premises on one run, each costing an agent a round of archaeology. Anything you cannot address, write as a hypothesis in those words.

4. **Check the ports before anything starts a server.** Where a repository is worked on in several worktrees at once, the usual dev ports frequently belong to another checkout, and an agent that assumes otherwise gets someone else's page or a port-in-use error. `lsof -i :<port>`, then put one line in every dispatch: *"port N is another checkout — bring your own API up on N+1."*

5. **A design is transcribed once, before any dispatch, and the transcription is what the briefs carry.** Four images cost nineteen agent reads on one run, and a design walk written late did not stop it — because every rule downstream tells an agent to distrust prose about a layout, rightly. So it must not be prose. Open each image yourself and write a five-axis walk — placement and hierarchy, the shape of each value, every label in the design's own words, what each element does, what the design shows that the contract cannot express — to a file beside the image. From then on **that file is the design**.

   - **Intake first.** A subagent cannot see the conversation, so an image pasted into chat reaches nobody. Save it to a path first and refer to it by that path forever after.
   - **Route it.** The walk goes only into briefs for packages that own UI files. A backend package gets no design at all, and given how many agents open those images, that alone is most of the saving.
   - **Let it heal.** An agent may open the image when the walk cannot answer its question — and when it does it appends the missing row and says so. That makes the Nth read the last one rather than the first of many.

## 3. Stage 1 — build

`single-agent`: one `implementer`, the plan path as its input.

`multi-agent`: one `implementer` per work package, in the dispatch order the plan's work-packages section closes with. Packages that neither block the other go in **one message**, so they actually run concurrently. Give each agent its package id and nothing else — its own package block carries the contract it may assume, and the planner repeated it there precisely so no agent has to read another's steps.

**At most two `judgement` packages in flight.** Three heavy implementers at once is what hit the session limit on one measured run: the kill cost 89M tokens in restarts against 52M of work done, and recovering from it plus repairing what it produced came to **45 % of the whole run's tokens against 26 % for building the feature**. Two concurrent is slower in wall-clock and strictly cheaper than three plus three restarts. Dispatch a package the plan marks `mechanical` at a lower tier — a constant plus a guard does not need the top one.

**Two or three agents in flight at once, never more, and the batch goes in one message.** Parallelism is a wall-clock lever, not a token one — each concurrent agent buys its own cold context, which is the most expensive thing a run pays for — so the cap is what stops it being neither. One message per batch is the token half: an orchestrator turn costs the same whether it dispatches one agent or three. A fourth package waits for a slot, and a plan with five simultaneously independent packages usually means the contract between them was never fixed.

**A spec being amended is not a spec to build against.** If `spec-creator` is still writing, wait for it. Four minutes of overlap on one branch let an implementer read criteria that were rewritten underneath it, and the criterion it missed had to be added by the next agent.

**A follow-up change to a surface goes back to the agent that built it.** `SendMessage` to that implementer, never a fresh dispatch: measured, the resumed UI implementer did 393 turns of work with 34 scouting calls where a fresh one did 273 with 67. A cold agent buys the whole "where does everything live" pass again, and that pass is most of what a run pays for. Before you send, sweep the whole screen the request came from — half the resumes on that run were things already visible when the previous one was sent.

### If an agent is killed mid-package

Its work is on disk and its context is gone. Do **not** hand-write a survey of the tree and label it "a guide, not the truth" — the successor then re-verifies every line of it, and you have paid twice. The restart brief is:

- the killed agent's progress note, quoted;
- pasted `git status --short`, `ls` of the new directories, and the `grep -n` that shows the state you are claiming — output, not prose;
- **two timestamps: when that state was captured, and what you know has happened since.** A paste is true when taken; two of five items in one branch's resume brief had already been fixed by someone else;
- whether the list of remaining work is exhaustive or only what is known.

## 4. Stage 2 — run it

**Exercise the feature through its real entry point.** A `curl` at the API, the page in a browser, the CLI command. Gates prove the code compiles and the fakes returned their fixtures; they prove nothing about a real provider, a real database or a real browser, and that is exactly where the defects that survive review live.

A defect caught here costs one command. The same defect caught after review costs a re-plan, another implementer, and makes the review itself moot — it graded a feature that never ran. If nothing is running and you cannot start it, say so plainly rather than letting green gates imply the feature was seen to work.

## 5. Stage 3 — verify against the plan

Dispatch `plan-verifier` with the plan path.

In `multi-agent`, dispatch it **per package as that package lands**, not once at the end: a package's `**Contract:**` block is what every later package was told it may assume, so verifying it late turns one package's divergence into three packages of rework. When the packages are genuinely independent and consume nothing from each other, one run at the end is enough — say which you chose and why.

`NOT_MET` and `PARTIAL` rows **skip the triage in [fix-rounds.md](fix-rounds.md) entirely**: the plan asked for them, so they are unfinished work rather than findings to weigh.

## 6. Stage 4 — review

Two reviews, both read-only, dispatched together in one message:

| Dispatch | For | Note |
|---|---|---|
| **`/code-review`** | the logic — bugs, correctness, efficiency | Built into Claude Code. Use `high` on a feature |
| **`architecture-review:architecture-reviewer`** | the boundaries, given the diff or the modules touched | Runs on `sonnet` |

**Nothing else in this pipeline hunts bugs.** The architecture reviewer routes correctness and performance away by its own *Subject* section, and no test-writing agent is in this pipeline at all. Leave `/code-review` out and a logic error passes every stage with a clean report at each one.

Read the architecture reviewer's `critical` and `major` as *"look at this"* rather than as a grade. That axis is the least reproducible thing it produces — the same finding scored `major` on one run and `minor` on the next — which is why nothing is allowed to threshold on it.

## 7. Stage 5 — the fix rounds

**[fix-rounds.md](fix-rounds.md)** carries this whole stage: where the brief goes and why, the three triage filters in the order they apply, what the brief holds, and why there are at most two rounds. Read it before acting on a single finding.

The one thing worth knowing without opening it: **an empty fix round is the ordinary outcome** on a careful diff, not a review that failed.

## 8. Stage 6 — close

Run the `sdd-engineering:engineering-insights` skill for the session as a whole. Each agent recorded its own; what is left is what only you saw, crossing the stages.

**Then stop, and hand back.** The commit, the push, the pull request and whatever pre-PR review the repository runs are the human's. Your final report says what shipped, what each stage found, which dispatches you downgraded a tier, and what is left for a person to look at.

**Say whether documentation was written**, and when it was not, name the mechanism you judged nobody would have to read. One measured run shipped a whole multi-agent review feature and wrote not one line of documentation for it — and because the skip was never stated, nobody got to disagree with it.

## 9. Boundary with the sibling skills

Split by **what happens after the output**, not by what is inspected.

| Run | Answers | Blocks? |
|---|---|---|
| **`run-plan`** (this) | Does the repo now match a plan that was approved? | no — it orchestrates; it issues no verdict |
| `/code-review` | Is the logic right? Does this code have bugs? | no |
| `sdd-engineering:engineering-insights` | What did this session learn that the next one should not rediscover? | no |
| `sdd-engineering:workflow-retro` | What did the orchestration cost, and what should the next brief carry? | no |

Where the repository has its own pre-PR review or gate command, that is the human's step and this skill never runs it.

## 10. Never

- **Never write or edit the plan**, and never write a spec. Both are records by the time you run. A divergence is a line in your report, not a correction you apply.
- **Never run more than two fix rounds**, and never start a third because the second returned something new.
- **Never fix a `pre-existing` finding inside a round.**
- **Never dispatch a test-writing agent from here** — see §11. If one is ever added, it runs **alone**: its *prove the test can fail* rule leaves a deliberate defect in the tree between mutating a file and reverting it, and any sibling that reads those files or shells out to a gate measures the mutation rather than the branch.
- **Never commit or push.** Ending a run with a commit nobody asked for makes a stage's output irreversible before it has been read.

## 11. What is deliberately not here

**A test-writing stage.** The tests a plan asks for are the implementer's — it ships them beside the code, and `## Tests` is a section of the plan it executes. What is lost is only *gap coverage*: code that shipped without a test and that nobody has since asked to cover. That gap is real and it grows quietly, so cover it by hand when a module has drifted — and never beside anything else.

**`spec-creator` and `implementation-planner`.** Dispatched by hand, before this skill runs.

**The model tiers are a cost decision, not a ranking.** `architecture-reviewer` runs on `sonnet` because its output is advisory — a human reads every row and decides. `implementer` and `plan-verifier` stay on `opus` because their failures are silent: code that compiles and is wrong, and a `MET` row for something that never happened.

**`effort` is that decision one notch finer, and every agent states it** — `medium` on the advisory ones, `high` on those that produce code, a plan, a spec or a verdict. `high` there is a **ceiling, not a raise**: without the field an agent inherits the session, and one measured run sent **20 of its 23 agents at `xhigh`** for exactly that reason — not one of them declared an effort. Do not lower the producing agents hoping to save tokens. Effort prices *thinking*, and thinking is not where a run's money goes: one run produced 386 k output tokens against 477 M re-read. The model tier prices both; effort only the first.

**The per-dispatch override is the cut that costs nothing.** The `Agent` tool's `model` parameter beats the frontmatter for one call, so mechanical work can drop a tier without touching the file — a fix round whose brief already carries `path:line`, the rule and the shape that satisfies it leaves little to reason about. Say in your report which dispatches you downgraded.
