---
name: plugin-feedback
description: "Keeps a local record of how installed plugins actually behave — both scanned automatically from the transcripts Claude Code already writes, and noted by hand when something goes wrong. Use when a plugin did something wrong, when one you expected never loaded, when asked which skills are actually being used or whether they are earning their cost, and when turning any of that into a bug report or an eval case. Nothing is sent anywhere; the log stays on this machine until an entry is exported and pasted deliberately."
metadata:
  version: "1.0.0"
keywords: [feedback, reporting, log, eval-case, maintenance]
---

# plugin-feedback

Two halves. One runs on its own from what is already on disk; the other costs a line and covers what a scan cannot see.

The failures worth reporting happen mid-task, when the person has no intention of stopping to
write a bug report — and by the evening the detail that made it reproducible is gone.

So record it in one line now, and decide later whether to send it.

**Nothing here touches the network.** The log is local, it stays local, and it moves only when
someone runs an export and pastes the result somewhere themselves.

## Start with the passive half — it needs nothing from anyone

```sh
${CLAUDE_PLUGIN_ROOT}/scripts/feedback.sh collect      # scan this project's transcripts
${CLAUDE_PLUGIN_ROOT}/scripts/feedback.sh usage        # what actually fired, and how often
```

Claude Code already writes a transcript for every session. `collect` reads them and records
**structural facts only** — which namespaced components were invoked, how many times, turn counts,
token totals, dates, branch. Never prompt text, never output text, never file contents.

This is the half that survives contact with real work, because it asks nothing of a busy person.
It also produces the one number a maintainer can never have: **how often a component fired out of
sessions actually run.**

`--all-projects` widens it beyond the current repository; `--days N` sets the window.

**A component sitting at 0% is the finding.** It is charging its description on every turn and
returning nothing, and nothing else in the toolchain can see that. An empty report — nothing fired
at all — is a finding too, not an empty result: either nothing is installed, or the descriptions are
not matching the work being done.

Read `reread_ratio` while you are there. A multi-agent bill is re-reading context, not producing
output, so an optimisation that cuts output and leaves re-reading alone has changed nothing.

### Use the official session report for the general question

**`session-report` in the official marketplace does this better and does more of it.** Same source,
a configurable window, `by_skill` and `by_subagent_type` breakdowns with shares, expensive-prompt
drill-downs, and an explorable HTML report. If the question is *where did my tokens go and what am I
using*, reach for that.

`collect` here is deliberately narrower and exists for one reason: **it writes into this log, so the
usage numbers sit beside the failures somebody recorded by hand.** "This fired twelve times and here
are the three entries where it went wrong" is a sentence neither half can produce alone. It also
counts only namespaced plugin components, because a built-in agent firing is not evidence about a
plugin.

If you are not using the manual half, you do not need this half either.

### What this is not

**It does not run, replace, or call a retrospective on a single orchestrated run**, and the two read
different files. This reads the main-session transcripts under `~/.claude/projects/`, many sessions
at a time, and answers *which components fire and how often*. A retrospective reads one session's
subagent output files and answers *what did this particular multi-agent run cost, agent by agent*.
There is a skill for that elsewhere in this marketplace; it is named here in prose rather than in
backticks, because this plugin declares no dependency on the one that owns it.

Both print a `reread_ratio`, which is the only place they overlap and the reason they are worth
telling apart: this one gives you the ambient figure across your real work, that one gives you a
single run broken down by agent. Neither number belongs in the other's table.

## Then the manual half, for what a scan cannot see

A scan knows a component fired. It does not know whether what it did was any good, and it cannot
know about the one that should have fired and did not. That needs a person, and it needs to cost
them one line.

## Three verdicts

| Verdict | When |
| :--- | :--- |
| `misfired` | It ran and did something wrong — a bad finding, an edit outside its scope, an incorrect refusal |
| `did-not-fire` | You expected a skill or agent and it never loaded, or a different one did |
| `worked` | It did something notably right, especially something you would have got wrong yourself |

**`did-not-fire` is the one to bother with.** Nobody reports it spontaneously: nothing visibly
breaks, you just do the work yourself and move on — so from a maintainer's seat it is
indistinguishable from success. It is also the expensive failure, because a component that never
fires is pure always-on cost.

**`worked` is not flattery.** It is the only evidence that a component earns its cost, and without
it the log is a list of complaints that argues for deleting everything.

## Recording one

Compose the entry, then append it. Five headings, and the fourth is the one that matters:

```sh
${CLAUDE_PLUGIN_ROOT}/scripts/feedback.sh record <plugin> <verdict> <<'ENTRY'
## Component
<plugin:skill-or-agent>

## What you asked
<the request, as close to verbatim as it survives>

## What happened
<the relevant excerpt. Not the whole transcript — the part that was wrong>

## What it should have done, and how you would tell
<a statement two people would grade the same way>

## Reproducible
<once / twice out of two / every time / did not retry>
ENTRY
```

**Write the fourth heading as a check, not a wish.** "It should have been better" cannot be graded
and will not become a case. "No naming preference appears in the findings table" can. This is the
same bar `docs/evals.md` rule 1.2 sets for every case, asked while the detail is still fresh.

**Redact as you write.** Replace real paths, names and identifiers with placeholders. The shape of
what happened is what matters, and an entry written clean is one you can export without re-reading
it line by line.

## Where the log lives, and the catch

Default is `${CLAUDE_PLUGIN_DATA}` — the per-plugin directory. **Claude Code deletes it when the
plugin is uninstalled from its last scope**, which means the log explaining why someone uninstalled
something vanishes at the moment they uninstall it.

Set `PLUGIN_FEEDBACK_DIR` to a path they own if it should outlive that, or export before
uninstalling. The default stays inside the plugin data directory because writing outside the project
without being asked would breach this marketplace's own security policy.

## Handing it on

```sh
feedback.sh list                     # what is in the log
feedback.sh export-issue <id>        # a body for the GitHub issue form
feedback.sh export-case <id> <dir>   # prompt.md + graders/criteria.md, for a pull request
```

**`export-issue`** produces the body for whichever of the two issue forms matches the verdict.
Read it once before pasting — the log was written for the author, and publishing is a different
audience.

**`export-case`** is the one that closes the loop. It writes the case skeleton straight into the
marketplace's layout, so a report can arrive as a pull request that already carries its own
regression test. The criteria still need rewriting into numbered bold assertions before it is
opened — the script says so, and it cannot do that step honestly on someone's behalf.

A maintainer receiving a case is receiving something they would otherwise have to write themselves
from a description of a thing they cannot see.

## Rules

- **One entry per observation.** A log entry covering three things becomes three arguments in one
  issue and gets closed as unclear.
- **Record before diagnosing.** The entry is what happened, not the theory. A theory in the entry
  narrows what a maintainer looks at, and the first theory is usually wrong.
- **Never send anything automatically**, and never suggest it. The user pastes, or nothing leaves.
- **An empty log after weeks of use is information.** Either nothing is going wrong, or nobody is
  recording. Say which you think it is rather than treating it as a good sign.
