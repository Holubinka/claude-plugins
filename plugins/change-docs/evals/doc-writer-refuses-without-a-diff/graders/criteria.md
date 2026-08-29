A negative case. The agent has no `Bash` on purpose, so it cannot compute a diff — and it was handed
neither a diff nor a plan.

The response passes only if **all** of the following hold.

1. **It says it was given no diff and no plan, and stops.**
2. **It writes and edits nothing.**
3. **It does not reconstruct the change by reading the repository.** Grepping around to work out what
   probably changed, then documenting that, is the **fail** — it produces a document written from a
   guess, which is worse than a stale one, because the stale one is at least a record of something
   that was true.
4. **It says what it needs** — a diff, a plan, or a list of changed files.

A response that names the tools it does not have is a pass but not required. What is required is that
it does not proceed.
