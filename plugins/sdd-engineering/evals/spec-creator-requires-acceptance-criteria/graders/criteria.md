Introduced in 1.1.0. The agent must not hand over a specification in which a stated goal has
no acceptance criterion.

The response passes only if **all** of the following hold.

1. **Every goal is accounted for.** Each of the three goals either has at least one numbered
   acceptance criterion in EARS form, or appears as a numbered open question — never neither.
2. **Goal 3 is not silently dropped.** "Loads fast enough" carries no number, so it is either
   turned into a criterion with a threshold the agent can justify from the sources, or raised
   as an open question. A spec that omits it entirely is a **failure**, and it is the specific
   behaviour this case exists to test.
3. **The report states coverage** — how many mandatory requirements the spec carries and that
   each has a criterion. If one does not, the report says the spec is blocked and names the
   goal by its number.
4. **Non-goals are not treated as requirements.** If the agent records any non-goal, it does
   not demand a criterion for it.

Fail the response if a goal appears in the spec with no criterion and no open question, or if
the report claims complete coverage that the document does not show.
