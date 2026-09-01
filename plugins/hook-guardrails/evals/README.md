# Evals

**This plugin has no model-graded cases, and that is the honest answer rather than a gap.**

It ships no skills and no agents. There is no description to trigger, no report to grade, and no
judgement to score — the whole plugin is two shell scripts that either exit 2 or do not. A case
asking a model to describe what a hook would do would be scoring the description, not the hook.

What replaces them is a deterministic self-test:

```sh
bash ../scripts/selftest.sh
```

Eighteen cases in a throwaway repository it creates and removes. Exit status is 1 if any case behaves
differently from what is asserted.

| Group | Cases |
| :--- | :--- |
| Pushes that must be refused | explicit branch, `HEAD:branch` refspec, `--force-with-lease`, `release/2.1` under a `release` pattern, a push after `&&` |
| Pushes that must go through | `-u origin feature/thing`, `echo "git push origin main"`, `git status`, a bare push with no upstream on an unprotected branch |
| The case the plugin exists for | a **bare `git push`** whose upstream silently resolves to `origin/main` |
| The escape hatch | `HOOK_ALLOW_PROTECTED_PUSH=1` lets a refused push through |
| Formatter skip rules | generated file, vendored path, missing file — each exits 0 and leaves the file alone |
| Formatter happy path | the edited file is formatted, using a stand-in binary so the path is exercised rather than assumed |

## Why the stand-in binary matters

The formatter case installs a two-line script at `node_modules/.bin/prettier` rather than checking
that the hook *would* have called one. That distinction found both bugs this plugin had:

- the hook checked for `node_modules/.bin/<tool>` and then invoked the tool **through the package
  runner**, which resolves the package rather than the shim and fails where only the shim exists;
- the project root fell back to the working directory outside a git repository, so a file would have
  been formatted to the rules of whatever project the session happened to be sitting in.

Neither is visible by reading the script. **A test that asserts a hook was reached is not a test that
it worked**, and both of these were reached.

## What is deliberately not tested

**Whether Claude Code wires the hooks as `hooks.json` declares.** That is the platform's contract, not
this plugin's behaviour, and a test of it would be a test of the harness. The self-test feeds the
scripts the same JSON payload shape the platform does, which is the part this plugin is responsible
for reading correctly.
