# Changelog

All notable changes to `sdd-engineering`. This project follows [SemVer](https://semver.org/); the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `sdd-engineering--v<version>`.

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
