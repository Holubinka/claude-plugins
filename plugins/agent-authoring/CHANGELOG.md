# Changelog

All notable changes to `agent-authoring`. This project follows [SemVer](https://semver.org/);
the bump rules this repository uses are in [docs/releasing.md](../../docs/releasing.md).

Releases are tagged `agent-authoring--v<version>`.

## [1.1.0] — 2026-09-25

The usage count was reporting a floor and calling it a total. Over thirty real days it found 138
invocations; the same transcripts hold 271.

### Fixed

- **`collect` reads subagent transcripts.** A skill an agent calls, or has preloaded by its
  `skills:` frontmatter, is written to `<session>/subagents/*.jsonl`, never to the main file. Eight
  skills that reported zero were firing there, some of them twenty times.
- **`collect` counts `/plugin:skill` typed by hand.** A slash command is a user record, not a tool
  call, so a skill run only that way read as never used.
- **A skill called by its bare name is credited** when exactly one installed plugin ships it and no
  project or personal skill of that name shadows it. The rest are counted under the table rather
  than dropped, so a large unattributed number is visible next to the zero it might explain.

### Added

- **`scripts/selftest.sh`** — the collector against a synthetic transcript tree, one assertion per
  place a component can load from and one per record that must not count. CI already runs every
  `plugins/*/scripts/selftest.sh`; this one fails on 1.0.0.

### Changed

- **`usage` splits every row by where it loaded** — `model`, `slash`, `subagent`. A component that
  fires only inside subagents is reached through an agent that names it, not through its own
  description, and that is a different finding from one that fires nowhere. Collections written by
  1.0.0 still report, with every count under `model`.
- **`model-routing` bounds the follow-up rule.** "Send a follow-up rather than spawn a fresh agent"
  held for one follow-up and was followed nine times: one agent, resumed across nineteen hours, took
  43% of a seventeen-agent run, because each resume replays everything accumulated before it. A
  third resume now means the brief gets fixed and the agent is dispatched fresh.
- **`model-routing` says when to carry a map rather than point at it** — when every lane of a
  fan-out sits in one package, the lines of its conventions file that matter go into the brief, so
  N agents do not each buy the same file.

## [1.0.0] — 2026-08-29

First release. Three skills and two scripts. The authoring conventions and the audit are generalised from a private monorepo's `.claude/` set; the feedback log is new.

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

- **`plugin-feedback`** and `scripts/feedback.sh` — a local log of how an installed plugin behaved,
  which exports as a bug report or as an eval case.

  It exists because of an asymmetry in what people report. Nobody files an issue saying a skill
  correctly stayed quiet, and **nobody reports the skill that should have loaded and did not** —
  nothing visibly breaks, they do the work themselves and move on. From a maintainer's seat that is
  indistinguishable from success, and it is the expensive failure, so it gets its own verdict and the
  skill asks for it by name.

  `worked` is a verdict for the same reason in reverse: it is the only evidence a component earns its
  always-on cost, and a log holding only complaints argues for deleting everything.

  Nothing touches the network. The default lives in `${CLAUDE_PLUGIN_DATA}`, which is deleted on
  uninstall — so the log explaining why someone uninstalled something vanishes when they do. That is
  named in the skill and the README rather than hidden, with `PLUGIN_FEEDBACK_DIR` as the way out.
  Writing outside the project uninvited would breach this marketplace's own security policy, and the
  constraint produced the better shape: the log is a staging area, and export is a deliberate act.

- **`A4` reads the manifest, not just the directory.** The check's stated rule is that a backticked
  cross-plugin name is a promise it resolves *at install time*, and it was only verifying that the
  name resolved *in the audited directory*. Two plugins sitting side by side in one repository made
  an undeclared edge look fine, and it would have broken for anyone installing either alone.

  Found by asking whether one of this plugin's own skills could point at another plugin's
  retrospective. It could, silently, and the audit had nothing to say about it.

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
