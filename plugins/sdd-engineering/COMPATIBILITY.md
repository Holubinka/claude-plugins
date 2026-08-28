# Compatibility

## Minimum

**Claude Code >= 2.1.110.**

That floor is set by **version-constrained plugin dependencies**: this plugin declares
`engineering-paved-path@^1.0.0`, `research-tools@^1.0.0` and `architecture-review@^1.0.0`, and
constraint resolution against git tags is what earlier versions do not have. On an older release
the dependencies either resolve to whatever the marketplace currently holds or fail outright.

Developed and exercised on 2.1.251.

## Features this plugin uses, and what each needs

| Feature | Used by | Note |
| :--- | :--- | :--- |
| Version-constrained plugin dependencies | the manifest | Sets the >= 2.1.110 floor |
| Namespaced cross-plugin skill and agent references | all four agents | `engineering-paved-path:onion-architecture`, `research-tools:researcher`, `architecture-review:architecture-reviewer` |
| `skills:` in agent frontmatter | `implementation-planner` | Preloads two skills on the dispatch path. **Verify this field accepts a plugin-scoped name in your version** — if it does not, the skills are still reachable with `Skill`, and the frontmatter line is the only thing to drop |
| `hooks:` in agent frontmatter | `spec-creator` | A `PreToolUse` hook live only while that subagent runs |
| `${CLAUDE_PLUGIN_ROOT}` | `spec-creator`'s hook command | Resolves to the installed plugin directory |
| `${CLAUDE_SKILL_DIR}` | `workflow-retro` | Resolves to the skill's own directory, for `stats.sh` |
| `${CLAUDE_PROJECT_DIR}` | `write-gate.sh` | The user's repository root, for reading `sdd.config.json` |
| `SendMessage` to a finished subagent | `workflow-retro`, `run-plan` | Resuming an agent that still holds its context |
| `Agent` tool `model` override | `run-plan` fix rounds | Beats the agent file's frontmatter for one dispatch |
| `/code-review` | `run-plan` stage 4 | Built in; not a dependency |

## External tools

| Tool | Needed by | If missing |
| :--- | :--- | :--- |
| `git` | `plan-verifier`, `architecture-reviewer`, `implementer` | The `introduced` / `pre-existing` axis and the report stamp both stop working |
| `jq` | `scripts/write-gate.sh` | The gate refuses **every** write and says why. That is the correct failure direction, but `spec-creator` cannot proceed |
| `rg` | most agents | They fall back to `grep`, more slowly |

## Not required

- No MCP server.
- No network access. `spec-creator`, `implementation-planner`, `implementer` and `plan-verifier`
  have neither `WebSearch` nor `WebFetch`. Only `research-tools:researcher`, in the dependency
  plugin, reaches the network — and only when dispatched.
- No particular language, framework, package manager or test runner. Where the repository has
  none of these configured, the workflow says so rather than assuming one.

## Early access

`claude plugin eval` — needed to run the suite under `evals/` — is in early access. Without it
enabled the command exits without running anything, and the cases' schema is unverified. Nothing
else in this plugin depends on it.
