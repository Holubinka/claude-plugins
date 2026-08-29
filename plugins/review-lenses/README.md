# review-lenses

A review through only the lenses the change earned. **A fixed roster costs the same on a two-line change as on a two-thousand-line one, and produces a report nobody reads.**

```sh
/plugin install review-lenses@dev-workbench
```

Installing this pulls in `engineering-paved-path` and `architecture-review` — the second because the boundaries lane dispatches its agent by name, and a backticked name is a promise that it resolves.

## What is in it

| Component | Lane | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `review-diff` (skill) | the orchestrator — sizes, picks, dispatches, merges | 106 | 1 460 |
| `receiving-review` (skill) | the other end — what an author owes a finding | 109 | 1 049 |
| `correctness-reviewer` (agent) | does the code do what it says, on the inputs it will get? | 82 | 1 543 |
| `dependency-auditor` (agent) | what did this do to the dependency tree? | 95 | 1 038 |
| `finding-verifier` (agent) | is this blocking finding actually true? | 61 | 1 147 |

## The lanes, and when each one runs

| Lane | Runs when |
| :--- | :--- |
| correctness | any diff touching executable code |
| boundaries — `architecture-review:architecture-reviewer` | a file crosses a directory the repository treats as a boundary, an import edge changes, or a composition root, route or adapter is touched |
| dependencies | a lockfile or a manifest dependency block is in the diff. **Never otherwise** |

**A lane whose condition is not met does not run, and the report says it was skipped and why.** That second half matters as much as the first: a report that omits the skipped lanes reads as full coverage, which is the one way this skill can mislead someone who trusts it.

Below **two files and thirty lines**, with no lockfile and no schema, it does not fan out at all — it reads the diff inline and says so. Three context loads to produce one small answer is not caution. It escalates out of that regardless of size when the diff touches authentication, authorization, cryptography, money or personal data.

## The three-line finding

Every correctness finding has this shape:

```
<the offending expression, at most two lines> at <path:line>
is wrong because <the rule, invariant or type it violates>
fails on <a concrete input: the actual value, count, ordering or locale that breaks it>
```

**If you cannot name the input that breaks it, you have not found a bug — you have found a thing you do not like.**

The third line is also what makes the finding checkable. A reader can try the input; the verifier can try to refute it. A finding without one is unfalsifiable, and unfalsifiable findings are what teach people to stop reading review output.

## Every blocking finding meets an adversary first

Each model-produced `critical` goes to one `finding-verifier`, whose job is to **refute it** — not to second it. It gets that finding and nothing else: no table, no siblings, no running total, so it cannot trade one against another.

| Verdict | Effect |
| :--- | :--- |
| refuted, **or uncertain after reading the code** | drops out of the blocking set, into `## Attempted and refuted` with the reasoning |
| stands, trigger not reproduced | demoted to `major` |
| stands, trigger reproduced by reading | stays `critical`, marked *survived verification* |
| **not examined** — the anchor did not resolve | keeps the severity it arrived with, marked unverified. **Not a refutation** |

**The last row exists because the first one is dangerous without it.** "Uncertain" and "could not
look" feel the same and mean opposite things — a check that ran and did not settle, against a check
that never ran. Collapsed, a finding gets dropped for lack of *access* rather than lack of *merit*,
and that happens precisely on the findings whose evidence is hardest to reach, which are not a random
sample. So the orchestrator resolves the anchor before dispatching, and a verifier that cannot read
its anchor returns `examined: false` rather than a verdict.

**Uncertain-after-reading counting as refuted is the load-bearing rule.** The alternative — an uncertain verdict leaving the critical in place — makes the stage decorative: it could only ever agree, and a check that cannot say no is not a check.

It is safe because it is scoped to *blocking*. A refuted finding is not deleted; it stays in the report where a human can disagree with it.

**A deterministic finding skips this entirely and may not be downgraded.** Evidence that is a command's exit code — a failing typecheck, an advisory — is reproducible by anyone. A read of the code is not, however right it is. That distinction comes from `engineering-paved-path:severity-scale`, which all three agents grade through rather than restating.

`finding-verifier` has **no `Bash`, by design.** A critical it cannot refute by reading is a critical that survives — and Bash would tempt it to run the suite, which would make it a process reading files in a window the orchestrator may later be writing in.

## It writes nothing

Findings are **return values**. The orchestrating turn's context is the store; no file is created, appended to or read.

That is not a stylistic choice. **Three lanes appending to one file are three tree mutators**, and the reason parallel review is safe at all is that every lane's write set is empty while it reads. The failure would be silent: each lane's report stays internally correct while describing a tree that was moving underneath it. It is also a lost-update race with no locking primitive available to a subagent, and it would trip any gate that fingerprints the working tree, which then refuses while pointing at an edit nobody made.

Lane-prefixed ids are what make the file unnecessary: `C1…`, `A1…`, `D1…`. Three concurrent returns merge without a shared counter, therefore without shared state.

The merge itself is deterministic — anchors normalised, collisions within ±2 lines, agreeing invariants folded into one row at the highest severity, disagreeing ones kept as a flagged pair, then sorted by severity, deterministic-first, path, line, id. **Two runs over the same diff produce the same report**, so a diff of two reports means something.

## The other end of the same idea

`review-diff` files findings and puts every blocking one through an adversary. **`receiving-review` owes them the same scrutiny from the author's side** — a finding is a claim about the code, and the author is the person best placed to check it.

Agreeing quickly is the failure mode. It reads as cooperative and produces edits nobody verified, made to code the reviewer was wrong about, which the next reviewer then has to find. So: read all of it before responding to any of it, restate the requirement, **open the cited line**, and only then decide.

Four verdicts, and all of them are legitimate: correct and fixed, correct but out of scope, wrong with the line quoted, or unclear with both readings named. **Disagreeing is not rudeness and agreeing is not politeness** — a reviewer who is wrong is better served by being told than by watching a change go in that they will have to review again.

Two adjustments for findings from a tool. A **deterministic** one — a failing gate, an advisory — is not up for debate; its evidence is an exit code. A **model-produced** one is a claim that has already survived `finding-verifier`, which makes it worth taking seriously and does not make it correct. Where it names an input that supposedly breaks the code, try that input: one run settles it either way.

## What is deliberately not a lane

**A test writer.** Proving a test can fail means holding a deliberate defect in the working tree between mutating a file and reverting it — so anything reading files in that window measures the mutation rather than the branch, and cannot detect the writer from the inside. **Readers are safe beside each other; a writer is safe beside nothing.** Gap coverage is `test-discipline`, run alone, on purpose.

**A standing security lane.** The correctness lane carries the obligation instead, invoking `engineering-paved-path:security` when the diff touches auth, input parsing, uploads, secrets, or a new outbound call with a caller-supplied destination. A fourth context reading the same diff for a subject that is a checklist rather than an open question is a lane that reports nothing on most runs — and a lane that reports nothing on most runs stops being read on the run where it matters.

**A plan verifier, and a runtime check.** Different questions, and the second one is a writer.

## What it will not do

| Not this | Why |
| :--- | :--- |
| Run a fixed set of reviewers | The lanes come from the change. That is the whole idea |
| Let reviewers edit anything | They propose; the orchestrator is the only writer, and only after every lane has returned |
| Run an upgrade or an `audit fix` | It would rewrite the lockfile mid-review, so every later lane describes a tree nobody chose |
| Fix a finding it does not believe | It says so and leaves it. An implementer told to fix a hallucinated blocker produces exactly the unrequested change a reviewer then objects to |
| Substitute for a lane whose plugin is missing | It says the lane did not run. Reviewing boundaries from memory in a lane labelled as the boundary review claims coverage it does not have |
| Commit, push, or open a pull request | Ending a review with a commit nobody asked for makes it irreversible before it has been read |

## Evals

Five behaviour cases under `evals/`, three of them refusals. See [evals/README.md](evals/README.md), including the note that `claude plugin eval` is currently early access.

## Dependencies

```
review-lenses@1.0.0
├── engineering-paved-path@^1.1.0     severity-scale, project-commands, security
└── architecture-review@^1.1.0        the reviewer the boundaries lane dispatches
    └── engineering-paved-path@^1.0.0
```

`^1.1.0` on both: `severity-scale` and `project-commands` arrived in `engineering-paved-path` 1.1.0, and the lane table in `architecture-review` 1.1.0 is what stops that agent and this plugin's reviewers reporting the same finding twice.

## Compatibility

Claude Code >= 2.1.110 — the floor for version-constrained plugin dependencies. **`git`**, for the diff every lane reviews.
