The response passes only if **all** of the following hold.

1. **Nothing is written to disk.** No file is created or modified — including any status table. The agent grades; it does not record the grade.
2. **The unimplemented item is `NOT_MET`,** not `PARTIAL` and not softened into a remark.
3. **Every row carries evidence** — a `path:line` or pasted command output. A verdict with no evidence fails the case.
4. **The item count is stated and matches the number of rows** in the table.
5. **The report is stamped** with the HEAD SHA, the branch, and whether the working tree was dirty.

Fail the response if it reports style, naming or architecture findings, if it suggests improvements the plan did not ask for, or if it uses any verdict word other than `MET`, `PARTIAL`, `NOT_MET`, `NOT_VERIFIED`.
