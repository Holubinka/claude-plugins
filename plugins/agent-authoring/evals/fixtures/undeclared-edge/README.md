# undeclared-edge

A fixture with one fault: `skills/borrower` names `drifted-set:review-everything` in backticks
while this plugin's manifest declares no dependency on `drifted-set`.

It resolves when both directories sit in the same repository, and it would not resolve for anyone
installing this plugin on its own. That gap is invisible to every other check.
