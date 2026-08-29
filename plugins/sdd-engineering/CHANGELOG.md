# Changelog

All notable changes to `sdd-engineering`. This project follows [SemVer](https://semver.org/); the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `sdd-engineering--v<version>`.

## [1.2.0] — 2026-08-29

Backward compatible: a fifth agent arrives, stage 4 gains a better reviewer, and two agents gain
paragraphs that were missing. No artefact shape changed, so a plan or a report from 1.1.0 still reads.

### Added

- **`insight-curator`** — the deliberate pruning pass `engineering-insights` has always assumed. That
  skill is append-only on purpose, because the session that finds an entry inconvenient is the one
  least qualified to remove it; **without a pruner, append-only becomes unbounded**, and a file long
  enough that nobody reads to the end has the same effect as an empty one at a higher cost.

  It proposes and stops, writing nothing until a human approves. Its rule is *verify before calling
  anything stale*, and it exists because the alternative has been measured: a command was cited in a
  repository's own conventions file and in an agent's prompt while existing in no manifest, and a false
  claim about a test framework spread to five files before anyone opened a test. **A claim repeated in
  several places is not corroborated — it is copied.**

- **`## Keep command output out of your context` in `implementer`.** One lint run over a large module
  returned 1 372 lines and four of them mattered. Redirect a gate to a file, read back the verdict.

  The rule that earns the section: **never pipe a gate through `tail`.** A pipeline's exit status is
  the last command's, and `tail` always succeeds — so `<gate> | tail -20` reports success with
  plausible-looking failure output underneath it. **The exit code is the verdict.**

- **The reason constraints are carried forward, in `implementation-planner`.** Every agent downstream
  starts with a fresh context window: a rule referenced by filename does not reach the implementer, it
  reaches a path the implementer may or may not open. That gap is silent — the plan looks complete, the
  implementer looks obedient, and the constraint was never in the room.

### Changed

- **Stage 4 now invokes `review-lenses:review-diff`** instead of dispatching two fixed reviewers. It
  picks only the lanes the change earned, and below two files and thirty lines it does not fan out at
  all. Every model-produced `critical` goes through an adversary first, where uncertain counts as
  refuted — so what reaches the fix rounds is one merged, ordered table of findings that survived a
  refutation attempt.

  `/code-review` is still worth running beside it on a feature. Two independent readers of one diff
  disagree usefully.

- **`fix-rounds.md` triages a report rather than reconciling several.** A finding under
  `## Attempted and refuted` does not enter triage at all — pulling one back in because it sounds
  plausible undoes the only stage that was trying to be wrong on purpose.

- **Gate discovery moved to `engineering-paved-path:project-commands`.** It was written twice here, in
  two different wordings, and three more components needed it. An agent prompt is paid on every
  dispatch; a skill body only when it fires.

### Dependencies

- **Added `review-lenses@^1.0.0`.** The graph is now four levels deep, and the shape is honest: this
  skill orchestrates a reviewer that orchestrates reviewers that read one shared severity definition.

- **`test-discipline` is deliberately not a dependency**, though `run-plan` §11 now names it in prose.
  §10 forbids dispatching a test writer from this pipeline, and **a dependency reads as permission** —
  declaring one on a plugin the skill may not dispatch is a contradiction in the manifest.

- **No existing range was tightened.** `architecture-review` stays at `^1.0.0` and resolves to 1.1.0 or
  newer by intersection through `review-lenses`. Tightening it directly is a major bump under this
  repository's own rules, for what is prose.

## [1.1.0] — 2026-08-29

Backward compatible: nothing was removed or renamed, and no dependency range moved. A spec
that already covered its goals is written exactly as before.

### Added

- **`spec-creator` will not finish a spec while a mandatory requirement has no acceptance
  criterion.** Every goal, and every user story stating something the feature must do, either
  carries a criterion or becomes a numbered open question with the spec reported as blocked.
  Non-goals are exempt — a boundary is not a requirement.

  It is a gate rather than a checklist line because of what happens downstream: the planner
  renumbers criteria into requirements and plans against those, and the verifier grades the
  plan. Neither reads the goals. A goal nobody wrote a criterion for is therefore approved by
  a human, built by nobody, and reported `MET` by every later stage.

- **A `## Coverage` line in the agent's report** — how many mandatory requirements the spec
  carries, and that each has a criterion, or which goal blocks it.

- **Three eval cases.** `spec-creator-requires-acceptance-criteria` covers the behaviour above.
  `sdd-does-not-fire-on-an-unrelated-request` and `workflow-retro-only-on-request` are the
  first negative cases in the suite: an expensive pipeline that fires on a one-line CSS fix is
  as broken as one that skips a gate, and only a negative case catches it.

## [1.0.1] — 2026-08-29

Patch: metadata only. No agent, skill or script changed behaviour, and no dependency range
moved.

### Added

- **`keywords` on every component.** The indexer reads them from a component's own
  frontmatter, which is a different field from the plugin manifest's `keywords`; without
  them the chips under every catalogue card were empty and the keyword facet had nothing
  to filter.

### Removed

- The `metadata.tags` lines three skills carried. The indexer never read that field, and
  two lists of the same concept drift on the next change. Their values are now in
  `keywords`.

## [1.0.0] — 2026-08-29

First release. Extracted from a private product repository and generalised: every path, module name, package-manager script and framework assumption specific to that codebase was replaced with either an explicit input or a discovery step.

### Added

- **Agents** — `spec-creator`, `implementation-planner`, `implementer`, `plan-verifier`.
- **Skills** — `run-plan` (the six-stage orchestrator, with `fix-rounds.md`), `workflow-retro` (with a bundled `stats.sh`), `engineering-insights`.
- **`scripts/write-gate.sh`** — the `PreToolUse` hook that confines `spec-creator` to the specs directory. Reads `specsDir` from `sdd.config.json` when present.
- **`sdd.config.json` support** — `specsDir`, `plansDir`, `modules`, `gates`, `scratchDir`, `reportLanguage`. All optional; the workflow runs in a repository with no configuration.
- **Six behaviour evals** under `evals/`, each testing a refusal rather than output quality.
- **Dependencies** on `engineering-paved-path@^1.0.0`, `research-tools@^1.0.0` and `architecture-review@^1.0.0`.

### Changed from the source workflow

- **Report language is English by default.** Section headings and verdict tokens (`MET`, `PARTIAL`, `NOT_MET`, `NOT_VERIFIED`, `critical`/`major`/`minor`/`note`) are fixed strings that never change language, because other stages key on them. Only the prose inside them follows `reportLanguage`.
- **EARS keywords are the standard English ones** — `WHEN`, `WHILE`, `IF … THEN`, `WHERE`, `shall`.
- **`implement` was renamed `run-plan`** and **`run-retrospective` was renamed `workflow-retro`**, once, at extraction. Renaming a skill after release is a major bump.
- **Empty-value sentinels are uniform**: `_None._` in both the spec and the plan, so a caller checks one string.
- **Gates come from the plan**, which takes them from `sdd.config.json`, the repository's scripts or its CI workflow. When none exists the planner writes `_None found._` and the implementer reports that the change could not be verified rather than inventing a command.
- **Architecture rules come from the repository**, not from the plugin. Where a repository states none, the skills apply their rules as a labelled proposal and `architecture-reviewer` reports the absence as its first finding.

### Removed from the source workflow

- `pr-self-review`, `test-writer` and `doc-writer` — each depended on scripts, hooks or gates specific to the source repository.
- Every hardcoded module name, package-manager script and dependency-cruiser rule name.
- Anecdote identifiers. The measurements they carried were kept; the spec and run identifiers that made them unreadable outside the source repository were not.
