# research-tools

One read-only agent, `researcher`, for questions that need an answer someone can check.

```sh
/plugin install research-tools@dev-workbench
```

## What it is for

Two kinds of question, and it will tell you which one it answered:

- **Mode A — the repository.** How does this actually work here? What is wired and what is only scaffolded? When did this change, and why?
- **Mode B — the outside world.** What do the docs, the spec, the changelog and the issue tracker say about this library, version or standard?

Ask it something that spans both and it returns both reports under one shared short answer, because *what the repository would not tell you* is a different failure from *what the internet would not*.

## The rule that makes the output worth reading

**A finding it cannot address to a `path:line` or to a URL it opened is not a finding.** It goes under a confidence label, or into `## What I could not establish` — a section that is never omitted. If everything was found, that section says so in one line.

Findings and evidence stay in separate sections: no links among the findings, no new claims among the evidence. That split is what lets you check the work without re-doing it.

Every finding carries `high` / `medium` / `low`:

| Label | Means |
| :--- | :--- |
| `high` | direct evidence says it |
| `medium` | it follows from evidence, but nothing states it |
| `low` | the best reading of incomplete information |

## Dispatching it

```
Use the research-tools:researcher agent to find out how <X> works in this repository.
```

`sdd-engineering`'s `spec-creator` dispatches it by that name while writing a specification's sources section. You can also use it on its own — it has no dependency on the SDD workflow.

**It cannot hold a conversation.** Its output goes back to whoever dispatched it, so when the request is ambiguous it returns a `## Clarification needed` block *as its whole output* and stops, having done no research. That block ends with what it would assume if you just say "go ahead", so the answer can be one word.

## What it will not do

| Not this | Why |
| :--- | :--- |
| Write or edit any file | It has no `Write` and no `Edit`, and it is told not to route around that with Bash |
| Run a mutating shell command | Bash is for `git log`, `git blame`, `rg`, `ls`, `cat` — not `>`, `sed -i`, `rm`, `git commit`, or any package-manager script |
| Spawn subagents | Everything it reports, it found itself |
| Propose code changes | Someone else decides what to do with what it found |

It has `WebSearch` and `WebFetch`, so Mode B reaches the network. It never cites a URL it did not actually open — a search snippet for a page that would not load goes under what it could not establish, with the URL, so you can try it yourself.

## Output language

English by default. The section headings are emitted verbatim and stay English in every case — they are the structure a caller keys on. Ask for another language in the dispatch and the prose inside those headings follows.

## Dependencies

None.

## Compatibility

Claude Code >= 2.1.110.
