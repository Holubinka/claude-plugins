---
name: project-commands
description: "Finds which command this repository uses to typecheck, lint or run its tests, when the task did not name one. Use when a script name from another project comes to mind, when choosing between npm, pnpm, yarn and bun, when a command failed with a missing-script error, when writing the gates section of a plan, and before reporting that a change could not be verified automatically. It answers which command to run — not why a command behaves as it does, which is ordinary debugging and not this."
metadata:
  version: "1.0.0"
keywords: [commands, discovery, gates, package-manager, monorepo]
---

# Project commands — discovered, never assumed

A command typed from habit is a guess wearing the costume of a fact. `npm test` in a pnpm
workspace, `pytest` in a repository that runs `tox`, `yarn lint` where the script is called
`check` — each fails in a way that reads like a broken repository rather than a wrong guess,
and each wastes a turn proving something that was never true.

**The rule this skill exists for:**

> You may run a script whose definition you have read.
> You may never run a script whose existence you are guessing at.

`pnpm test` typed without opening `package.json` is a guess. `pnpm test` typed after reading
`"test": "vitest run"` and seeing `pnpm-lock.yaml` at the root is a discovered command. They
look identical in the transcript. Only one of them is evidence.

## Three lanes, discovered independently

**Typecheck, lint and test are separate questions.** A repository may define one and not the
others, and finding a test command tells you nothing about whether a lint command exists.
Resolve each on its own, and stop at the first source that yields a command.

| # | Source | Why it ranks here |
| :--- | :--- | :--- |
| 1 | **The task itself** — a plan's `## Gates`, a fix brief, the dispatch prompt | Someone already decided. Use it character for character; do not substitute an equivalent |
| 2 | **A convention file** — `CONTRIBUTING.md`, `TESTING.md`, `AGENTS.md`, `CLAUDE.md`, a module `README.md` | A documented workaround beats the bare form. If the docs say `--runInBand` on this machine, that is the command |
| 3 | **The CI workflow** — `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `.circleci/config.yml` | The only place a command is *proven* to work: it executes on every push |
| 4 | **The manifest's script table**, for the language actually present | Real, but a name is not a definition — see below |
| 5 | **Nothing found** | Then that lane has no command. This is a valid answer |

Step 5 is not a failure state. Say which of the four sources you read and that each was empty.
Do not invent a command, do not install anything, and do not run a package-manager script on
the chance that it exists. A gate reported green that was never earned is worse than a gate
reported missing.

[`discovery-order.md`](discovery-order.md) carries the per-language key tables, the lockfile
map, and what to read in a workspace where the root and the package disagree.

## The runner prefix is discovered too

Resolve it from the lockfile at the repository root — `pnpm-lock.yaml` → `pnpm`, `yarn.lock` →
`yarn`, `bun.lock`/`bun.lockb` → `bun`, `package-lock.json` → `npm`, none → `npm`.

**Two lockfiles is a finding, not a coin toss.** Use whichever `packageManager` in
`package.json` names. If that field is absent, say the repository is ambiguous and stop —
picking one silently means every command you report afterwards may have run against a
different dependency tree than the one CI uses.

## Two rules that keep the answer honest

**A script key that exists is not a command that runs.** `"test": "echo no tests && exit 0"`
is real, common, and exits 0. So is a `typecheck` script that only covers one workspace, and a
`lint` that has `--max-warnings=9999` pinned to it. Read the script's *value* before treating
its exit code as evidence, and quote the value when you report the gate.

**Report a discovered command as discovered.** Name the lane, the command, and which of the
five sources produced it:

```
typecheck: pnpm -r typecheck        (package.json scripts, pnpm-lock.yaml at root)
lint:      _none found_             (read: dispatch, CONTRIBUTING.md, .github/workflows, package.json)
test:      npx vitest run           (.github/workflows/ci.yml:31)
```

A reader can then tell the difference between *this repository has no lint gate* and *nobody
looked*. Those are different facts, and only one of them is a reason to stop worrying.

## Where this rule is also implemented in code

Two shipped scripts obey it without a model in the loop, and each carries a comment naming
this skill as the source:

- `engineering-paved-path`'s `ts_diagnostic.py` — discovers TypeScript sources rather than
  assuming `src/`, resolves the runner from the lockfile, and prints `not scanned` where it
  looked at nothing. A missing directory and an empty result are not the same outcome.
- `hook-guardrails`'s `scoped-lint-fix.sh` — resolves one formatter for one file from config
  presence, and exits silently when none resolves.

If you change the rule here, those two are what has to change with it.
