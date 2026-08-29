# Changelog

All notable changes to `agent-authoring`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `agent-authoring--v<version>`.

## [1.0.0] — 2026-08-29

First release. Two skills and an audit script, generalised from a private monorepo's `.claude/` set.

### Added

- **`authoring`** — the conventions, built around one rule: the frontmatter description is a trigger
  condition and must never summarise the workflow.

  **A description that reads like a procedure gets followed instead of the body.** Nothing errors —
  the model reads three summarised steps, believes it knows the workflow, and never loads the file
  where the rules live. That failure is repeatable, which makes it worse than an unreliable one.

  Four tests ship with it. The negative one is the one that earns its place: name a close request
  that must *not* fire this, and check the description does not match it. A description that cannot
  be made to fail is not a trigger, it is a category label.

- **`model-routing`** — the two knobs, and what each actually reduces. A cheaper tier lowers price
  per token; lower effort lowers the token count. Conflating them produces a cheap model redoing
  work: the same tokens, several times, at a lower price each.

  Its more useful half is the list of where savings actually are, which is not in making agents
  cheaper. It is in not duplicating their work — partitioning scope and naming the other lanes,
  pointing agents at a map before they search, and not fanning out when one agent suffices.

- **`scripts/audit-harness.py`** — a static audit of a set of skills and agents, checking the claims
  they make about each other. Four checks, each of which has drifted in a real set at least once, and
  none of which any runtime would catch.

  The load-bearing one is `A2`: **a fan-out table must declare, per lane, the condition under which
  that lane runs.** A roster with no conditions is a roster the user has to select from by hand, which
  is the thing the fan-out was supposed to do for them.

  `A4` is the machine form of the rule that decides every dependency edge in this marketplace: a
  backticked `plugin:name` is a promise that it resolves at install time. A component that cannot
  make that promise names the role in prose instead.

  No YAML library, deliberately — a frontmatter reader that needs a dependency does not run in the
  environments this script is most useful in.

### Changed from the source workflow

- **The "when Claude may propose a new command" protocol did not come across.** It was a policy about
  one repository's approval process, not a convention about authoring.

- **The agent roster, the pipeline file and the stage-guard registration steps are gone.** They were
  instructions for maintaining one specific set, and every one of them named a file that exists in no
  other repository.

- **The audit's four repo-shaped checks were dropped**, keeping the four that work on any set. The
  originals also verified a roster against a pipeline document, a hook's write-scope buckets against
  the agents that exist, and two counts stated in prose — each real, and each assuming files this
  script cannot expect to find.

### Removed from the source workflow

- The five-level effort vocabulary, reduced to three with the reasoning kept: five levels means the
  next person has to choose between five, and the extremes are better reached for deliberately at
  dispatch than selected by habit in a file.
- Every per-agent routing default, which was a table about twenty specific agents rather than a rule.
