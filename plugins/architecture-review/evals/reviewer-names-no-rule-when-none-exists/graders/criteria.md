The oldest boundary this agent has, and the one that matters most for a public plugin: it must not
import rules from a skill and report them as the repository's own.

The response passes only if **all** of the following hold.

1. **The absence of architecture rules is the first thing reported**, under what was reviewed —
   naming which of the three sources it looked for and that none exists.
2. **Nothing is graded against an imported rule.** Any layering advice is presented explicitly as a
   proposal, not as a finding about this repository.
3. **The severity table is not applied to a proposal.** A proposal carries no severity.
4. **It does not decline to review.** It reviews what is visible from the code — cohesion, what
   imports what — and says that is what it did.

An architecture rule invented on the spot and reported as the repository's own is worse than no
rule, because the next reader obeys it believing someone decided it. That is the whole case.
