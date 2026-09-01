Introduced in 1.1.0. Until this release the `security` skill's trigger description named React,
Express, MongoDB and JWT, which narrowed it on every other stack. Nothing about the guidance was
ever stack-specific.

The response passes only if **all** of the following hold.

1. **The open-redirect risk is identified** — an attacker-controlled destination reached after
   authentication, used for phishing or token leakage.
2. **The check named is an allow-list decision, not a blocklist or a string test.** Validating
   that the target is a known internal path, or a host on an explicit allow-list, and rejecting
   otherwise. Answers that only strip `//` or check for `http://` are a **fail** — that is the
   shape this class of bug survives.
3. **Nothing in the answer assumes Express, React, MongoDB or JWT.** Advice framed as "in
   Express you would…" when the question named Django is a fail.

Whether the model announces that it loaded a skill is not graded. What is graded is that the
answer carries the skill's content on a stack the old description excluded.
