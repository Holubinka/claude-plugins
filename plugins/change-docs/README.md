# change-docs

Everything a change needs after it works: a picture of it, a description of it, a ticket that says what to do and how to check it, and the sentences elsewhere that it just made false.

```sh
/plugin install change-docs@dev-workbench
```

Installing this pulls in `engineering-paved-path`, for the diagram conventions `doc-writer` uses.

## What is in it

| Component | For | Always-on | On invoke |
| :--- | :--- | ---: | ---: |
| `annotated-screenshots` (skill) | Showing a UI change instead of describing it | ~150 | ~1.5k |
| `pr-description` (skill) | The short four-part body a reviewer actually needs | ~130 | ~1.9k |
| `ticket-description` (skill) | A ticket that says what to do, then test steps and screenshots once the PR is open | ~130 | ~1.5k |
| `doc-writer` (agent) | Fixing the documentation a change falsified | ~120 | ~1.6k |

Figures are the estimates from `claude plugin details`. The components are independent, with one exception: `ticket-description` takes its screenshots with `annotated-screenshots`.

## `annotated-screenshots` — the callouts land on real coordinates

It injects a small overlay into the **running page** and asks the browser for the element's own rectangle, so a box goes exactly where the button is. The alternative — drawing boxes onto a saved image at estimated coordinates — looks correct while you are authoring it and is wrong by a row when someone else reads it.

Works with any browser automation that can evaluate a script and save a screenshot: a DevTools MCP server, Playwright, Puppeteer. Nothing in it is specific to one.

Five traps have their own reference file, because each produces an image that looks plausible and is wrong:

| Trap | What happens |
| :--- | :--- |
| A virtualised table | Rows outside the visible window are not in the DOM at all. The query returns nothing and the annotation silently does not happen |
| A native `<dialog>` | It lives in the browser's top layer, above `z-index: 2147483647`. There is no value that wins, and an hour disappears into finding that out |
| Full-page capture | A fixed overlay does not survive stitching — the boxes repeat at the wrong offsets |
| A page still moving | A capture during a transition catches the element mid-flight. Wait for settled, not for present |
| A scripted click on a library component | `el.click()` from a script opens nothing on a dropdown or dialog that listens for pointer events. The script reports success and the next frame is of the wrong state |

Two rules do most of the work: **at most two or three callouts per image**, and **read the image back after writing it**. The second is the step that is easiest to skip and the one that catches everything.

**The colour is always red** — boxes, arrows and label chips, with white label text. It is not picked per page, so every screenshot on a ticket or a PR reads as one set.

## `pr-description` — a short fixed shape and a long list of what to leave out

```
**What** — two or three bullets, one line each.
**Why** — one sentence.
**Test** — what was actually verified, and how.
**Risk** — what could go wrong, and what would show it first.
```

**What comes before Why.** A reviewer reads *what* to decide whether to read at all; a *why* that arrives first is context for something they cannot picture yet.

About ten lines, fifteen at most. If What needs a fourth bullet, the diff should have been two. **Nothing is hard-wrapped** — one sentence is one line, because hosts render a single newline as a visible break.

Test steps and screenshots do not go in the PR. They go on the ticket, through `ticket-description`.

The never-include list is the longer half of the skill — a file-by-file summary, the commit log, diff statistics, per-suite test counts, raw tool output, narration of the process. **Each of these makes a description feel thorough while making it worse**, which is why they survive everywhere.

Two operational rules that came from real failures, and are vendor-neutral because both hosts have the same shape:

- **Never send a body through a shell heredoc.** Write it to a file and have the tool read the file. Nested quoting has silently produced empty descriptions.
- **Read the description back after sending it.** A successful-looking response can come back with an empty or truncated body, and from the outside it is indistinguishable from success. On an update, fetch first and send every other field back verbatim — most update APIs replace the whole object, so an omitted field is cleared, not left alone. Reviewers and labels have been lost by an update that only meant to fix a typo.

The skill produces the text and holds the approval gate. It does not talk to a host, so it works with `gh`, with a self-hosted server's REST API, or with you pasting it.

## `ticket-description` — what to do, then how to check it

A ticket is written in two moments.

**When it is created**, it says what to do: an imperative title and two to four lines, plus a one-line link to the plan if there is one. The plan carries the detail, so the ticket never restates its steps, file names or acceptance criteria — two copies drift, and nobody updates both.

**Once the PR is open**, a comment adds the PR link, numbered test steps with the starting state first and `Expected:` where the result shows, and screenshots taken with `annotated-screenshots` while walking those steps. A change with nothing on screen says "No UI change" instead of photographing a terminal.

It shares `pr-description`'s write rules — show the draft first, send the text from a file, read it back — and, like it, does not talk to any tracker itself.

## `doc-writer` — Drift is the default

Two modes: **Author** a new page, or **Drift** — fix only the sentences a change made false.

**When the dispatch does not say which, it does Drift.** It is the smaller and more reversible action, and the agent has no channel to ask. An unnecessary Drift pass costs a few edits; an unnecessary Author pass adds a page someone now has to maintain, and a page nobody asked for is very rarely deleted.

Three boundaries make it safe to point at a repository you care about:

**It has no `Bash`, deliberately.** It cannot run `git diff`, so it must be *handed* the change. Given neither a diff nor a plan it says so and stops, rather than documenting the repository as it imagines it. A document written from a guess is worse than a stale one — the stale one is at least a record of something that was true.

**`CLAUDE.md`, `AGENTS.md` and insights files are not documentation.** They are context written for agents, with their own writers and their own rules. If one is now false, the agent reports it and leaves it.

**It does not modernise.** A document in an older style, referring to an older tool, describing a process that still works, is not drift. Rewriting it turns a small diff into a large one and buries the correction the change actually needed. Someone else's stale text is reported under `Left:`, not fixed.

## What it will not do

| Not this | Why |
| :--- | :--- |
| Draw boxes onto a saved image | Estimated coordinates are wrong by a row, and look right while you author them |
| Seed data to make a screen look fuller | A screenshot is evidence. Invented rows get quoted back at you |
| Photograph something that is not working yet | An annotated screenshot reads as proof |
| Publish a PR description or a ticket without showing it first | It is published, quotable, and often mailed to a team the moment it lands |
| Copy the plan into a ticket | The ticket says what to do; the plan already says how, and two copies drift |
| Introduce a documentation convention the repository lacks | No new decision-record scheme, no new directory, no new template, as a side effect of documenting a feature |
| Edit source, tests or configuration | `doc-writer`'s write scope is documentation paths, and it has no Bash to route around that |
| Commit, push, or open a pull request | Ending a run with a commit nobody asked for makes it irreversible before it has been read |

## Evals

Five behaviour cases under `evals/`. See [evals/README.md](evals/README.md), including the note that `claude plugin eval` is currently early access.

## Dependencies

```
change-docs@1.1.0
└── engineering-paved-path@^1.0.0     mermaid-diagram, for doc-writer's diagrams
```

`^1.0.0` and not `^1.1.0`: the only thing needed is `mermaid-diagram`, which has shipped since 1.0.0. Constrain what you rely on, not what happens to be current.

## Compatibility

Claude Code >= 2.1.110 — the floor for version-constrained plugin dependencies.

`annotated-screenshots` — and `ticket-description` when it takes screenshots — additionally needs browser automation that can evaluate a script in the page and save a screenshot to a file. It names no particular one, and works with whatever the session has.
