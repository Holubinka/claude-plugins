# architecture-review

One agent, `architecture-reviewer`, that answers a single question: **which boundary did this change cross, and does it still hold?**

```sh
/plugin install architecture-review@dev-workbench
```

Installing this also installs `engineering-paved-path`, which carries the two architecture skills the agent reads its rules from.

## What makes it different from a general review

It reviews **boundaries and nothing else** — ring placement, dependency direction, ports and their adapters, the composition root, the shape of data crossing a boundary, module cohesion, and the Server/Client line in frontend code.

Everything else it walks past, it hands to whoever owns it and does not grade:

| Not its subject | Whose |
| :--- | :--- |
| Injection, auth, secret handling | a security review |
| Naming, formatting, file length | a conventions or lint pass |
| A logic bug, a race | `/code-review`, and the tests |
| An N+1, a missing index | `/code-review` |

That restraint is the design. A performance note dressed as an architecture finding reaches a reader who cannot act on it — which is the same outcome as saying nothing, minus the space it took.

## It learns your rules before it looks for violations

**This agent does not arrive with a list of rules to enforce.** Its first step is to find out what this repository actually decided, in this order:

1. **An automated boundary gate** — `.dependency-cruiser.cjs`, `eslint-plugin-boundaries`, `import/no-restricted-paths`, an Nx or Turbo graph constraint, an ArchUnit-style test. It reads the rules, runs the gate once read-only, and then **never re-reports what the gate already decides**, because repeating a machine-checkable finding buries the ones only a human can make.
2. **Architecture documentation** — `docs/architecture*.md`, `ARCHITECTURE.md`, an architecture section in `AGENTS.md` or `CLAUDE.md`, a module `README.md`, an ADR directory.
3. **A written contract** — a shared types module whose header states what may depend on it.

Then it invokes the matching skill from `engineering-paved-path` — `onion-architecture` for backend work, `frontend-architecture` for frontend — *before* reviewing, never after.

**If the repository states no architecture rules at all, that is its first finding**, and it reviews only what is visible from the code itself. It will not import rules from the skills and report them as yours. A rule invented on the spot and reported as the repository's own is worse than no rule: the next reader obeys it believing someone decided it.

## Every finding carries two axes

Severity, and `introduced` versus `pre-existing`, decided from `git diff` against the base rather than from intuition about which code looks newer.

Without that second axis a reader cannot tell whether a finding blocks the change in front of them or belongs on a backlog, and every finding reads as an accusation.

| Severity | The boundary |
| :--- | :--- |
| `critical` | Gone, not bent — and nothing else stops it |
| `major` | Holds structurally, but the shape crossing it does not |
| `minor` | Broken in one place while the same slice already does it right elsewhere |
| `note` | Nothing forbids it yet; worth the next reader knowing |

Severity is the least reproducible thing any reviewer produces, so the agent carries an explicit tie-break: **does the fix need a decision, or only an edit?** One default parameter with no call-site changes is `minor` even when the rule it breaks is important. Changing what two rings promise each other is `major` even when the edit is small. That rule is written down because it was measured — the same finding scored `major` on one run and `minor` on the next.

**Read `critical` and `major` as "look at this", not as a grade.** Nothing should threshold on them automatically.

## Dispatching it

```
Use the architecture-review:architecture-reviewer agent to review the boundaries in <diff | module | path>.
```

Give it a diff, a module or a path. If the target resolves to no files, or "this change" has no base to diff against, it returns a `## Clarification needed` block as its whole output and stops — ending with what it would assume if you just say "go ahead".

`sdd-engineering`'s `run-plan` skill dispatches it at stage 4, in parallel with `/code-review`. It works equally well on its own against a branch or a PR.

## What it returns

```
## What was reviewed      — targets, diff base, which rule sources exist, gate result
## Findings               — table: # | severity | introduced/pre-existing | path:line | rule | what does not hold
## Checked and clean      — which boundaries held, and why. Never omitted
## Uncertain observations — no rule under them; not counted as findings
## Not covered            — what was left unreviewed, or "nothing"
```

**An empty findings table is a valid result** and is returned as one, with the checked-and-clean section filled in. The agent is told not to pad the table, not to invent a "considerations" list, and not to issue a verdict, a score or an approval — it describes, and someone else decides.

It writes nothing to disk. `Write` and `Edit` are absent from its tool list; the rest of the restraint is a rule it keeps rather than a wall.

## One scheduling constraint

**Do not run it beside an agent that mutates the working tree.** A test-writing agent that proves a test can fail leaves a deliberate defect in the tree between mutating a file and reverting it, so any file read or gate run inside that window describes the mutation rather than the branch. The agent cannot detect a sibling from the inside; if the tree shifts under it, it reports that under `## Not covered` instead of reporting what it saw.

## Dependencies

`engineering-paved-path@^1.0.0` — for `onion-architecture` and `frontend-architecture`, which are where its architectural rules come from.

## Compatibility

Claude Code >= 2.1.110 — the floor for version-constrained plugin dependencies.
