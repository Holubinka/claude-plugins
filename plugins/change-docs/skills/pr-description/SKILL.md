---
name: pr-description
description: "Writes the description on a pull request or merge request — what changed, why, how it was verified, and what the risk is — with hard length limits and an explicit list of what never goes in one. Use when opening a PR, updating an existing PR's body, or asked to summarise a branch for review. Vendor-neutral: it produces the text and the approval gate, whatever hosts the repository."
metadata:
  version: "1.0.0"
keywords: [pull-request, review, description, writing]
---

# PR description

A reviewer opens your description to answer one question: **what am I about to read, and what should
I be suspicious of?** Everything that does not serve that is taking space from what does.

## The shape

Four labelled parts, in this order, as **bold labels rather than headings** — a PR body is already
inside a page with its own heading hierarchy, and `##` inside it fights the page.

```
**What** — the change, as numbered items. One line each.

**Why** — the reason for each, pointing back by number.

**Testing** — what was actually verified, and how.

**Risk** — what could go wrong, and what would show it first.
```

**What comes before Why, and the numbering is what joins them.** A reviewer reads *what* to decide
whether to read at all; a *why* that arrives first is context for something they cannot picture yet.
Numbering lets Why say "2 is what makes 1 safe" instead of restating 1 to point at it.

## Length

**Fifteen lines is normal. Forty is the ceiling.** A description longer than the diff is a signal
that the diff should have been two.

If you cannot get under forty lines, that is worth saying in the description itself: name the two or
three separable pieces, so the reviewer can read them as separable even though they arrived
together.

## Testing is a report, not instructions

**Say what was verified and how, in the past tense.** "Ran the suite in `<package>`: 34 passing.
Exercised the import path with a 12 MB file, confirmed the row count in the database." A reviewer
uses this to decide what they still need to check themselves.

Reproduction steps belong in the ticket, or in a comment when someone asks. A `Testing` section that
is a numbered how-to has answered a question nobody asked and hidden the one they did.

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

The list is long because each of these makes a description *feel* thorough while making it worse,
which is why they survive.

## Risk, honestly

Name the failure mode and its first symptom, not a reassurance. "If the migration runs against a
table larger than the staging copy it will hold a lock long enough to time out requests; the first
sign is a spike in 504s on the orders endpoint" is risk. "Low risk, well tested" is not — it is the
sentence people write when they have not thought about it.

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
