# Changelog

All notable changes to `research-tools`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `research-tools--v<version>`.

## [1.1.0] — 2026-08-29

Backward compatible: the report gains a section, and nothing else about it changed. A caller
that reads the existing headings is unaffected.

### Added

- **`researcher` closes every report with `## Cost`** — files opened, searches run, pages
  fetched. Counts of work actually done in the turn, never estimates.

  Whoever dispatched the agent is deciding whether to dispatch another, and the shape of the
  last one is the only evidence they have. A question answered from two files and a question
  answered from forty are different questions, and only the agent can tell them apart
  afterwards.

  Two rules travel with it, because a number a report must print is a number something will
  eventually be tempted to make look good: **do not open a file in order to have something to
  count**, and do not stop short of an answer to keep the figure low. A cheap wrong answer is
  the expensive one.

- **An `evals/` suite** — one case that the section is present and truthful, one negative case
  that a single-file question stays a single-file question. This also closes the `W103` the
  catalogue reported against this plugin.

## [1.0.1] — 2026-08-29

### Added

- `keywords` on the `researcher` agent, so the catalogue can facet on them.

## [1.0.0] — 2026-08-29

First release. The `researcher` agent, generalised from a private product repository.
