#!/usr/bin/env python3
"""Structural linter for this marketplace.

`claude plugin validate` covers JSON syntax, manifest fields, skill frontmatter
and version drift between a marketplace entry and a plugin manifest. It does not
notice a plugin whose components sit in the wrong place, a manifest whose name
disagrees with its directory, a plugin nobody registered, or a hardcoded secret.
Those are the checks here — the ones that otherwise fail silently at install time.

Usage: python3 scripts/lint-structure.py [marketplace-root]
Exit code 1 if any error is reported; warnings alone do not fail the run.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

COMPONENT_DIRS = ("skills", "agents", "commands", "hooks", "workflows", "output-styles", "monitors")
CONFIG_FILES = ("hooks/hooks.json", ".mcp.json", ".lsp.json", "monitors/monitors.json")

# Absolute paths break for every user but the author: plugins install into
# ~/.claude/plugins/cache. ${CLAUDE_PLUGIN_ROOT} is the only portable form.
ABSOLUTE_PATH = re.compile(r'"(?:/Users/|/home/|/opt/|/private/|[A-Za-z]:\\\\)[^"]*"')

SECRET_PATTERNS = (
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI API key", re.compile(r"\bsk-[A-Za-z0-9]{32,}")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)

SCANNABLE_SUFFIXES = {".json", ".md", ".sh", ".py", ".js", ".ts", ".yml", ".yaml", ".toml", ".env"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, code: str, message: str) -> None:
        self.errors.append(f"{where}: [{code}] {message}")

    def warn(self, where: str, code: str, message: str) -> None:
        self.warnings.append(f"{where}: [{code}] {message}")


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def check_layout(plugin: Path, root: Path, report: Report) -> None:
    """Only plugin.json belongs in .claude-plugin/. Anything else there is dead weight:
    Claude Code will not discover it, and the plugin installs with no components."""
    meta = plugin / ".claude-plugin"
    if not meta.is_dir():
        return
    for entry in sorted(meta.iterdir()):
        if entry.name == "plugin.json":
            continue
        if entry.is_dir() and entry.name in COMPONENT_DIRS:
            report.error(
                rel(entry, root),
                "E001",
                f"'{entry.name}/' is nested inside .claude-plugin/. Move it to the plugin "
                "root — Claude Code will not discover it here and the plugin installs empty.",
            )
        else:
            report.warn(
                rel(entry, root),
                "W001",
                "unexpected file in .claude-plugin/ — only plugin.json belongs there.",
            )


def check_manifest(plugin: Path, root: Path, report: Report) -> dict | None:
    manifest_path = plugin / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        report.error(
            rel(plugin, root),
            "E002",
            "no .claude-plugin/plugin.json. Every plugin in this marketplace declares one.",
        )
        return None
    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        report.error(rel(manifest_path, root), "E003", f"invalid JSON: {exc}")
        return None

    name = manifest.get("name")
    if name != plugin.name:
        report.error(
            rel(manifest_path, root),
            "E004",
            f"manifest name '{name}' does not match directory '{plugin.name}'. The two must "
            "agree or the marketplace entry and the installed plugin disagree on identity.",
        )
    if not manifest.get("version"):
        report.warn(
            rel(manifest_path, root),
            "W002",
            "no version. Without one, users cannot be offered a controlled update.",
        )
    return manifest


def check_bin(plugin: Path, root: Path, report: Report) -> None:
    if (plugin / "bin").is_dir():
        report.warn(
            rel(plugin / "bin", root),
            "W003",
            "a top-level bin/ blocks distribution through claude.ai organization settings. "
            "Use scripts/ and call it as ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.",
        )


def check_absolute_paths(plugin: Path, root: Path, report: Report) -> None:
    for relative in CONFIG_FILES:
        config = plugin / relative
        if not config.is_file():
            continue
        for match in ABSOLUTE_PATH.finditer(config.read_text()):
            report.error(
                rel(config, root),
                "E005",
                f"absolute path {match.group(0)} — use ${{CLAUDE_PLUGIN_ROOT}} instead; "
                "plugins install into ~/.claude/plugins/cache on other machines.",
            )


def check_secrets(plugin: Path, root: Path, report: Report) -> None:
    for path in sorted(plugin.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNABLE_SUFFIXES:
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                report.error(
                    rel(path, root),
                    "E006",
                    f"looks like a committed {label}. Read it from the environment or "
                    "declare a sensitive userConfig field instead.",
                )


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    catalogue_path = root / ".claude-plugin" / "marketplace.json"
    report = Report()

    if not catalogue_path.is_file():
        print(f"error: no {rel(catalogue_path, root)}", file=sys.stderr)
        return 1
    try:
        catalogue = json.loads(catalogue_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"error: {rel(catalogue_path, root)} is invalid JSON: {exc}", file=sys.stderr)
        return 1

    entries = catalogue.get("plugins", [])
    registered: dict[str, dict] = {}
    for entry in entries:
        name = entry.get("name")
        if name:
            registered[name] = entry
        source = entry.get("source")
        if isinstance(source, str):
            if not (root / source).is_dir():
                report.error(
                    ".claude-plugin/marketplace.json",
                    "E007",
                    f"entry '{name}' points at '{source}', which does not exist.",
                )
        if "version" in entry:
            report.warn(
                ".claude-plugin/marketplace.json",
                "W004",
                f"entry '{name}' declares a version. This repository keeps version in "
                "plugin.json only, so the two cannot drift apart.",
            )

    plugins_dir = root / "plugins"
    directories = sorted(p for p in plugins_dir.iterdir() if p.is_dir()) if plugins_dir.is_dir() else []

    for plugin in directories:
        check_layout(plugin, root, report)
        check_manifest(plugin, root, report)
        check_bin(plugin, root, report)
        check_absolute_paths(plugin, root, report)
        check_secrets(plugin, root, report)
        if plugin.name not in registered:
            report.error(
                rel(plugin, root),
                "E008",
                "not registered in .claude-plugin/marketplace.json — a plugin that is not "
                "listed there cannot be installed.",
            )

    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}", file=sys.stderr)

    plural = "" if len(directories) == 1 else "s"
    print(
        f"\nChecked {len(directories)} plugin{plural}: "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
