# Changelog

All notable changes to `architecture-review`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `architecture-review--v<version>`.

## [1.1.0] — 2026-08-29

Backward compatible: the agent looks harder and says more about what it walked past. Its subject,
its severity anchors and its report shape are unchanged, and its dependency range is unchanged —
nothing here needs anything newer than it already required.

### Added

- **An adversarial stance.** The agent now aims to surface at least three candidate boundary
  problems before concluding a target is clean.

  **Three is how hard you look, not how many you file.** A first pass that finds one thing and stops
  has usually stopped at the first thing, and the boundary problems worth having are rarely the most
  visible ones. The existing counterweight is restated in the same breath and is not weakened: an
  empty findings table is a valid result, and three candidates that all turn out to be correct code
  produce a report with zero findings and a full checked-and-clean section.

  Written with its three exclusions attached, because an instruction to look harder invites all
  three: it is not a quota, not a reason to widen the subject, and not a reason to grade harder.

- **Two more rows in the lane table**, for uncovered behaviour and for dependency findings, and a
  paragraph on running as one lane of several. The agent names another lane's subject when it walks
  past one, without grading it and without assuming that lane ran — and where it is the only lane, it
  says so under `## Not covered` rather than widening its subject to compensate.

  The lanes are named as **roles, not as plugin identifiers**. A backticked cross-plugin name is a
  promise this plugin would have to keep at install time, and this agent is useful on its own.

- **An `evals/` suite**, with a fixture that has no architecture rules at all. This closes the `W103`
  the catalogue reported against this plugin.

  Two of the three cases are refusals. That ratio is deliberate: this agent's value is as much in
  what it declines to say as in what it finds, and the release that told it to look harder is exactly
  the release that needed a case fixing a target with nothing to find.
