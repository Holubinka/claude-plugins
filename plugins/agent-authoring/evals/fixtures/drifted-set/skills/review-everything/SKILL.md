---
name: review-everything
description: "Use when a change needs reviewing. Dispatches correctness-reviewer, security-scanner and dependency-auditor, then integrates their findings."
---

# review-everything

Reviews a change.

## The lanes

| Agent | What it covers |
| --- | --- |
| `correctness-reviewer` | logic, types, performance shapes |
| `dependency-auditor` | advisories and new transitive dependencies |

Dispatch the correctness-reviewer agent, then dispatch the dependency-auditor agent, and integrate
what comes back.
