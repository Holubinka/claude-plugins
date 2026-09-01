#!/usr/bin/env python3
"""
TypeScript Project Diagnostic Script
Analyzes TypeScript projects for configuration, performance, and common issues.

Three rules this script exists to obey, all of them from
`engineering-paved-path:project-commands`:

  1. Never assume a folder name. The sources are discovered — from tsconfig, then
     from git, then by walking. A repository whose code lives in `packages/*/src`,
     `app/`, or `lib/` is not a repository with no TypeScript in it.
  2. Every check has three outcomes, not two. "Nothing found" and "nothing looked
     at" print differently, because an empty grep and a missing directory used to
     print the same green tick — which is how a diagnostic reports a false clean.
  3. Never read a verdict through a pipe. `tsc | head` throws away the exit code,
     and the exit code is the verdict.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

# Directories that never hold reviewable source, regardless of repository shape.
EXCLUDED_DIRS = {
    "node_modules", "dist", "build", "out", "coverage", ".next", ".nuxt",
    ".svelte-kit", ".turbo", ".git", "vendor", "generated",
}
SOURCE_SUFFIXES = (".ts", ".tsx", ".mts", ".cts")

NOT_SCANNED = "not scanned"


def run(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a command as an argv list — no shell, no pipe, exit code preserved."""
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, 127, "", f"{args[0]}: not found")
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, "", "timed out")
    except OSError as exc:
        return subprocess.CompletedProcess(args, 126, "", str(exc))


def runner_prefix() -> tuple[list[str], str]:
    """Resolve the package runner from the lockfile at the repository root.

    Two lockfiles is a finding, not a coin toss: `packageManager` decides, and if
    it is absent the ambiguity is reported rather than guessed away."""
    lockfiles = {
        "pnpm-lock.yaml": (["pnpm", "exec"], "pnpm"),
        "yarn.lock": (["yarn"], "yarn"),
        "bun.lockb": (["bun", "x"], "bun"),
        "bun.lock": (["bun", "x"], "bun"),
        "package-lock.json": (["npx"], "npm"),
    }
    present = [name for name in lockfiles if Path(name).exists()]

    if len(present) > 1:
        declared = ""
        try:
            with open("package.json") as handle:
                declared = str(json.load(handle).get("packageManager", ""))
        except (OSError, json.JSONDecodeError):
            pass
        for name, (prefix, manager) in lockfiles.items():
            if name in present and declared.startswith(manager):
                return prefix, f"{manager} (packageManager, {len(present)} lockfiles present)"
        return [], f"ambiguous — {', '.join(sorted(present))} and no packageManager field"

    if present:
        prefix, manager = lockfiles[present[0]]
        return prefix, f"{manager} ({present[0]})"

    return ["npx"], "npm (no lockfile found)"


def tsc(prefix: list[str], local: bool, *args: str) -> subprocess.CompletedProcess:
    """Route through the package runner only when TypeScript is installed in the
    project. `npx tsc` against a global-only install refuses to run and exits 1,
    which reads exactly like a type error."""
    return run([*prefix, "tsc", *args] if local else ["tsc", *args])


def typescript_available() -> tuple[bool, str, bool]:
    """Is there a compiler to run at all? Answered structurally, not by parsing a
    runner's English. `npx tsc` in a project without TypeScript exits 1 with a
    friendly banner, which is indistinguishable from a type error to anything
    reading the exit code alone."""
    here = Path.cwd().resolve()
    for directory in [here, *here.parents]:
        if (directory / "node_modules" / "typescript" / "package.json").exists():
            return True, f"installed at {directory / 'node_modules' / 'typescript'}", True
        if (directory / ".git").exists():
            break

    on_path = shutil.which("tsc")
    if on_path:
        return True, f"{on_path} (global, not a project dependency)", False

    try:
        with open("package.json") as handle:
            pkg = json.load(handle)
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "typescript" in deps:
            return False, "declared in package.json but not installed — run an install first", False
    except (OSError, json.JSONDecodeError):
        pass

    return False, "no typescript in node_modules and no tsc on PATH", False


def unavailable(result: subprocess.CompletedProcess) -> bool:
    """Backstop for a command that never ran, as opposed to running and failing."""
    if result.returncode in (124, 126, 127):
        return True
    haystack = (result.stderr + result.stdout).lower()
    return any(
        needle in haystack
        for needle in ("not found", "no such file", "could not determine executable", "enoent")
    )


def tsconfig_roots(config: dict) -> list[str]:
    """Directories named by tsconfig, if it names any."""
    options = config.get("compilerOptions", {})
    roots: list[str] = []
    for entry in config.get("files", []) or []:
        roots.append(str(entry))
    for entry in config.get("include", []) or []:
        # Strip the glob tail: "packages/*/src/**/*.ts" -> "packages/*/src"
        head = str(entry).split("*")[0].rstrip("/")
        if head:
            roots.append(head)
    for key in ("rootDir", "baseUrl"):
        if options.get(key):
            roots.append(str(options[key]))
    return roots


def walk(base: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for filename in filenames:
            if filename.endswith(SOURCE_SUFFIXES) and not filename.endswith(".d.ts"):
                found.append(Path(dirpath) / filename)
    return found


def typescript_sources() -> tuple[list[Path], str]:
    """Discover the TypeScript sources. Returns (files, how they were found).

    Order: what tsconfig names, then what git tracks, then a walk from here.
    Never `src/`."""
    config_path = Path("tsconfig.json")
    if config_path.exists():
        try:
            with open(config_path) as handle:
                roots = tsconfig_roots(json.load(handle))
        except (OSError, json.JSONDecodeError):
            roots = []
        collected: list[Path] = []
        for root in roots:
            path = Path(root)
            if path.is_dir():
                collected.extend(walk(path))
            elif path.is_file() and path.suffix in SOURCE_SUFFIXES:
                collected.append(path)
        if collected:
            named = ", ".join(sorted({str(r) for r in roots})[:4])
            return sorted(set(collected)), f"tsconfig.json ({named})"

    tracked = run(["git", "ls-files", "*.ts", "*.tsx", "*.mts", "*.cts"])
    if tracked.returncode == 0 and tracked.stdout.strip():
        files = [
            Path(line)
            for line in tracked.stdout.splitlines()
            if line and not line.endswith(".d.ts")
            and not any(part in EXCLUDED_DIRS for part in Path(line).parts)
        ]
        if files:
            return sorted(set(files)), "git ls-files"

    walked = walk(Path("."))
    if walked:
        return sorted(set(walked)), "directory walk from the working directory"

    return [], "nothing found"


def scan(files: list[Path], predicate) -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                for number, line in enumerate(handle, 1):
                    if predicate(line):
                        hits.append((path, number, line.rstrip()))
        except OSError:
            continue
    return hits


def check_versions(prefix: list[str], how: str, has_ts: bool, where: str, local: bool):
    print("\n📦 Versions:")
    print("-" * 40)

    print(f"  Package runner: {how}")
    if not has_ts:
        print(f"  TypeScript: {NOT_SCANNED} — {where}")
    elif local and not prefix:
        print(f"  TypeScript: {NOT_SCANNED} — the runner is ambiguous")
    else:
        result = tsc(prefix, local, "--version")
        version = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        if unavailable(result) or not version:
            print(f"  TypeScript: {NOT_SCANNED} — tsc did not resolve")
        else:
            print(f"  TypeScript: {version}")

    node = run(["node", "-v"])
    print(f"  Node.js: {node.stdout.strip() or 'Not found'}")


def check_tsconfig():
    print("\n⚙️ TSConfig Analysis:")
    print("-" * 40)

    tsconfig_path = Path("tsconfig.json")
    if not tsconfig_path.exists():
        print("⚠️ tsconfig.json not found")
        return

    try:
        with open(tsconfig_path) as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in tsconfig.json")
        return

    compiler_opts = config.get("compilerOptions", {})

    if compiler_opts.get("strict"):
        print("✅ Strict mode enabled")
    else:
        print("⚠️ Strict mode NOT enabled")

    flags = {
        "noUncheckedIndexedAccess": "Unchecked index access protection",
        "noImplicitOverride": "Implicit override protection",
        "skipLibCheck": "Skip lib check (performance)",
        "incremental": "Incremental compilation",
    }
    for flag, desc in flags.items():
        status = "✅" if compiler_opts.get(flag) else "⚪"
        print(f"  {status} {desc}: {compiler_opts.get(flag, 'not set')}")

    print(f"\n  Module: {compiler_opts.get('module', 'not set')}")
    print(f"  Module Resolution: {compiler_opts.get('moduleResolution', 'not set')}")
    print(f"  Target: {compiler_opts.get('target', 'not set')}")

    if config.get("references"):
        print(f"  Project references: {len(config['references'])}")


def check_tooling():
    print("\n🛠️ Tooling Detection:")
    print("-" * 40)

    pkg_path = Path("package.json")
    if not pkg_path.exists():
        print("⚠️ package.json not found")
        return

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in package.json")
        return

    all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    tools = {
        "biome": "Biome (linter/formatter)",
        "eslint": "ESLint",
        "prettier": "Prettier",
        "vitest": "Vitest (testing)",
        "jest": "Jest (testing)",
        "turbo": "Turbo/Turborepo (monorepo)",
        "nx": "Nx (monorepo)",
        "lerna": "Lerna (monorepo)",
    }
    for tool, desc in tools.items():
        if any(tool in dep.lower() for dep in all_deps):
            print(f"  ✅ {desc}")

    scripts = pkg.get("scripts", {})
    if scripts:
        print(f"\n  Scripts defined: {', '.join(sorted(scripts)[:8])}")
        print("  Read a script's value before treating its exit code as evidence —")
        print('  "test": "echo no tests && exit 0" is real, and it is green.')


def check_monorepo():
    print("\n📦 Monorepo Check:")
    print("-" * 40)

    indicators = [
        ("pnpm-workspace.yaml", "PNPM Workspace"),
        ("lerna.json", "Lerna"),
        ("nx.json", "Nx"),
        ("turbo.json", "Turborepo"),
    ]
    found = False
    for file, name in indicators:
        if Path(file).exists():
            print(f"  ✅ {name} detected")
            found = True

    if not found:
        print("  ⚪ No monorepo configuration detected")


def check_sources(files: list[Path], how: str):
    print("\n📄 Sources:")
    print("-" * 40)
    if not files:
        print(f"  ⚠️ {NOT_SCANNED} — no TypeScript sources found ({how})")
        return
    print(f"  {len(files)} TypeScript files, found via {how}")


def check_any_usage(files: list[Path], how: str):
    print("\n⚠️ 'any' Type Usage:")
    print("-" * 40)

    if not files:
        print(f"  ⚠️ {NOT_SCANNED} — no TypeScript sources found ({how})")
        return

    hits = scan(files, lambda line: ": any" in line)
    if hits:
        print(f"  ⚠️ Found {len(hits)} occurrences of ': any'")
        for path, number, text in hits[:5]:
            print(f"    {path}:{number}: {text.strip()[:100]}")
    else:
        print(f"  ✅ No explicit 'any' types found across {len(files)} files")


def check_type_assertions(files: list[Path], how: str):
    print("\n⚠️ Type Assertions (as):")
    print("-" * 40)

    if not files:
        print(f"  ⚠️ {NOT_SCANNED} — no TypeScript sources found ({how})")
        return

    def is_assertion(line: str) -> bool:
        stripped = line.lstrip()
        if stripped.startswith(("import", "export", "//", "*")):
            return False
        return " as " in line and " as const" not in line

    hits = scan(files, is_assertion)
    if hits:
        print(f"  ⚠️ Found {len(hits)} type assertions ('as const' excluded)")
        for path, number, text in hits[:5]:
            print(f"    {path}:{number}: {text.strip()[:100]}")
    else:
        print(f"  ✅ No type assertions found across {len(files)} files")


def check_type_errors(prefix: list[str], files: list[Path], has_ts: bool, where: str, local: bool):
    print("\n🔍 Type Check:")
    print("-" * 40)

    if not has_ts:
        print(f"  ⚠️ {NOT_SCANNED} — {where}")
        return
    if local and not prefix:
        print(f"  ⚠️ {NOT_SCANNED} — the package runner is ambiguous")
        return
    if not Path("tsconfig.json").exists() and not files:
        print(f"  ⚠️ {NOT_SCANNED} — no tsconfig.json and no TypeScript sources")
        return

    result = tsc(prefix, local, "--noEmit")
    if unavailable(result):
        print(f"  ⚠️ {NOT_SCANNED} — tsc did not resolve. Run this from the workspace")
        print("     root that owns TypeScript.")
        return

    output = result.stdout + result.stderr
    if result.returncode == 0:
        print("  ✅ No type errors (tsc exited 0)")
        return

    errors = output.count("error TS")
    print(f"  ❌ tsc exited {result.returncode}" + (f", {errors} errors" if errors else ""))
    print("\n".join(output.splitlines()[:20]))


def check_performance(prefix: list[str], has_ts: bool, where: str, local: bool):
    print("\n⏱️ Type Check Performance:")
    print("-" * 40)

    if not has_ts:
        print(f"  ⚠️ {NOT_SCANNED} — {where}")
        return
    if local and not prefix:
        print(f"  ⚠️ {NOT_SCANNED} — the package runner is ambiguous")
        return

    result = tsc(prefix, local, "--extendedDiagnostics", "--noEmit")
    if unavailable(result):
        print(f"  ⚠️ {NOT_SCANNED} — tsc did not resolve")
        return

    wanted = ("Check time", "Files:", "Lines:", "Nodes:", "Total time")
    lines = [
        line for line in (result.stdout + result.stderr).splitlines()
        if any(line.strip().startswith(w) for w in wanted)
    ]
    if lines:
        for line in lines:
            print(f"  {line.strip()}")
    else:
        print("  ⚠️ Could not measure performance — tsc ran but reported no diagnostics")


def main():
    print("=" * 50)
    print("🔍 TypeScript Project Diagnostic Report")
    print("=" * 50)

    prefix, how_runner = runner_prefix()
    files, how_sources = typescript_sources()
    has_ts, where_ts, local_ts = typescript_available()

    check_versions(prefix, how_runner, has_ts, where_ts, local_ts)
    check_tsconfig()
    check_tooling()
    check_monorepo()
    check_sources(files, how_sources)
    check_any_usage(files, how_sources)
    check_type_assertions(files, how_sources)
    check_type_errors(prefix, files, has_ts, where_ts, local_ts)
    check_performance(prefix, has_ts, where_ts, local_ts)

    print("\n" + "=" * 50)
    print("✅ Diagnostic Complete")
    print("=" * 50)
    print("Anything marked 'not scanned' was never looked at. It is not a pass.")


if __name__ == "__main__":
    main()
