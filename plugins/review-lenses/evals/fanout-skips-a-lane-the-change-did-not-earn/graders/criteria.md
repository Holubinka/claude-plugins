The change earns two lanes and not the third. Running everything is the failure this plugin exists to
avoid.

The response passes only if **all** of the following hold.

1. **The correctness and boundaries lanes run**, the second because a route handler and an adapter
   changed and an import edge moved.
2. **The dependency lane does not run.** There is no lockfile and no manifest dependency block in the
   diff, so there is nothing for it to say.
3. **The `## Lanes` section names the skipped lane and the condition that skipped it.** Omitting it is
   a **fail** even if the lane was correctly not run — a report that does not say what was skipped
   reads as full coverage.
4. **The lanes that do run are dispatched in one message.** Two separate dispatches is a fail: they run
   in series and the fan-out was imagined.
5. **Each brief names what the other lane owns.** Overlap is only fixable at dispatch, because parallel
   contexts cannot see each other.

Running a security pass because the adapter is new is a **pass** only if it is the correctness lane's
own obligation, not a fourth dispatched agent.
