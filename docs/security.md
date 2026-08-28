# Permissions, secrets and scripts

A plugin is not data. It is code and instructions that Claude follows with your user
privileges: a hook can pipe file contents anywhere, a skill can tell Claude to make a
change you did not ask for, an MCP server can proxy every tool call through a process
you do not control. Anthropic does not vet what a third-party marketplace ships, so the
review below is the only gate this repository has.

Treat a plugin the way you treat an npm dependency: read it before you trust it.

## What a plugin may do here

| Capability | Policy |
| :--- | :--- |
| Skills, agents, output styles | Allowed. Prose only. |
| Hooks | Allowed, but justify the event in the PR. Prefer a skill (see below). |
| `scripts/` executables | Allowed. Must be reviewed line by line. |
| MCP servers | Allowed. Credentials must come from `userConfig` or the environment. |
| Network calls at install or session start | Not allowed without an explicit note in the PR description. |
| Reading files outside the project or `${CLAUDE_PLUGIN_DATA}` | Not allowed. |
| Committed credentials of any kind | Never. |

### Prefer a skill over a hook

A skill is loaded when Claude decides it is relevant; its body costs tokens only when it
fires. A hook runs on **every** matching event whether or not it helps, and its cost is
paid on every exchange. Use a hook only when the value is in the automatic reaction
itself — formatting after an edit, blocking a write — and say so in the PR.

`claude plugin details <name>` prints the always-on and on-invoke token cost. Include the
numbers in the PR when adding anything that loads eagerly.

## Secrets

**Never commit a credential.** `scripts/lint-structure.py` scans for GitHub, Anthropic,
OpenAI, AWS and Slack token shapes and private-key blocks (`E006`), but it only catches
known formats — it is a backstop, not the policy.

Take secrets from one of two places:

**1. A `userConfig` field marked `sensitive`.** Claude Code prompts the user once and
stores the value in the OS keychain, not in the repository:

```json
{
  "name": "deploy-kit",
  "userConfig": {
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "Token for the deployment API",
      "sensitive": true
    }
  }
}
```

Reference it as `${user_config.api_token}` in MCP and LSP configs and in hook commands,
or read `CLAUDE_PLUGIN_OPTION_API_TOKEN` from the environment inside a script.

Shell-form hook commands reject `${user_config.*}` substitution — use the exec form with
`args`.

**2. The user's own environment**, read at run time by the script. Document the variable
name in the plugin README.

If a secret is ever committed, rotate it first and rewrite history second. Removing it in
a later commit does nothing: the value stays reachable in the history and in every clone.

## Reviewing scripts

Before approving a PR that adds or changes anything under `scripts/`, or any hook
command, check each of these:

- **Read the whole script.** Not the diff — the file. A small diff can arm code that was
  already there.
- **No `curl … | sh`**, no downloading and executing anything at run time. Everything a
  plugin executes must be visible in the repository.
- **No absolute paths.** `${CLAUDE_PLUGIN_ROOT}` for bundled files, `${CLAUDE_PROJECT_DIR}`
  for the user's project. The linter enforces this in config files (`E005`); scripts are
  on you.
- **Quote every expansion.** `"${CLAUDE_PLUGIN_ROOT}"/scripts/x.sh`, not bare. Paths
  contain spaces.
- **Hook input is untrusted.** It arrives as JSON on stdin and contains file paths and
  content the user or Claude produced. Parse it with `jq`; never interpolate it into a
  shell command.
- **Bounded side effects.** A hook that writes outside the project directory, installs
  packages, or calls the network needs an explicit justification in the PR.
- **Exit codes are the contract.** A hook that exits non-zero blocks the tool call. Make
  sure that is intended and that failure modes are not silent.

## Reviewing MCP servers

- Pin the server version — an unpinned `npx <pkg>` fetches whatever is published today.
- Credentials via `${user_config.*}` or the environment, never inline in `.mcp.json`.
- Note in the PR which external service the server reaches and what it sends there.

## Trust boundaries when consuming

This marketplace resolves its own plugins by relative path, so what users get is exactly
what is in this repository at the commit they fetched.

- Pin external plugin sources to a `sha`, not a branch, so unreviewed upstream commits
  cannot reach users automatically.
- Auto-update is off by default for third-party marketplaces. Leave it off unless you
  have a reason.
- Adding a name to `allowCrossMarketplaceDependenciesOn` grants that marketplace the
  right to have its code installed automatically. Review it as you would this one.

## Reporting a problem

Do not open a public issue for a suspected credential leak or a malicious plugin. Contact
the repository owner directly, and rotate anything exposed before anything else.
