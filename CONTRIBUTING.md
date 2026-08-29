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

## The free checks

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

Two more run in the same job, and both are free because neither calls a model:

```sh
python3 plugins/agent-authoring/scripts/audit-harness.py plugins/
for s in plugins/*/scripts/selftest.sh; do bash "$s"; done
```

The audit checks whether the plugins still say true things about each other — a fan-out
table with no per-lane condition, a description promising a roster the body never
dispatches, a `plugin:name` in backticks that resolves to nothing. **That last one is the
rule the dependency graph is built on**: a backticked cross-plugin name is a promise it
resolves at install time, and this is the only check that catches one with no edge behind
it.

`build-index.py --check` also enforces a **search-payload budget**: it warns over 150 KB gzipped and
fails over 400 KB. **W108 is firing now, at exactly 150 KB.** CI stays green — it is a warning — but
it is a real item rather than noise.

The headroom went to three `sdd-engineering` agent bodies of 28, 27 and 20 KB, against the 10 KB this
repository budgets per agent. The fix is to move prose out of those three into reference files they
read on demand — **not** to delete it, and **not** to trim a doc, since all 39 doc sections together
are 29 KB of a 324 KB corpus. It is a behaviour change to three shipped agents and belongs in its own
pass with its own verification, not bundled into whatever change happens to cross the line.

The self-tests belong to plugins whose behaviour is a shell script rather than a prompt.
They are the whole of what is checkable for those, and they have already caught two real
bugs that reading the scripts did not.

## Run them before you push

```sh
git config core.hooksPath .githooks
```

Once per clone. `.githooks/pre-push` then runs all five before anything leaves the
machine — about a second in total, so there is no reason to reach for `--no-verify`. The
full site build stays in CI, and so do the behaviour evals.

The probes are the least obvious of them. `site/tests/queries.json` holds
natural-language questions and the artifact each must return; the docs are the search
corpus, so editing a doc can move the ranking and break one. That has already happened
twice — the second time when twenty components landed at once and a probe that was
passing at exactly its limit had no room left.

## The evals, which are not free

Every plugin carries behaviour cases under `evals/` — a `prompt.md` and a
`graders/criteria.md` per case, checking that a component stops where it is supposed to
stop rather than grading its prose.

```sh
scripts/run-evals.sh                            # every plugin that has cases
scripts/run-evals.sh review-lenses              # one
scripts/run-evals.sh --case 'verifier-*' review-lenses
scripts/run-evals.sh --changed-since origin/main
```

These call a model, so they live in their own workflow — `.github/workflows/evals.yml`,
triggered by hand from the Actions tab, or automatically on a pull request **for the
plugins that pull request touched**. Running every plugin's suite on every push costs
real money for changes that cannot have affected them.

It needs an `ANTHROPIC_API_KEY` repository secret. Without one — on a fork's pull request,
for instance — the job says so and runs the free self-tests instead. That is not a
failure.

**`claude plugin eval` is currently in early access.** On an account without it the
command exits 1 with `plugin eval is currently in early access`, which is indistinguishable
from a failing suite by exit code alone. `scripts/run-evals.sh` reads the message and
reports those plugins as *gated* rather than failed, because a red check nobody can turn
green teaches people to ignore the check.

Until access lands, the way to exercise a case is by hand:

```sh
claude --plugin-dir ./plugins/<name> -p "$(cat plugins/<name>/evals/<case>/prompt.md)" \
       --permission-mode plan --output-format text < /dev/null
```

then read the answer against that case's `graders/criteria.md`. Three cases run that way
so far, and each one found a real defect.

## Releasing

Bump `version` in `plugin.json` — nothing reaches existing users otherwise — then tag
from a clean tree on `main`:

```sh
claude plugin tag ./plugins/<name> --push
```

Rollback, renames and removals: [docs/releasing.md](docs/releasing.md).
