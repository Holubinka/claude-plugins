# Changelog

All notable changes to `agile-delivery`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `agile-delivery--v<version>`.

## [1.1.0] — 2026-09-26

### Changed

- **`backlog-planning`** — a problem that blocks the release is a defect even when its parent is not
  in the current sprint; a bug is estimated only when it needs development effort, is sized in hours
  to a couple of days, and needs no parent — it links to the broken item when that is known and goes
  to the backlog unless it is urgent.

## [1.0.0] — 2026-09-25

First release. One skill, generalised from three internal delivery-process courses.

### Added

- **`backlog-planning`** — the work hierarchy from initiative to sub-task, the bug-versus-defect rule,
  four ways to split an item that will not fit a sprint, the story-point scale and who sets it, the
  Definition of Ready and Done, and the sprint habits that keep velocity and completion rate
  meaningful. Two reference files load on demand: `templates.md` (story, task, epic and initiative
  content, both checklists) and `sprints-and-metrics.md` (ceremonies, what counts at close, eight
  metrics and how to read them).

  The rule that earns the skill is **bug or defect is decided by the state of the parent, not by
  severity**. A defect sub-task attached to a closed story is on no board and in no sprint, and
  nothing reports that it is missing.

### Removed from the source material

- Every company name, project key, custom field, workflow status name and planning-block calendar.
  What survived is the part that holds in any tracker.
