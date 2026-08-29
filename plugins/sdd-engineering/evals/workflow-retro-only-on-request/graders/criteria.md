A negative case for the retrospective, which reads transcripts and costs real tokens.

The response passes only if **all** of the following hold.

1. **`workflow-retro` is not invoked.** The request asks what shipped, not what the
   orchestration cost. The skill's own instruction is that it runs when a run of three or more
   subagents has finished **and the question is whether the orchestration was worth it** — a
   summary request is not that.
2. **`stats.sh` is not run**, and no task transcript is read.
3. **The summary is actually produced** from what is known, rather than deferred to a
   retrospective.

A response that finishes the summary and then *offers* a retrospective passes: offering is not
running. Fail the response if the retrospective is run unasked, or if the summary is withheld
pending one.
