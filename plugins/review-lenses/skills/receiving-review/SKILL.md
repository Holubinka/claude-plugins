---
name: receiving-review
description: "Handles review feedback on your own work — evaluating each item against the code before implementing it, asking when a comment is unclear, and pushing back with reasons when it is wrong. Use when a reviewer, a teammate or a review tool has returned comments, when tempted to agree and start editing, and when a suggestion looks technically questionable. Every finding needs the same burden of proof whether a person or a tool raised it."
metadata:
  version: "1.0.0"
keywords: [code-review, feedback, verification, pushback]
---

# Receiving review

The other half of `review-diff`. That side files findings and puts each blocking one through an
adversary. **This side owes them the same scrutiny** — a finding is a claim about the code, and the
author is the person best placed to check it.

Agreeing quickly is the failure. It reads as cooperative and produces edits nobody verified, made
to code the reviewer was wrong about, which the next reviewer then has to find.

## The order

1. **Read all of it before responding to any of it.** Comments interact — two suggestions can
   contradict, and one can be answered by another. Reacting item by item as you read produces edits
   you then undo.
2. **Restate the requirement in your own words.** If you cannot, you have not understood it, and
   that is a question rather than a task.
3. **Check it against the code.** Open the line. Does the thing described actually happen?
4. **Decide whether it is right *for this codebase*.** A correct general principle can be wrong
   here — the repository may have decided otherwise, deliberately, somewhere the reviewer did not
   look.
5. **Respond**: a technical acknowledgement, or reasoned disagreement.
6. **Implement one item at a time**, and verify each before moving on.

## Four verdicts, and all of them are legitimate

| Verdict | When | What you owe |
| :--- | :--- | :--- |
| **Correct — fix it** | You checked and it holds | The fix, and evidence it worked |
| **Correct but out of scope** | Real, and not this change's | Say so, and where it should go instead |
| **Wrong** | The code does not do what the comment says | The line, quoted, showing it |
| **Unclear** | Two readings lead to different work | The question, with both readings named |

**Disagreeing is not rudeness and agreeing is not politeness.** A reviewer who is wrong is better
served by being told, with the line quoted, than by watching a change go in that they will have to
review again.

## What not to say

**"You're absolutely right"** — before you have checked, this is agreement performed rather than
reached. Say it after step 3 if it is true, and then say *what* you checked.

**"Good catch"**, **"Great point"** — they cost a line and carry no information. The technical
acknowledgement already contains the respect.

**"Let me implement that now"** — before verification, this commits you to an edit whose merit you
have not established.

**Silent compliance.** Making a change you believe is wrong, without saying so, is the worst of the
options: the reviewer learns nothing, the code gets worse, and the disagreement resurfaces later
with no record that it was ever considered.

## Findings from a tool

Same burden of proof, with two adjustments.

**A deterministic finding — a failing gate, an advisory with a version range — is not up for
debate.** Its evidence is a command's exit code. You can argue about the priority; you cannot argue
about whether it is red.

**A model-produced finding is a claim, not a verdict.** `review-lenses:review-diff` already routes
every blocking one through `review-lenses:finding-verifier`, and what reaches you has survived an
attempt to refute it. That makes it worth taking seriously; it does not make it correct. Check the
anchor: the fastest way to dismiss a wrong finding is to open the line it cites.

Where a finding names an input that supposedly breaks the code, **try that input.** It settles the
question in one run, in whichever direction.

## Common mistakes

| Mistake | Fix |
| :--- | :--- |
| Implementing before opening the cited line | Step 3. Most wrong findings die there |
| Agreeing to close the thread faster | The edit outlives the thread |
| Treating a tool's finding as automatically right, or automatically noise | Deterministic outranks model-produced. Both are checkable |
| Batching six fixes, then running the suite once | One at a time, verified. A red suite after six edits is a bisect by hand |
| Arguing scope without offering a home | "Out of scope" plus where it should go is an answer; alone it is a deflection |
| Fixing a symptom the comment described | The comment reports a surface. `engineering-paved-path:systematic-debugging` if the cause is unclear |
