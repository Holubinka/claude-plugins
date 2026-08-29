# research-tools

Two read-only agents for questions that need an answer someone can check. One is thorough, one is cheap, and picking the wrong one is the main way to waste tokens here.

```sh
/plugin install research-tools@dev-workbench
```

## Which of the two

| | `investigator` | `researcher` |
| :--- | :--- | :--- |
| Question shape | **structural** — what connects to what | **subject** — how does this work, and why |
| Output | a trace: hops with `path:line` citations | a report: findings, evidence, confidence, and what it could not establish |
| Reaches the network | no | yes — `WebSearch` and `WebFetch` |
| Model / effort | haiku, low | sonnet, medium |
| Always-on cost | 94 tokens | 100 tokens |
| Body, paid when it fires | 1 435 | 2 346 |

*"Which modules break if I change this exported type"* is `investigator`, however large the answer turns out to be. *"How does this authentication flow actually work, and when did it change"* is `researcher`. **The line between them is the shape of the question, never its difficulty.**

Each names the other and will decline out of its lane rather than grow into it — `investigator` stops and says the question needs research instead of producing something that looks like a report; `researcher` names `investigator` on a purely structural question rather than answering it for ten times the tokens.

## `researcher` — two modes, and it tells you which one it answered

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

## `investigator` — the map before the grep

**A grep finds imports. It does not find the edges no import carries**, and those are the ones that cost a session when they are missed: a producer and its consumer joined only by a routing key, two services joined by a generated client neither reads at runtime, a shared library whose change reaches dependents named in no import you are looking at, a value injected at a composition root and never referenced by name where it is used.

So it looks for the repository's own map first — an architecture document, the workspace manifest, a module's `CLAUDE.md` — uses it as an **index**, and then confirms the specific fact against current code. Where the two disagree, the code is right and it says the map has drifted. Where no map exists, it says so once and searches.

Its output is fixed and small:

```
Answer:   <one to three sentences>
Trace:    <path:line> — <what it establishes>
Edges:    <each cross-module hop, with its transport>
Caveats:  <what a map claimed that the code did not confirm>
```

Three hops or more and it adds a mermaid diagram, carrying three conventions of its own: a dashed edge for a queue or event hop labelled with its routing key, every node a real name from the code, and the trace cited beneath the fence. Never *instead of* the citations — a diagram is the one place a wrong detail reads as authoritative, because it looks like it came from a tool.

## Dispatching them

```
Use the research-tools:researcher agent to find out how <X> works in this repository.
Use the research-tools:investigator agent to trace what reaches <Y>.
```

`sdd-engineering`'s `spec-creator` dispatches `researcher` by name while writing a specification's sources section. Both work on their own — neither has any dependency on the SDD workflow.

**Neither can hold a conversation.** Output goes back to whoever dispatched it, so when the request is ambiguous `researcher` returns a `## Clarification needed` block *as its whole output* and stops, having done no research. That block ends with what it would assume if you just say "go ahead", so the answer can be one word.

## What they will not do

| Not this | Why |
| :--- | :--- |
| Write or edit any file | Neither has `Write` or `Edit`, and both are told not to route around that with Bash |
| Run a mutating shell command | Bash is for `git log`, `git blame`, `rg`, `ls`, `cat` — not `>`, `sed -i`, `rm`, `git commit`, or any package-manager script |
| Spawn subagents | Everything they report, they found themselves |
| Propose code changes | Someone else decides what to do with what they found |
| Trust a language server's "no references found" | Cross-package navigation is broken or incomplete in enough toolchains that a negative from it is not evidence. `investigator` confirms a negative with a text search |

`researcher` never cites a URL it did not actually open — a search snippet for a page that would not load goes under what it could not establish, with the URL, so you can try it yourself.

## Output language

English by default. The section headings are emitted verbatim and stay English in every case — they are the structure a caller keys on. Ask for another language in the dispatch and the prose inside those headings follows.

## Evals

Four behaviour cases under `evals/`. See [evals/README.md](evals/README.md), including the note that `claude plugin eval` is currently early access.

## Dependencies

None. Both agents carry everything they need in their own prompts — including `investigator`'s diagram conventions, which are stated inline rather than borrowed from a skill in another plugin. A backticked name is a promise this plugin would then have to keep at install time, and neither agent needs one.

## Compatibility

Claude Code >= 2.1.110.
