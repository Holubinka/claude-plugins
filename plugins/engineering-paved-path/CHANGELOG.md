# Changelog

All notable changes to `engineering-paved-path`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `engineering-paved-path--v<version>`.

## [1.1.0] — 2026-08-29

Backward compatible: two skills arrive, one trigger description widens, and one bundled script
stops reporting a false clean. Nothing that existed was renamed or removed.

### Added

- **`project-commands`** — the rule for finding the command a repository actually uses to
  typecheck, lint or test, instead of guessing one.

  This was already written down twice, in two different wordings, inside two agent prompts in
  `sdd-engineering`, and three more components were about to need it. An agent prompt is paid
  on every dispatch; a skill body is paid only when it fires, which is why the duplication was
  the first candidate named in [docs/COST-BASELINE.md](../../docs/COST-BASELINE.md).

  The one line it exists to enforce: **you may run a script whose definition you have read; you
  may never run a script whose existence you are guessing at.** Finding nothing is a valid
  answer, and the skill says which sources it read rather than inventing a command.

- **`severity-scale`** — `critical` / `major` / `minor` / `note`, defined by what each level
  stops rather than by how bad it feels.

  Six components arriving in this marketplace grade findings on this scale. Copying the
  definition into each of them is exactly the duplication this plugin exists to prevent, so it
  lives here once and they depend on it. It carries the two rules that make a model-produced
  finding safe to act on — deterministic findings outrank model-produced ones and may not be
  downgraded, and a model-produced `critical` must survive an adversarial pass in which
  *uncertain counts as refuted*.

- **An `evals/` suite.** This also closes the `W103` the catalogue reported against this plugin.

### Fixed

- **`ts_diagnostic.py` reported a false clean in any repository without a top-level `src/`.**
  Three of its checks grepped a hardcoded `src/` with stderr suppressed, so a missing directory
  and an empty result printed the same green tick — *zero* `any` usages and *zero* unsafe
  assertions, for a codebase full of both.

  It now discovers the sources (tsconfig's `include`/`files`, then `git ls-files`, then a walk),
  and every check has a third outcome: `not scanned`, which is never a pass. It also stops
  piping `tsc` through `head`, which discarded the exit code that *was* the verdict, and it
  routes through the package runner only when TypeScript is a project dependency — `npx tsc`
  against a global-only install exits 1 with a banner that reads exactly like a type error.

- **`typescript-expert` told agents to run `npm run` and `npx` as if they were universal.** It
  now points at `project-commands` and shows discovered forms as illustrations rather than as
  commands to type. This one contradicted a promise made in `sdd-engineering`'s own README.

- **Four unread frontmatter keys removed from `typescript-expert`** (`category`, `risk`,
  `source`, `date_added`) — provenance residue from an imported skill that no indexer reads.

### Changed

- **`security`'s trigger description no longer names React, Express, MongoDB and JWT.** The
  description is the always-on line that decides whether the skill fires at all, and naming one
  stack narrowed it on every other. The guidance was never stack-specific; only the samples
  were, and they now say so.

- **`frontend-architecture`'s examples no longer describe one real product.** The route tree,
  the component names and the domain types came from the repository this skill was extracted
  from. Two of them were phrased as rules about where hooks live rather than as examples, which
  is the version of this problem that actually misleads a reader.

- **Nothing here names a skill that is not installed.** Three references to unreleased framework
  skills became prose. A backticked name is a promise, and a promise with nothing behind it
  sends a reader looking for a file that does not exist.
