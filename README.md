# claude-plugins

A [Claude Code](https://claude.com/claude-code) plugin marketplace. Each plugin under
`plugins/` bundles skills, agents, commands or hooks that are worth carrying from one
project to the next.

## Use it

```sh
/plugin marketplace add Holubinka/claude-plugins
/plugin install <plugin-name>@claude-plugins
```

## Add a plugin

1. Create `plugins/<name>/` with a `.claude-plugin/plugin.json`:

   ```json
   {
     "name": "<name>",
     "description": "One line on what it does and when it fires.",
     "version": "0.1.0"
   }
   ```

2. Put its content in the folders the plugin loader reads — `skills/<skill>/SKILL.md`,
   `agents/<agent>.md`, `commands/<command>.md`, `hooks/hooks.json`.
3. Register it in `.claude-plugin/marketplace.json` under `plugins`, with a `source`
   pointing at the folder:

   ```json
   {
     "name": "<name>",
     "description": "Same line, this is what the marketplace listing shows.",
     "source": "./plugins/<name>",
     "category": "code-review"
   }
   ```

4. Verify before pushing: `claude plugin validate .`

## Layout

```
.claude-plugin/marketplace.json   the catalogue — a plugin does not exist until it is listed here
plugins/<name>/                   one folder per plugin
```
