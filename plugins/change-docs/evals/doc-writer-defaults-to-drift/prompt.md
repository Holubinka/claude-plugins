Use the `change-docs:doc-writer` agent to document this change. Here is the diff:

```diff
--- a/lib/retry.js
+++ b/lib/retry.js
-const MAX_ATTEMPTS = 3;
+const MAX_ATTEMPTS = 5;
@@
-  await sleep(200);
+  await sleep(backoffMs(attempt));
```

`docs/reliability.md` currently says: "Failed requests are retried up to three times, 200ms apart."
It also has a section on the queue that this change does not touch, and a paragraph describing the
deployment process that has been out of date since the move to containers.
