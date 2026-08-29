# Discovery order — the tables

Reference for `project-commands`. The rule is in `SKILL.md`; this is what to open.

## The lockfile map

Read at the **repository root**, not the current directory. A package inside a workspace does
not carry its own lockfile, and finding none there proves nothing.

| Lockfile | Runner | Run a script | Run a binary |
| :--- | :--- | :--- | :--- |
| `pnpm-lock.yaml` | pnpm | `pnpm run <script>` | `pnpm exec <bin>` |
| `yarn.lock` | yarn | `yarn <script>` | `yarn <bin>` |
| `bun.lock`, `bun.lockb` | bun | `bun run <script>` | `bun x <bin>` |
| `package-lock.json` | npm | `npm run <script>` | `npx <bin>` |
| none | npm | `npm run <script>` | `npx <bin>` |

**A globally installed binary is not reached through the runner.** `npx tsc` in a project that
has no local `typescript` refuses to run and exits non-zero with a banner — which is
indistinguishable from a type error to anything reading the exit code. Check
`node_modules/<tool>` first (walking up to the repository root); fall back to the bare binary
on `PATH`; and if neither exists, that lane has no command.

## Script keys, by lane

Match by key, in this order, and take the first that exists.

| Lane | `package.json` keys |
| :--- | :--- |
| typecheck | `typecheck`, `type-check`, `types`, `tsc`, `check-types` |
| lint | `lint`, `check`, `lint:ci`, `format:check` |
| test | `test`, `test:unit`, `test:ci` |

A monorepo root usually has a recursive form (`pnpm -r typecheck`, `turbo run lint`,
`nx run-many -t test`). Prefer the root's recursive script when the change spans packages, and
the package's own script when it does not — a whole-repository run on a one-package change is
slow enough that it gets skipped, and a skipped gate is a missing gate.

## Other languages

| Ecosystem | Where commands live | Typical |
| :--- | :--- | :--- |
| Python | `pyproject.toml` (`[tool.poetry.scripts]`, `[tool.hatch.envs]`), `tox.ini`, `noxfile.py`, `Makefile` | `pytest`, `ruff check`, `mypy` |
| Rust | `Cargo.toml`, `Makefile.toml` | `cargo test`, `cargo clippy`, `cargo fmt --check` |
| Go | `go.mod`, `Makefile` | `go test ./...`, `go vet ./...` |
| Ruby | `Rakefile`, `Gemfile` | `bundle exec rspec`, `bundle exec rubocop` |
| PHP | `composer.json` `scripts` | `composer test`, `vendor/bin/phpunit` |
| JVM | `build.gradle*`, `pom.xml` | `./gradlew test`, `mvn -q verify` |
| Anything | `Makefile` targets, `justfile` recipes, `Taskfile.yml` | `make test`, `just lint` |

A `Makefile` target is worth preferring over the underlying tool when one exists: it is the
form the repository's own contributors type, and it usually carries flags that matter.

## Reading a CI workflow

Take the `run:` lines (`script:` in GitLab, `sh`/`bat` steps in a `Jenkinsfile`), in the job
that is named for the lane. Two cautions:

- **Strip the CI-only flags.** `--reporter=github`, `--coverage`, `CI=true`, a matrix variable
  and an `--shard` argument belong to the runner, not to the command. Keep the rest verbatim.
- **A setup step is part of the command.** If the workflow runs an install or a codegen step
  before the gate, that step is a precondition, not an optimisation. Report it alongside, or the
  gate fails on a stale generated file and the failure gets blamed on the change.

## When the root and the package disagree

Walk **up** from the file that changed to the nearest manifest, then to the repository root.
Report both when they differ, and prefer the nearest one for a single-package change. If the
nearest manifest defines a lane and the root does not, that lane exists — for that package.

If a package defines no gate at all, say so per package rather than for the repository. "Two of
the four packages this change touches have no test command" is a usable fact. "The repository
has no test command" is not, and it is false.

## Reporting a stub

A gate that runs and proves nothing must be reported as proving nothing. The three shapes worth
naming explicitly, because all three exit 0:

- a test script that matches no files, or is `echo` plus `exit 0`
- a typecheck script that is a placeholder for a package nobody has migrated
- a lint script pinned to a warning ceiling high enough that nothing can fail

State it in the same line as the result: `test: pass (0 tests collected — the suite is empty)`.
Reporting that as a green gate is how a change ships with the appearance of coverage.
