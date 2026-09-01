# Changelog

All notable changes to `change-docs`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `change-docs--v<version>`.

## [1.0.0] — 2026-08-29

First release. Two skills and an agent, generalised from a private monorepo's `.claude/` set.

### Added

- **`annotated-screenshots`**, with its overlay script. The idea it is built on: ask the running page
  for the element's own rectangle, rather than drawing boxes onto a saved image at estimated
  coordinates. The second approach looks correct while you author it and is wrong by a row when
  someone else reads it.

  Four traps ship with it, each producing an image that looks plausible and is wrong: a virtualised
  table whose off-screen rows are not in the DOM at all, a native `<dialog>` that sits above the
  maximum `z-index` because it is in the browser's top layer, full-page capture stitching a
  fixed-position overlay into repeated boxes, and a capture taken while the page is still animating.

- **`pr-description`**, vendor-neutral. The four-part shape with What before Why and numbered items
  so Why can point back, hard length limits, and a never-include list that is the longer half of the
  skill — because each item on it makes a description *feel* thorough while making it worse.

  Two operational rules came from real failures and are host-independent: never send a body through a
  shell heredoc (nested quoting has silently produced empty descriptions — write a file), and read the
  description back after sending it, because a successful-looking response can carry an empty body and
  is indistinguishable from success from the outside.

- **`doc-writer`**, defaulting to Drift. It fixes the sentences a change made false and changes
  nothing else, because it has no channel to ask which mode was wanted and Drift is the reversible
  one. It has no `Bash` on purpose, so it must be handed a diff rather than reconstructing one — a
  document written from a guess is worse than a stale one.

### Changed from the source workflow

- **The Jira and Bitbucket integrations did not come across.** They carried a hardcoded tenant URL, a
  real email address, a keychain service name and seven real reviewer usernames. What survived is the
  part that was never vendor-specific: the description discipline and the two write-safety rules,
  which now work with any host or with nobody at all.

- **The screenshot skill no longer defers to a ticket workflow** for where the files go. It writes
  them where it is told and reports absolute paths.

- **`doc-writer`'s placement table is gone.** It named one repository's documentation tree. It is
  replaced by a step that reads the existing tree first, and a rule against introducing a convention
  the repository does not already have.

### Removed from the source workflow

- Every example naming a real product, service or route.
- The "what this repository's docs actually are" section, which was a list of one repository's
  documentation debts.
