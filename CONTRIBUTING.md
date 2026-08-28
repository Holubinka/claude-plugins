# Contributing

Reference docs, split by what you are doing:

| Doc | Covers |
| :--- | :--- |
| [docs/plugin-structure.md](docs/plugin-structure.md) | Directory layout, manifest schema, dependency requirements |
| [docs/security.md](docs/security.md) | What a plugin may do, secrets policy, reviewing scripts and MCP servers |
| [docs/releasing.md](docs/releasing.md) | SemVer, tags, how updates reach users, rollback, renames |

## Add a plugin

**1. Create the directory.** Kebab-case; it becomes the skill namespace, so keep it
short — users type `/<name>:<skill>`.

```sh
mkdir -p plugins/<name>/.claude-plugin
```

**2. Write the manifest** at `plugins/<name>/.claude-plugin/plugin.json`. `name` must
match the directory.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
  "name": "<name>",
  "description": "One line on what it does and when it fires.",
  "version": "0.1.0",
  "author": { "name": "Vitalii Holubinka" },
  "license": "MIT",
  "keywords": []
}
```

**3. Add the components** at the **plugin root** — `skills/<skill>/SKILL.md`,
`agents/<agent>.md`, `hooks/hooks.json`, `.mcp.json`. Nothing but `plugin.json` goes in
`.claude-plugin/`; nesting a component directory there fails silently and the plugin
installs empty. Full layout, the add-versus-replace rules for manifest path fields, and
skill authoring are in [docs/plugin-structure.md](docs/plugin-structure.md).

**4. Register it** in `.claude-plugin/marketplace.json` under `plugins`:

```json
{
  "name": "<name>",
  "source": "./plugins/<name>",
  "description": "Same line as the manifest — this is what the listing shows.",
  "category": "development",
  "keywords": ["..."]
}
```

Do not put `version` here. It belongs in `plugin.json` only, so the two cannot drift —
see [docs/releasing.md](docs/releasing.md).

**5. Test and check.**

```sh
claude --plugin-dir ./plugins/<name>    # /reload-plugins after each edit
claude plugin validate . --strict
claude plugin validate ./plugins/<name> --strict
python3 scripts/lint-structure.py
python3 scripts/build-index.py --check
```

`claude plugin eval ./plugins/<name>` scores eval cases from `plugins/<name>/evals/`
against a no-plugin baseline. `claude plugin details <name>` reports the token cost.

## The three checks

`claude plugin validate` covers JSON syntax, manifest fields, skill frontmatter, and
version drift between a marketplace entry and a manifest.

`scripts/lint-structure.py` covers what it misses, all of which fail silently at install
time:

| Code | |
| :--- | :--- |
| `E001` | Component directory nested inside `.claude-plugin/` |
| `E004` | Manifest `name` disagrees with the directory name |
| `E005` | Absolute path in a hook, MCP or LSP config instead of `${CLAUDE_PLUGIN_ROOT}` |
| `E006` | Committed credential |
| `E007` | Marketplace entry points at a directory that does not exist |
| `E008` | Plugin directory not registered in the marketplace |
| `W003` | Top-level `bin/` (blocks claude.ai organization distribution) |
| `W004` | Marketplace entry declares a version |

`scripts/build-index.py --check` covers the metadata the catalogue site needs — the
things that leave a plugin installable but unfindable, or findable but unreadable:

| Code | |
| :--- | :--- |
| `E101` | Description missing, or under 40 characters |
| `E102` | Marketplace entry description disagrees with `plugin.json` |
| `E103` | Registered plugin exposes zero components |
| `E104` | Search payload over its gzipped ceiling |
| `E105` | A manifest, hook, MCP or LSP config is unreadable or invalid JSON |
| `W101` | Fewer than two `keywords` |
| `W102` | No plugin `README.md` |
| `W103` | No `evals/` directory |
| `W104` | Skill description reads as a summary, not a trigger condition |
| `W105` | Version has no matching `<plugin>--v<version>` tag |
| `W106` | Unconstrained dependency |
| `W107` | Two skill descriptions overlap above the collision threshold |
| `W108` | Search payload over the single-file budget |
| `W109` | No tag satisfies a constrained dependency (`no-matching-tag`) |

All three run in CI on every pull request. Errors fail the build; warnings do not.

## Run them before you push

```sh
git config core.hooksPath .githooks
```

Once per clone. `.githooks/pre-push` then runs the two linters and the search probes
before anything leaves the machine — under a second in total, so there is no reason to
reach for `--no-verify`. The full site build stays in CI.

The probes are the least obvious of the three. `site/tests/queries.json` holds
natural-language questions and the artifact each must return; the docs are the search
corpus, so editing a doc can move the ranking and break one. That has already happened
once.

## Releasing

Bump `version` in `plugin.json` — nothing reaches existing users otherwise — then tag
from a clean tree on `main`:

```sh
claude plugin tag ./plugins/<name> --push
```

Rollback, renames and removals: [docs/releasing.md](docs/releasing.md).
