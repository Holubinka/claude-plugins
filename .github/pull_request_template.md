## What and why

<!-- One paragraph. What does this add or change, and what problem does it solve? -->

## Type

- [ ] New plugin
- [ ] Change to an existing plugin
- [ ] Docs / tooling only

## Checks

- [ ] `claude plugin validate . --strict` passes
- [ ] `python3 scripts/lint-structure.py` passes
- [ ] Loaded locally with `claude --plugin-dir ./plugins/<name>` and the components actually fire

## Plugin changes

<!-- Delete this section for docs/tooling-only PRs. -->

- [ ] `version` bumped in `plugin.json` per [docs/releasing.md](../docs/releasing.md)
      (nothing reaches existing users without it) — **old → new:**
- [ ] Components are at the plugin root, not inside `.claude-plugin/`
- [ ] Bundled files referenced with `${CLAUDE_PLUGIN_ROOT}`, no absolute paths
- [ ] New or changed dependencies carry a version range, and the upstream is tagged
- [ ] Plugin renamed or removed? `renames` updated (append-only)

**Context cost** — paste `claude plugin details <name>`:

```
```

## Security

<!-- See docs/security.md. Answer both, even if the answer is "none". -->

- [ ] No credentials committed; secrets come from `userConfig` (`sensitive`) or the environment

**Scripts, hooks or MCP servers added or changed?** If yes, describe what each executes,
what it touches outside the plugin directory, and why a hook is needed rather than a
skill:

**Network access at install or session start?** If yes, name the host and what is sent:
