# claude-plugins

A [Claude Code](https://claude.com/claude-code) plugin marketplace. Each plugin under
`plugins/` bundles skills, agents, commands or hooks that are worth carrying from one
project to the next.

The marketplace is named `dev-workbench` — that name is the `@suffix` you install with,
and it is independent of the repository name.

## Browse it

**<https://holubinka.github.io/claude-plugins/>**

Search every skill, agent, command, hook and doc in one box, in the words you would use
to ask for it — "a skill that reviews migrations" finds the skill. Each result says why
it matched, what it triggers on, what it costs in context, and what it does to your
machine. `⌘K` jumps anywhere from any page.

The site is generated from this repository on every push, so it cannot describe a plugin
that is not here or miss one that is.

## Use it

```sh
/plugin marketplace add Holubinka/claude-plugins
/plugin install <plugin>@dev-workbench
```

Add the marketplace over git (a GitHub `owner/repo`, a git URL, or a local path). Adding
it by a direct URL to `marketplace.json` will not work here: the plugin entries use
relative `./plugins/<name>` sources, which only resolve when the repository itself is
cloned.

## Develop

Load a plugin straight from the working tree, without installing it:

```sh
claude --plugin-dir ./plugins/<name>
```

Run `/reload-plugins` after each edit to pick up changes without restarting. Skills are
namespaced by plugin, so the skill `foo` in plugin `bar` is invoked as `/bar:foo`.

Validate before pushing — CI runs the same command:

```sh
claude plugin validate . --strict
```

While the catalogue is empty, `--strict` fails on the "no plugins defined" warning. Drop
the flag until the first plugin is registered; CI already does this automatically.

`claude plugin validate` does not notice components nested inside `.claude-plugin/`, a
manifest name that disagrees with its directory, an unregistered plugin, or a committed
credential — all of which fail silently. A second check covers those:

```sh
python3 scripts/lint-structure.py
```

A third covers the metadata the catalogue site is built from — a missing description, a
skill whose trigger overlaps another's, a release nothing tagged:

```sh
python3 scripts/build-index.py --check
```

A fourth asks whether the plugins still say true things about each other — a fan-out
table with no per-lane condition, a description promising a roster the body never
dispatches, a `plugin:name` in backticks that resolves to nothing:

```sh
python3 plugins/agent-authoring/scripts/audit-harness.py plugins/
```

All four are free, take about a second together, and run on every pull request alongside
the bundled `selftest.sh` scripts. The **behaviour evals are separate**, because they
call a model and cost money:

```sh
scripts/run-evals.sh                    # every plugin that has cases
scripts/run-evals.sh review-lenses      # one
```

They run from `.github/workflows/evals.yml` — by hand from the Actions tab, or on a pull
request for the plugins it touched, given an `ANTHROPIC_API_KEY` secret. `claude plugin
eval` is currently in early access; without it the runner reports those plugins as
*gated* rather than failed. [CONTRIBUTING.md](CONTRIBUTING.md#the-evals-which-are-not-free)
has the manual fallback.

Other useful commands: `claude plugin details <name>` (component inventory and token
cost), `claude plugin tag ./plugins/<name> --dry-run` (check the manifest and the
marketplace entry agree on the version).

## Add a plugin

Create `plugins/<name>/` with a `.claude-plugin/plugin.json`, put the components at the
plugin root, then register it in `.claude-plugin/marketplace.json`.
[CONTRIBUTING.md](CONTRIBUTING.md) has the full checklist.

## Docs

| Doc | Covers |
| :--- | :--- |
| [docs/plugin-structure.md](docs/plugin-structure.md) | Directory layout, manifest schema, dependency requirements |
| [docs/security.md](docs/security.md) | What a plugin may do, secrets policy, reviewing scripts and MCP servers |
| [docs/releasing.md](docs/releasing.md) | SemVer, tags, how updates reach users, rollback, renames |

> **Only `plugin.json` belongs in `.claude-plugin/`.** `skills/`, `agents/`,
> `commands/` and `hooks/` go at the plugin root. Nesting them under `.claude-plugin/`
> fails silently: the plugin installs with no components at all.

## Versioning

`version` lives in the plugin's `plugin.json` and nowhere else. Bump it on every
release — users only receive an update when it changes. Marketplace entries deliberately
omit `version` so the two can never drift apart.

## Layout

```
.claude-plugin/marketplace.json   the catalogue — a plugin does not exist until it is listed here
plugins/<name>/                   one folder per plugin
scripts/                          the two checks and the site's indexer
site/                             the catalogue site, deployed to GitHub Pages on every push
```
