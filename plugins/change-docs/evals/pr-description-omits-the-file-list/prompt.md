Write the pull request description for this branch. It changes 14 files: a new `backoffMs` helper
and its test, the retry loop that calls it, a configuration default, and eleven call sites updated
to pass the new option. The suite passes in both packages. The retry path is exercised by unit
tests; the behaviour against a real flaky upstream has not been observed.
