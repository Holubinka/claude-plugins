# Changelog

All notable changes to `engineering-paved-path`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `engineering-paved-path--v<version>`.

## [1.3.0] — 2026-08-29

Backward compatible: one skill arrives, carrying the half of a well-known set of principles that a
plugin can actually hold.

### Added

- **`scoped-change`** — build only what was asked, change only what you must, and say which reading
  you took when a request has two. Derived from four widely-circulated principles about how coding
  agents fail; two of the four were already covered here — clarification blocks for not guessing, and
  `verification-before-completion` for success criteria — so only the scope half is new.

  Its test for any line in a diff: **would this be here if the request had never arrived?**

  **The skill deliberately says what it cannot reach.** A skill fires on a request; over-building is
  an impulse. "Make it configurable" reaches it. The urge to add a factory while implementing
  something perfectly well-specified does not, because nothing in the request signals it. That half
  is always-on behaviour and belongs in the repository's own `CLAUDE.md`, so
  `skills/scoped-change/always-on.md` ships six lines to copy in — with the reasoning for why this
  marketplace does not inject them with a session-start hook the way some others do. A plugin that
  installs its opinions into every turn has taken a decision that belongs to whoever owns the
  repository.

  Wired into `refactor-safely:refactor-implementer` and `test-discipline:test-writer`, the two
  code-writing agents whose plugins could tighten their range for it without a major bump.

## [1.2.0] — 2026-08-29

Backward compatible: two skills arrive and six components stop restating one of them.

### Added

- **`verification-before-completion`** — *if you have not run the command in this turn, you cannot
  say it passes.* Six components were each carrying a piece of that rule in their own words:
  `project-commands`, `ts_diagnostic.py`, `implementer`, `plan-verifier`, `test-writer` and
  `testfix`. Where a dependency range allowed it, they now point here instead.

  Its load-bearing half is that a check has **three** outcomes rather than two. "Nothing found" and
  "nothing looked at" produce the same silence and mean opposite things — a linter with no files in
  scope, a suite that collected zero tests, a gate the repository never defined, each exits 0 and
  proves nothing. That is the same distinction `ts_diagnostic.py` was fixed for in 1.1.0, stated once
  where everything can reach it.

- **`systematic-debugging`** — *no fix before the cause is known.* Nothing in this marketplace owned
  debugging; `testfix` was the only component that touched it, and only to decide whether a test or
  the source was wrong.

  A change that removes a symptom without an explanation has either fixed the defect or moved it, and
  from the outside those look identical — the second being worse, because the next reader finds a bug
  with a comment above it saying it was handled.

  **It requires an observed symptom.** Reading code to judge whether it looks correct, with nothing
  having failed, is a review. That clause was added after a routing probe caught the skill firing on
  "is this function correct? I think the loop bounds are off by one" — a suspicion, not a defect.

### Changed

- **The trigger for `project-commands` is narrower**, after the same probe caught it firing on "why
  is `npm run build` running out of memory on my laptop but not in CI?" — a question about how a
  command behaves, not about which command to run. It now says so explicitly.

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
