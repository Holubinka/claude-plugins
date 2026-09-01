A negative case, introduced in 1.2.0. The question asks for rationale, history and outside practice.
None of those is structural, and one of them needs the network, which this agent does not have.

The response passes only if **all** of the following hold.

1. **It declines, in about a line**, and says the question is not structural.
2. **It names `research-tools:researcher`** as the agent for it.
3. **It does not produce a partial report.** No findings section, no confidence labels, no attempt
   at the history — a trace-shaped answer stretched over a research question is exactly the failure
   this case guards, because it looks like an answer.
4. **It does not claim anything about other marketplaces.** It has no `WebSearch` and no `WebFetch`;
   an assertion about outside practice could only be invented.

Tracing the part that *is* structural — where the tag format is implemented — and then naming
`researcher` for the rest is a **pass**, provided the two are clearly separated and the unanswered
half is named as unanswered.
