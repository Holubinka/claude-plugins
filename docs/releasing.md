# Versioning, tags, updates and rollback

## SemVer

Every plugin carries a semver `version` in its `plugin.json`, and **only** there. The
marketplace entry deliberately omits `version`: when both declare one, `plugin.json`
wins at install time and the entry is silently ignored, so the entry can drift out of
date while looking authoritative. `claude plugin validate` warns about the mismatch and
`scripts/lint-structure.py` warns about the entry declaring a version at all (`W004`).

| Change | Bump |
| :--- | :--- |
| Skill or agent wording that changes behaviour, new component, new dependency | minor |
| A skill's trigger `description` narrowed or widened | minor |
| Removing a component, renaming a skill, tightening a dependency range | major |
| Typo, formatting, README, a fix that changes no behaviour | patch |

Renaming a skill is a **major** change: users invoke it as `/plugin:skill`, and the old
name stops working.

Nothing reaches users until `version` changes. A commit without a bump is invisible to
anyone who already installed the plugin.

## Tagging a release

Releases are tagged `{plugin-name}--v{version}`. The prefix lets one repository host
several plugins on independent version lines.

```sh
claude plugin tag ./plugins/<name> --dry-run   # check first
claude plugin tag ./plugins/<name> --push
```

The command derives the tag from the manifest and, before creating it, validates the
plugin, checks that `plugin.json` and the marketplace entry agree on the version,
requires a clean working tree under the plugin directory, and refuses if the tag already
exists. `--push` pushes to `origin`; without it the command prints the `git push` to run.

`git tag <name>--v<version>` by hand is equivalent, but skips every one of those checks.

**Tags are not optional if anything depends on the plugin.** Dependency version
constraints resolve against these tags. An untagged plugin has no versions to resolve, so
a constrained dependency on it fails with `no-matching-tag`.

## Release checklist

1. Bump `version` in `plugins/<name>/.claude-plugin/plugin.json`.
2. Update the plugin's `README.md` if behaviour changed.
3. `claude plugin validate . --strict` and `python3 scripts/lint-structure.py`.
4. Merge the PR.
5. `claude plugin tag ./plugins/<name> --push` from a clean tree on `main`.

## How users receive an update

Auto-update is **off by default** for third-party marketplaces like this one, so most
users update deliberately:

```sh
claude plugin update <name>          # then /reload-plugins
```

Users who enable auto-update in `/plugin` get the new version on a background refresh
after session start, with a prompt to run `/reload-plugins`. The running session keeps
the version it launched with either way.

`claude plugin marketplace update dev-workbench` refreshes the catalogue without
installing anything — needed before installing a plugin published since the last refresh.

## Rollback

Pick by blast radius.

**One user, right now** — reinstall at a known-good tag:

```sh
claude plugin uninstall <name>
claude plugin install <name>@dev-workbench
```

**Everyone, immediately** — revert the plugin directory on `main` and republish with a
*higher* version. Do not re-release the broken number: users who already have it will
never be offered the same version again.

```sh
git revert <bad-commit>
# set version to the next patch above the bad one, e.g. 2.3.1 -> 2.3.2
claude plugin tag ./plugins/<name> --push
```

Never force-move a published tag to a different commit. Anyone who already installed
keeps the old content, and the two populations silently diverge. Claude Code partly
guards against this — a tag-resolved install caches under a directory keyed by commit
SHA, so a moved tag produces a fresh cache rather than stale content — but the version
number then means two different things.

**A dependency broke you** — narrow the range in your own plugin and release a patch.
Constraints are intersected across everything installed, so widening someone else's is
not yours to do.

## Renaming or removing a plugin

Deleting or renaming an entry gives everyone who installed it a `plugin-not-found`
error. Record the change in `renames` in `.claude-plugin/marketplace.json`:

```json
"renames": {
  "old-name": "new-name",
  "removed-plugin": null
}
```

A name mapped to a string is loaded under the new name, with a notice, and the user's
settings are rewritten. A name mapped to `null` is dropped and reported as removed.

`renames` is **append-only history**. Claude Code follows chains to the final
destination, so entries from earlier renames must stay forever. Never edit or delete an
existing key.
