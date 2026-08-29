# The lanes

Reference for `review-diff`. What each lane owns, what it must not report, and what happens when it
is not installed.

## correctness — `review-lenses:correctness-reviewer`

**Runs when:** any diff touching executable code.

**Owns:** logic, the inputs the code will actually get, type-safety holes, performance *shapes*,
concurrency hazards.

**Must not report:** placement, dependency direction, OWASP shapes, advisories, test coverage, style.

**Its discipline is the three-line finding** — the offending expression at `path:line`, the invariant
it violates, and **a concrete input that breaks it**. If a lane cannot name the input, it has not found
a bug; it has found something it does not like. That third line is also what makes the finding
falsifiable, which is what the verification step needs.

**Its security obligation.** Rather than a separate lane, this one invokes
`engineering-paved-path:security` itself when the diff touches authentication, authorization, input
parsing, uploads, secret handling, or a new outbound request with a caller-supplied destination.

A separate security agent would be a fourth context reading the same diff for a subject that is a
checklist rather than an open question. Where a security review genuinely needs its own pass — a
change that is *about* the auth model rather than one that touches it — dispatch that deliberately
instead of adding a standing lane.

## boundaries — `architecture-review:architecture-reviewer`

**Runs when:** a file crosses a directory the repository treats as a boundary, an import edge changes,
or a composition root, a route or an adapter is touched.

**Owns:** ring placement, dependency direction, ports and adapters, module cohesion, the shape of data
crossing a boundary, the Server/Client line.

**Must not report:** correctness, performance, naming, security — it names the owner in one line and
moves on.

It reads the repository's own architecture rules first, and where none exist it applies its own
**as a proposal, explicitly labelled** — never as a finding about your repository. That is the property
that makes it safe to point at a codebase it has never seen.

## dependencies — `review-lenses:dependency-auditor`

**Runs when:** a lockfile or a manifest dependency block is in the diff. **Never otherwise** — there is
nothing for it to say, and a lane that reports nothing on most runs stops being read on the run where
it matters.

**Owns:** advisories weighted by whether the path ships, what actually entered the tree, whether the
repository already has something that does this job, which dependency block it landed in, maintenance
and licence.

**Must not report:** anything about the code that uses the dependency.

Its advisory findings are **deterministic** — evidence is a command's exit code and a database entry —
so they skip verification and may not be downgraded.

## What is deliberately not a lane

**A test writer.** Proving a test can fail means holding a deliberate defect in the working tree
between mutating a file and reverting it. Anything reading files or running a gate in that window
measures the mutation rather than the branch, and it cannot detect the writer from the inside.

Readers are safe beside each other. A writer is safe beside nothing. Gap coverage is separate work,
run alone.

**A plan verifier.** It compares the branch against a document, which is a different question from
whether the code is right, and it wants the whole change rather than a slice.

**A runtime check.** Exercising the change against a running system is worth doing and is not a review
— it needs the stack up, it seeds and cleans up data, and it is therefore a writer.

## When a lane's plugin is not installed

`architecture-review` is a declared dependency, so the boundaries lane resolves at install time.

If a lane is unavailable for any other reason, **say so in the `## Lanes` section and do not
substitute.** Reviewing boundaries from memory, in a lane labelled as the boundary review, produces a
report that claims coverage it does not have — which is worse than the gap it was papering over.
