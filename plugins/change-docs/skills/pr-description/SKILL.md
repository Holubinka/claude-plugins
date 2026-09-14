---
name: pr-description
description: "Writes the description on a pull request or merge request — what changed, why, how it was verified, and what the risk is — with hard length limits and an explicit list of what never goes in one. Use when opening a PR, updating an existing PR's body, or asked to summarise a branch for review. Vendor-neutral: it produces the text and the approval gate, whatever hosts the repository."
metadata:
  version: "1.1.0"
keywords: [pull-request, review, description, writing]
---

# PR description

A reviewer opens your description to answer one question: **what am I about to read, and what should
I be suspicious of?** Everything that does not serve that is taking space from what does.

## When not to use this

| Situation | Instead |
| :--- | :--- |
| Filing the ticket for the work, or adding test steps and screenshots to it once the PR is open | `change-docs:ticket-description` |
| Showing a UI change in an image | `change-docs:annotated-screenshots` |

## The shape

Four labelled parts, in this order, as **bold labels rather than headings** — a PR body is already
inside a page with its own heading hierarchy, and `##` inside it fights the page.

```
**What**
- Two or three bullets. One line each.

**Why** — one sentence.

**Test** — what was actually verified, and how.

**Risk** — what could go wrong, and what would show it first.
```

**What comes before Why.** A reviewer reads *what* to decide whether to read at all; a *why* that
arrives first is context for something they cannot picture yet.

**Why is one sentence for the whole change**, not one per bullet. If the bullets need separate
reasons, they are separate changes.

## Length

**About ten lines. Fifteen is the ceiling.** The description is a signpost to the diff, not a second
copy of it.

If What will not fit in three bullets, do not add a fourth — the diff should have been two. Say that
in one line instead, naming the separable pieces.

**Do not hard-wrap.** One bullet or one sentence is one line, however long. Never insert a line break
at 80 or 90 characters: several hosts render a single newline in a PR body as a visible break, so the
wrapped text shows up as ragged half-lines in the middle of sentences.

## Example

```
**What**
- Order export streams rows to the response instead of building the whole file in memory.
- Adds a `limit` query parameter, capped at 100 000 rows.

**Why** — exports over roughly 50 000 rows ran the worker out of memory and returned a 502.

**Test** — ran the export suite; exported 180 000 rows locally with memory flat at about 90 MB. Not tried against a production-sized replica.

**Risk** — the streamed response has no `Content-Length`, so a client that relies on it shows a progress bar stuck at 0%.
```

Nine lines. The interesting part is the last sentence of Test: the one thing that was not checked is
named, so the reviewer knows exactly what is left for them.

## Test is a report, not instructions

**Say what was verified and how, in the past tense**, in a line or two. A reviewer uses this to
decide what they still need to check themselves.

**Step-by-step test steps and screenshots do not go here.** They go on the ticket once the PR is
open — see `change-docs:ticket-description`. A `Test` section that is a numbered how-to has answered
a question the reviewer did not ask and hidden the one they did.

**If something was not verified, say so.** "The scheduled path is unexercised — no way to trigger it
locally" is the most useful line in most descriptions. An unqualified "tested" that turns out to
mean "the typecheck passed" costs the next reviewer their trust in every future one.

## Never include

| Not this | Why |
| :--- | :--- |
| A file-by-file list of what changed | The diff is right there, and it is authoritative. A prose copy of it drifts as you push |
| The commit log | Same. If the commits are the explanation, the description has not been written |
| Diff statistics — files changed, lines added | The interface shows them, and they measure typing, not risk |
| Per-suite test counts for every package | One line of outcome. The detail is in CI |
| Raw tool output, stack traces, logs | Paste those in a comment where they can be scrolled past |
| Narration of the process — "I first tried X, then Y" | Nobody is reviewing the path you took |
| A description of the codebase for context | The reviewer works here |
| Anything about how the change was produced | Not part of what is being reviewed |

Each of these makes a description *feel* thorough while making it worse, which is why they survive.

## Risk, honestly

Name the failure mode and its first symptom, not a reassurance. "Low risk, well tested" is not risk —
it is the sentence people write when they have not thought about it.

**Where the honest answer is that the risk is low, say what makes it low.** One reason is enough:
"behind a flag that is off everywhere", "additive column with a default, no read path yet".

## Before it is sent

**Show the draft and stop.** A description is published, quotable, and often mailed to a team the
moment it lands. Do not create or update a pull request until whoever asked has read the body.

**Then verify it afterwards by reading it back.** Fetch the pull request and check that the body is
what you sent. A successful-looking response can come back with an empty or truncated description —
a nested-quoting mistake, a body sent as a shell argument, a field silently dropped — and it looks
identical to success from the outside. Reading it back is the only way to know.

**Never send a body through a shell heredoc.** Write it to a file and have the tool read the file.
Nested quoting has silently produced empty descriptions often enough that the file is the rule, not
the precaution.

## Updating an existing description

**Read the current one first, and preserve what you are not changing.** Update APIs on most hosts
replace the whole object: a field you omit is not left alone, it is cleared. Reviewers, labels,
assignees and the target branch have all been lost this way, by an update that only meant to fix a
typo in the body.

Fetch, change the one field, send the rest back verbatim, then read it back again.
