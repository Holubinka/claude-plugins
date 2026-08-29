---
name: plugin-feedback
description: "Records how an installed plugin's skill or agent actually behaved, into a local log, and turns an entry into a paste-ready bug report or an eval case for a pull request. Use when something a plugin did was wrong, when one you expected did not load at all, when something worked notably well, or when asked to report, log or send feedback about a plugin. Nothing is sent anywhere — the log stays on this machine until you export an entry and paste it yourself."
metadata:
  version: "1.0.0"
keywords: [feedback, reporting, log, eval-case, maintenance]
---

# plugin-feedback

The failures worth reporting happen mid-task, when the person has no intention of stopping to
write a bug report — and by the evening the detail that made it reproducible is gone.

So record it in one line now, and decide later whether to send it.

**Nothing here touches the network.** The log is local, it stays local, and it moves only when
someone runs an export and pastes the result somewhere themselves.

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
