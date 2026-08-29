Use the `change-docs:doc-writer` agent to document this change. Here is the diff:

```diff
--- a/package.json
+++ b/package.json
-    "test": "node --test",
+    "test": "vitest run",
```

`CLAUDE.md` at the repository root says "run `node --test` to exercise the suite".
`docs/contributing.md` says the same thing in its setup section.
