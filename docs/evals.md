# Specification for the eval suites

What an eval case in this repository must be, how it is graded, how many times it runs, and what
a result is allowed to claim. Normative: **MUST** is a rule a case has to satisfy to be merged,
**SHOULD** is a default with a stated reason to depart from it.

Scope is the automated suites under `plugins/*/evals/`.
[measuring.md](measuring.md) covers the complementary question — judging a component on real work,
by hand. [COST-BASELINE.md](COST-BASELINE.md) covers whether a change made a run cheaper.

## Where the rules come from

Two sources, and they disagree in one place worth knowing about.

**Anthropic's own guidance for agent evals** sets the shape: start with 20–50 tasks drawn from
real failures rather than waiting for hundreds, because early on "each change to the system often
has a clear, noticeable impact, and this large effect size means small sample sizes suffice";
prefer deterministic graders and reach for a model grader only where necessary; and **"it's often
better to grade what the agent produced, not the path it took"**, so that a creative valid
solution is not penalised.

**The wider field** adds that outcome-only scoring "hides why an agent succeeded or failed", so
trajectory-aware evaluation is needed alongside it; that LLM-as-judge alone is insufficient for
agentic systems; and that most eval failures come from underspecified criteria rather than bad
prompts.

**The disagreement, and how this repository resolves it.** Grading the path penalises valid
routes; grading only the product misses *how* it got there, which for these plugins is the entire
subject — every component here is defined by what it refuses.

> **Grade the constraint, never the route.**
>
> "Did not edit a source file", "did not run an upgrade", "did not dispatch a lane the change did
> not earn" are constraints: violating one is a defect on any route. "Read the plan, then opened
> the diff, then ran the gate" is a route, and a case MUST NOT require it.

A constraint is falsifiable by inspection and does not care how the agent arrived. That keeps the
Anthropic rule intact while still scoring the thing these plugins exist for.

## Current state, measured

Not aspirational — this is what `plugins/*/evals/` contains today.

| Measurement | Value | Against |
| :--- | ---: | :--- |
| Cases | 43 | 20–50 recommended to start ✅ |
| Negative cases | 19 (44%) | balance required; single-sided evals cause one-sided optimisation ✅ |
| Numbered criteria | 183 | — |
| Plausibly script-checkable | 29 (15%) | "deterministic where possible" ❌ |
| Highest skill-trigger overlap (static) | 0.136 | warns at 0.55 ✅ |
| Median trigger overlap (static) | 0.029 | — |
| Trigger routing, behavioural | 7/7 recall · 6/6 precision | over 13 probes ⚠️ small |
| Calibration examples | 0 | "a judge that doesn't agree with humans on a small labeled set is not a judge" ❌ |
| Cases sourced from an observed failure | 3 | "drawn from real failures" ❌ |

The two ❌ rows and the thin third are the work items at the end of this document.

**The two trigger rows say different things, and the gap between them is the point.** Lexical
distance of 0.136 against a 0.55 threshold looks like plenty of room. It is not evidence of correct
routing: interference is a runtime property, and only a behavioural run measures it.

`scripts/trigger-probe.sh` is that run. Its first pass scored 5/5 and 3/3 — which under §6.2 means
the probe set was too easy, not that routing was proven, because the negatives were nowhere near
the skills they were meant to tempt. Rewriting them as *adjacent* negatives produced a false fire
immediately: `project-commands` loaded for **"Why is `npm run build` running out of memory on my
laptop but not in CI?"** — a question about how a command behaves, not about which command to run.

That was a real defect in the description, which carried *"when about to run a build… command"* and
*"or a CI reproduction"* — two clauses loose enough to catch anything CI-adjacent. Narrowing it, with
an explicit "not why a command behaves as it does", closed the false fire without costing the
positive. **The static score could not have found it**, and the easy probe set did not.

Thirteen probes is still under the 20–50 the guidance asks for, and every one was written by the
author of the skills. Treat the current 7/7 and 6/6 as *the set has stopped producing signal again*,
and the next move is harder negatives rather than a claim about routing.

## 1 — Case design

**1.1** A case MUST be one `prompt.md` plus one `graders/criteria.md`. The prompt carries every
environment fact the grader depends on; a grader MUST NOT depend on a fact the prompt did not
state.

**1.2** A case MUST satisfy the **two-readers test**: two people who know the domain, reading the
criteria independently, reach the same pass/fail verdict. A case that fails this is a broken case,
not a failing component.

**1.3** Criteria MUST be numbered, each opening with a bold assertion, and the file MUST contain
the sentence `The response passes only if **all** of the following hold.`

**1.4** Every case MUST state what a **pass** looks like at its edge — the near-miss that is
still acceptable, or the plausible-looking answer that is not. Most eval failures are
underspecified criteria; the edge is where the underspecification lives.

**1.5** Negative cases MUST be at least 40% of a plugin's suite. Testing only that a behaviour
occurs optimises in one direction, and for these components the refusals *are* the product.

**1.6** New cases SHOULD be sourced from an observed failure — a real run that went wrong — in
preference to one imagined while writing the component. A case written by the author of the
component tests the author's imagination; a case written from a transcript tests the component.

**1.7** A case MUST NOT require a specific sequence of tool calls, file reads, or steps. See
*grade the constraint, never the route*.

## 2 — Graders

**2.1** A criterion that a script can decide MUST be decided by a script, not by a judge.
Deterministic checks are reproducible, free, and immune to judge drift. The current suite is at
15%, which is too low.

Criteria that are script-decidable in this repository, and MUST be moved as the harness allows:

- no file outside a named set was created or modified
- a required section heading is present, spelled exactly
- output contains a `path:line` anchor
- a command's exit code was captured rather than piped away
- no dependency was installed and no manifest changed
- a named file is unchanged from its pre-run content

**2.2** A model grader MUST grade **one dimension**, not several. One judge per criterion beats
one judge for the whole rubric.

**2.3** A model grader MUST be able to answer *unknown*. A judge with no way out hallucinates a
verdict, and an invented verdict is worse than an abstention because it is indistinguishable from
a real one.

**2.4** A model grader SHOULD state its reasoning before its score. Score-first ordering invites
rationalisation of a number already chosen.

**2.5** Graders MUST be calibrated before their verdicts are quoted. Calibration is a small set of
responses labelled pass/fail by hand, run through the grader, with the disagreements read. **A
judge that does not agree with a human on that set is not a judge**, and a suite built on one
measures nothing.

Minimum: five labelled responses per plugin, at least two of them near the pass/fail edge.

## 3 — Runs and thresholds

**3.1** Every case MUST declare which of two questions it asks, because they need different
statistics:

| Question | Metric | Passes when | Use for |
| :--- | :--- | :--- | :--- |
| Can it do this at all? | `pass@k` | at least one of `k` runs succeeds | capability — a positive case |
| Does it do this every time? | `pass^k` | **all** `k` runs succeed | **every refusal case** |

At `k=1` the two are identical; by `k=10` they diverge sharply. A refusal that holds four times in
five is not a boundary — it is a tendency, and the fifth run is the one that ships the defect.

**3.2** Refusal cases MUST be scored `pass^k` with `k ≥ 3`.

**3.3** A result quoted anywhere MUST be a median of at least three runs. One run is a story; two
that agree are an untested coincidence.

**3.4** A run's threshold is `1.0`. Partial credit MAY be used for a multi-part positive case, and
MUST NOT be used for a refusal — a boundary is held or it is not.

## 4 — Environment

**4.1** Each trial MUST start clean. Shared state between runs — a leftover file, a cached result,
a fixture a previous case wrote to — produces correlated failures that read as component defects.

**4.2** A fixture MUST NOT be modified by a case. Where a case needs to write, it writes to a copy.

**4.3** A fixture MUST make the shape it is testing load-bearing, and say so in its own README.
`two-runner-repo` documents its conventions nowhere except in its own files precisely because a
component carrying a runner table would get exactly half of that case right.

## 5 — Cost accounting

**5.1** Cost MUST be reported per **successful** completion, not per run. Cost per run rewards
failing fast.

**5.2** Token spend SHOULD be normalised before models are compared, since output is priced
several times input and cache reads are a fraction of it:

```
effective = model_multiplier × (1.0 × new_input + 0.1 × cache_read + 4.0 × output)
```

**5.3** `reread_ratio` MUST be reported alongside any cost claim. A multi-agent run's bill is
re-reading context, not producing output — one measured run produced 386 k output tokens against
477 M cache-read — so an optimisation that cuts output and leaves re-reading alone has changed
nothing that matters.

**5.4** Every suite run MUST carry `--max-cost-usd`. A run without a ceiling is one bad case away
from an unbounded bill.

## 6 — Maintenance

**6.1** Transcripts MUST be read, not just scores. A grader's own mistakes are invisible in its
output and obvious in the transcript, and this is ongoing work rather than one-time setup.

**6.2** A suite where everything passes MUST be treated as **saturated**, not as healthy. It has
stopped producing signal. The response is harder cases or a new dimension — never a celebration.

**6.3** When a real failure is found outside the suite, a case reproducing it MUST be added in the
same change that fixes it. Three of the current cases exist because of failures found by hand this
way; they are the most valuable in the suite.

**6.4** A case that has never failed in twenty runs and was not sourced from a real failure SHOULD
be deleted. It is costing money to confirm something nothing threatens.

## Work items, in order

Numbered by what unblocks what, not by size.

1. **Calibrate the graders.** Five labelled responses per plugin, disagreements read and the
   criteria adjusted. Until this is done, no pass rate from this suite may be quoted. *(Section 2.5,
   currently 0.)*
2. **Convert the 29 script-decidable criteria** to deterministic checks. They are the cheapest and
   most reliable half of the suite and are currently being paid for on every run. *(2.1, currently
   15%.)*
3. **Declare `pass@k` or `pass^k` per case**, and set `k ≥ 3` on all 19 refusal cases. *(3.1–3.2,
   currently undeclared.)*
4. **Source the next ten cases from transcripts**, not from imagination. *(1.6, currently 3 of 43.)*
5. **Grow the probe set past 20**, weighted toward adjacent negatives, and source the requests from
   real sessions rather than from the author. `scripts/trigger-probe.sh` and
   `scripts/trigger-probes.tsv` exist and pass at 13 probes, which per §6.2 means they need to get
   harder — not that routing is settled. *(Current state table.)*
6. **Add the cost fields** to the runner's JSON output so 5.1–5.3 can be reported at all.

## Sources

- [Demystifying evals for AI agents — Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [LLM Agent Evaluation Metrics in 2026: Tool Calling, Task Completion, Reasoning, and Trace-Based Evals — Confident AI](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide)
- [LLM Evaluation Framework: Trajectories vs. Outputs — LangChain](https://www.langchain.com/resources/llm-evaluation-framework)
- [LLM-as-a-Judge in 2026: evaluation techniques and best practices — DeepEval](https://deepeval.com/blog/llm-as-a-judge)
- [SkillJuror: Measuring How Agent Skill Organization Changes Runtime Behavior](https://arxiv.org/pdf/2606.11543)
- [GroundEval: A Deterministic Replacement for LLM-as-Judge in Stateful Agent Evaluation](https://arxiv.org/pdf/2606.22737)
- [Key metrics for evaluating token efficiency in AI systems — Glean](https://www.glean.com/perspectives/key-metrics-for-evaluating-token-efficiency-in-ai-systems)
- [Evaluating AI agents: real-world lessons from building agentic systems at Amazon — AWS](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/)
