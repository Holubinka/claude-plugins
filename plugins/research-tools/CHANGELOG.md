# Changelog

All notable changes to `research-tools`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `research-tools--v<version>`.

## [1.2.0] — 2026-08-29

Backward compatible: a second agent arrives and `researcher` gains one section naming it. Nothing
about `researcher`'s report shape changed, so a caller reading its headings is unaffected.

### Added

- **`investigator`** — a cheap structural tracer. One question in, a compact trace out: hops with
  `path:line` citations, the transport on each cross-module edge, and what a map claimed that the
  code did not confirm. Haiku at low effort, roughly an order of magnitude below `researcher`.

  The idea it is built on: **a grep finds imports, and the edges that cost a session are the ones no
  import carries** — a producer and its consumer joined only by a routing key, two services joined
  by a generated client neither reads at runtime, a value injected at a composition root and never
  referenced by name where it is used. So it reads the repository's own map first, uses it as an
  index, and then confirms the fact against current code. A map that has drifted is worse than no
  map, which is why nothing it reports rests on the map alone.

- **`## Boundary with research-tools:investigator` in `researcher`.** Each agent now names the other
  and declines out of its lane. A purely structural question reaching `researcher` gets one line
  naming `investigator` rather than a report costing ten times as much; a research question reaching
  `investigator` stops rather than growing into something that looks like a report and is not one.

  Without this the pair is worse than either alone, because the cheap agent is only cheap when it is
  the one that gets dispatched.

- **Two eval cases** covering the new agent — that it returns a trace rather than a file dump, and
  the negative case that it declines a question that is not structural.

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
