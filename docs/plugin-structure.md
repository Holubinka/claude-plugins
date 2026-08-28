# Plugin structure, manifest and dependencies

Everything a plugin in this marketplace must look like. For the release process see
[releasing.md](releasing.md); for what a plugin is allowed to do see
[security.md](security.md).

## Directory layout

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json        # the manifest — and nothing else in this directory
├── skills/<skill>/SKILL.md
├── agents/<agent>.md
├── hooks/hooks.json
├── scripts/               # helper executables (not bin/)
├── .mcp.json
├── .lsp.json
└── README.md
```

> **Only `plugin.json` goes in `.claude-plugin/`.** Component directories nested there
> are never discovered — the plugin installs with zero components and
> `claude plugin validate` reports nothing. `scripts/lint-structure.py` catches this
> (`E001`); it is the single most common way to ship a broken plugin.

The directory name must equal the manifest `name` (`E004`). That name is the skill
namespace: a skill `foo` in plugin `bar` is invoked as `/bar:foo`.

### Where components live

| Component | Default path | Manifest field | Overriding the field… |
| :--- | :--- | :--- | :--- |
| Skills | `skills/<name>/SKILL.md` | `skills` | **adds to** the default scan |
| Agents | `agents/<name>.md` | `agents` | **replaces** the default |
| Commands | `commands/<name>.md` | `commands` | **replaces** the default |
| Workflows | `workflows/` | `workflows` | **replaces** the default |
| Output styles | `output-styles/` | `outputStyles` | **replaces** the default |
| Hooks | `hooks/hooks.json` | `hooks` | merges |
| MCP servers | `.mcp.json` | `mcpServers` | merges |
| LSP servers | `.lsp.json` | `lspServers` | merges |
| Monitors | `monitors/monitors.json` | `experimental.monitors` | **replaces** the default |

The replace-versus-add distinction bites: setting `"agents": ["./extra/x.md"]` stops
`agents/` from being scanned at all. If you need both, list both.

Prefer `skills/` over `commands/` — flat command files are the legacy form.

## Manifest

`plugins/<name>/.claude-plugin/plugin.json`. Only `name` is strictly required; this
repository additionally expects `description`, `version`, `author` and `license`.

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

Use `https://json.schemastore.org/claude-code-plugin-manifest.json` as `$schema`. The
`anthropic.com/claude-code/*.schema.json` URLs that circulate are 404s.

`description` is what the marketplace listing shows, so write it for someone deciding
whether to install.

### Skills

```markdown
---
description: Use when the user asks to ...
---

Instructions to Claude, not documentation for a human.
```

The frontmatter `description` is the **only** thing Claude sees when deciding whether to
load the skill. Write it as a trigger condition, not a summary. The body is injected
into the conversation once the skill fires, so it costs tokens on invocation — keep it
tight and push detail into sibling files the skill can read on demand.

### Referencing bundled files

Use `${CLAUDE_PLUGIN_ROOT}` — never an absolute path. Plugins install into
`~/.claude/plugins/cache`, so `/Users/you/...` works only on your machine. The linter
rejects absolute paths in hook, MCP and LSP configs (`E005`).

`${CLAUDE_PLUGIN_DATA}` is a persistent per-plugin directory
(`~/.claude/plugins/data/<id>/`) for caches and installed dependencies. It is deleted
when the plugin is uninstalled from its last scope.

Avoid a top-level `bin/`: it is incompatible with distribution through claude.ai
organization settings. Put executables in `scripts/` (`W003`).

## Dependencies

A plugin may depend on other plugins. Declare them in the manifest:

```json
{
  "name": "deploy-kit",
  "version": "3.1.0",
  "dependencies": [
    "audit-logger",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}
```

A bare string tracks whatever version the marketplace provides. An object takes `name`,
a semver `version` range (`~2.1.0`, `^2.0`, `>=1.4`, `=2.1.0`), and optionally
`marketplace`.

**Requirements for this repository:**

- **Constrain anything you rely on behaviourally.** An unconstrained dependency tracks
  latest, so an upstream release can change a tool name under you without warning.
- **The dependency must be tagged.** Constraints resolve against git tags named
  `{plugin-name}--v{version}` on the repository hosting the dependency — for a
  relative-path plugin like ours, this repository. An untagged dependency resolves to the
  marketplace's current copy, and a constrained one fails with `no-matching-tag`. See
  [releasing.md](releasing.md).
- **Pre-releases are excluded** unless the range opts in (`^2.0.0-0`).

### Cross-marketplace dependencies

Depending on a plugin in another marketplace is blocked by default, so that one
marketplace cannot silently pull in code from a source you have not reviewed. To allow
it, the **root** marketplace — the one hosting the plugin being installed — lists the
target:

```json
{
  "name": "dev-workbench",
  "allowCrossMarketplaceDependenciesOn": ["acme-shared"]
}
```

Trust does not chain: only the root marketplace's allowlist is consulted. Treat adding a
name here as a security decision and review the target marketplace first.

### How constraints interact

When several installed plugins constrain the same dependency, Claude Code intersects the
ranges and installs the highest version satisfying all of them. Incompatible ranges
(`~2.1` against `~3.0`) fail the second install with `range-conflict` and leave the
first plugin untouched. Widen the range in a new release rather than pinning with `=`,
which freezes the dependency for everyone who installs your plugin.

### Testing a plugin with its dependency

```sh
claude --plugin-dir ./plugins/my-dependency --plugin-dir ./plugins/my-plugin
```

The local copy satisfies the dependency entry without installing from a marketplace, and
version constraints are not checked against it.

### Dependency errors

| Error | Meaning |
| :--- | :--- |
| `dependency-unsatisfied` | Dependency not installed, or installed but disabled. |
| `dependency-version-unsatisfied` | Installed version is outside the declared range. |
| `no-matching-tag` | No `{name}--v*` tag satisfies the range. |
| `range-conflict` | Two plugins' ranges cannot be combined. |
| `cross-marketplace` | Target marketplace is not in `allowCrossMarketplaceDependenciesOn`. |

`claude plugin list --json` reports these in an `errors` field. Claude Code disables the
affected plugin until the error is resolved.

Enabling a plugin enables its dependencies; disabling one is refused while another
enabled plugin still needs it. `claude plugin prune` removes auto-installed dependencies
that nothing requires any more.
