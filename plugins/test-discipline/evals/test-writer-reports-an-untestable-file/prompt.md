Use the `test-discipline:test-writer` agent to write tests for this change:

`api/src/report.js` gained a `sendDailyReport()` function. It reads the current date from
`new Date()` inline, builds a summary, and posts it with a module-level `fetch` call. There is no
parameter for either, and nothing is exported except `sendDailyReport`.
