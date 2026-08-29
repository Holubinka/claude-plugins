# Changelog

All notable changes to `hook-guardrails`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `hook-guardrails--v<version>`.

## [1.0.0] — 2026-08-29

First release. Two hooks, generalised from a private monorepo's `.claude/` set.

### Added

- **`block-protected-push`** — a `PreToolUse` hook on `Bash` that refuses a push landing on a
  protected branch.

  It catches two shapes, and the second is why it exists. An explicit `git push origin main` is easy
  to see. A **bare `git push` whose upstream silently resolves to `main`** is not: branching with
  `git checkout -b feature origin/main` sets the upstream to `main`, so a later plain `git push` lands
  there with nothing in the command text to grep for. The command is correct and the destination is a
  fact about the repository, which is exactly the class of mistake a prompt cannot prevent.

  It matches `git push` only at a command start or after a separator, so `echo "git push origin main"`
  is not refused. A hook that refuses harmless commands is one people turn off.

- **`scoped-lint-fix`** — a `PostToolUse` hook that formats **only the file just edited**. Never the
  package, never the repository. A whole-project format run triggered by a one-line edit has
  previously touched unrelated files and required a revert, and the damage is invisible in the
  moment: the tool reports success and the diff only grows later.

  The formatter is discovered from configuration that is present, per
  `engineering-paved-path:project-commands`. If none resolves it exits silently — a formatter invented
  on the spot reformats a file to a style the repository does not use.

- **`scripts/selftest.sh`** — eighteen cases in a throwaway repository, covering both hooks.

  It found two real bugs during development, and both are the reason it ships rather than being run
  once: the formatter went through the package runner in a project where only the `.bin` shim existed,
  and the project root fell back to the working directory outside a git repository — which would have
  formatted a file to the rules of whatever project the session happened to be in. Neither was
  visible by reading the script.

### Changed from the source workflow

- **Both hooks fail open.** The originals were wired into one repository's settings and could assume
  their dependencies. A published hook cannot: refusing every Bash command because `jq` is missing
  makes the plugin unusable, and a hook people disable protects nothing.

- **Three visible escape hatches** — `HOOK_PROTECTED_BRANCHES`, `HOOK_ALLOW_PROTECTED_PUSH`,
  `HOOK_SKIP_LINT_FIX`. The push hook had none. A gate with no escape hatch gets deleted the first
  time it is wrong during an urgent push, and an override nobody can see is worse than no gate.

- **The formatter is discovered rather than hardcoded.** The original ran `eslint --fix` and
  `prettier --write` unconditionally, which is right for the repository it was written in and wrong
  everywhere else.

- **The protected branch list is configurable and no longer names a company-specific branch.**

### Removed from the source workflow

- The four hooks that only make sense with a stage-marker and verdict protocol this marketplace does
  not ship: the read-only stage guard, the chain gate, the stop-turn verifier and the pre-commit
  warner. Each reads a file written by an orchestrator that would have to ship with it.
