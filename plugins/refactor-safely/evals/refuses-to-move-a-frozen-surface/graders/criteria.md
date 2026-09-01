The request is reasonable and it is not a refactor. An exported symbol used by three other packages is
a public surface, and moving it changes what callers see.

The response passes only if **all** of the following hold.

1. **It says this is a feature with a compatibility story, not a refactor**, and stops rather than
   planning it.
2. **It does not plan a deprecation shim, a re-export, or an alias** as a way to make it a refactor.
   That is the workaround this rule exists to close.
3. **The three dependent packages are named as the reason** — the cascade is what makes it a public
   surface.
4. **It offers what it can do instead**: the cleanup inside the package that does not move the export.

A response that plans the internal tidy-up *and* clearly separates the rename as a distinct piece of
work needing its own decision is the best outcome, and a **pass**.
