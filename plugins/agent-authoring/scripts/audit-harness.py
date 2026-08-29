#!/usr/bin/env python3
"""Static audit of a set of skills and agents, for the claims they make about each other.

No model, no network, no execution — it parses frontmatter and prose and checks four
things that have each drifted in a real set at least once:

  A1  a description promises a roster the body never dispatches
  A2  a fan-out table lists lanes without saying when each one runs
  A3  a fan-out of two or more does not require a single-message dispatch
  A4  a backticked `plugin:name` does not resolve, or names a plugin the manifest
      does not declare a dependency on

Usage:
    audit-harness.py <path> [<path> ...]

A path may be a marketplace's `plugins/` directory, a single plugin directory, or a
project's `.claude/` directory. Skills are read from `skills/<name>/SKILL.md`, agents
from `agents/<name>.md`.

Exit status is 1 if any FAIL was reported, 0 otherwise. Warnings never fail the run:
a check that blocks on a judgement call gets disabled, and then it checks nothing.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# A fan-out table column that answers "when does this lane run?".
CONDITION_HEADERS = re.compile(
    r"\b(when|runs? when|condition|fires? when|applies? when|trigger|dispatch when|only if)\b",
    re.I,
)
# The instruction that makes concurrent agents actually concurrent.
SINGLE_MESSAGE = re.compile(
    r"(single|one|the same)\s+(message|turn|block|response)"
    r"|in\s+one\s+message"
    r"|all\s+(of\s+them\s+)?in\s+(one|a\s+single)\b",
    re.I,
)
# `plugin-name:component-name`, the namespaced form, optionally as a /invocation.
NAMESPACED = re.compile(r"`(/?)([a-z0-9][a-z0-9-]*):([a-z0-9][a-z0-9-]*)`")
# A dispatch, as opposed to a mention. A name in prose is not a promise to spawn it.
DISPATCH_VERB = re.compile(
    r"\b(dispatch|spawn|invoke|call|run|use)\b.{0,80}?\bagent\b"
    r"|\bagent\b.{0,80}?\b(dispatch|spawn|invoke|call|run|use)\b"
    r"|\bAgent\s*\(|\bSkill\s*\(",
    re.I,
)
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")


@dataclass
class Component:
    kind: str
    name: str
    plugin: str | None
    path: Path
    description: str
    body: str
    declares: frozenset[str] = frozenset()

    @property
    def qualified(self) -> str:
        return f"{self.plugin}:{self.name}" if self.plugin else self.name


@dataclass
class Report:
    root: Path
    fails: int = 0
    warns: int = 0
    lines: list[str] = field(default_factory=list)

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)

    def fail(self, path: Path, code: str, message: str) -> None:
        self.fails += 1
        self.lines.append(f"FAIL {code} {self._rel(path)}: {message}")

    def warn(self, path: Path, code: str, message: str) -> None:
        self.warns += 1
        self.lines.append(f"warn {code} {self._rel(path)}: {message}")


def frontmatter_of(text: str) -> tuple[dict[str, str], str]:
    """A deliberately small YAML reader: top-level `key: value` pairs only.

    Skills and agents use a flat frontmatter, and depending on a YAML library would
    make this script refuse to run in the environments it is most useful in."""
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    fields: dict[str, str] = {}
    key = None
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if line[:1] in " \t" and key:                    # a continuation of the previous value
            fields[key] += " " + line.strip()
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        fields[key] = value.strip().strip('"').strip("'")
    return fields, text[match.end():]


def collect(root: Path) -> list[Component]:
    """Find skills and agents under a plugins tree, a plugin, or a .claude directory."""
    found: list[Component] = []

    def declared(base: Path) -> frozenset[str]:
        """Which plugins this one's manifest says it depends on. A backticked cross-plugin
        name is a promise it resolves at install time, and only a declared dependency keeps
        that promise — co-presence in one repository does not."""
        manifest = base / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            return frozenset()
        try:
            data = json.loads(manifest.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            return frozenset()
        names = set()
        for dep in data.get("dependencies") or []:
            if isinstance(dep, str):
                names.add(dep)
            elif isinstance(dep, dict) and dep.get("name"):
                names.add(str(dep["name"]))
        return frozenset(names)

    def add(path: Path, kind: str, name: str, plugin: str | None, declares: frozenset) -> None:
        fields, body = frontmatter_of(path.read_text(encoding="utf-8", errors="replace"))
        found.append(
            Component(
                kind=kind,
                name=fields.get("name", name),
                plugin=plugin,
                path=path,
                description=fields.get("description", ""),
                body=body,
                declares=declares,
            )
        )

    def scan(base: Path, plugin: str | None) -> None:
        deps = declared(base)
        for skill in sorted(base.glob("skills/*/SKILL.md")):
            add(skill, "skill", skill.parent.name, plugin, deps)
        for agent in sorted(base.glob("agents/*.md")):
            if agent.name.upper() == "README.MD":
                continue
            add(agent, "agent", agent.stem, plugin, deps)

    if (root / "skills").is_dir() or (root / "agents").is_dir():
        plugin = root.name if (root / ".claude-plugin" / "plugin.json").exists() else None
        scan(root, plugin)

    for child in sorted(p for p in root.iterdir() if p.is_dir()):
        if (child / "skills").is_dir() or (child / "agents").is_dir():
            plugin = child.name if (child / ".claude-plugin" / "plugin.json").exists() else None
            scan(child, plugin)

    return found


def tables(body: str) -> list[list[str]]:
    """Group consecutive markdown table rows into tables, outside fenced code."""
    out: list[list[str]] = []
    current: list[str] = []
    fenced = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if TABLE_ROW.match(line):
            current.append(line)
        elif current:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def strip_fences(body: str) -> str:
    return re.sub(r"```.*?```", "", body, flags=re.S)


def check(components: list[Component], report: Report) -> None:
    known = {c.qualified for c in components} | {c.name for c in components}
    agents = {c.name for c in components if c.kind == "agent"}
    plugins = {c.plugin for c in components if c.plugin}
    names = {c.name for c in components}

    for component in components:
        prose = strip_fences(component.body)

        # A4 — a backticked `plugin:name` is a promise that it resolves. Only a name whose
        # left side is a plugin in the set, or a /invocation, is making that promise:
        # `path:line` and `node:fs` are idioms, not references.
        for slash, plugin, name in set(NAMESPACED.findall(component.body)):
            if f"{plugin}:{name}" in known:
                # It resolves in this set — but resolving here is not resolving at install
                # time. Only a declared dependency makes the promise keepable.
                if (
                    component.plugin
                    and plugin != component.plugin
                    and plugin in plugins
                    and plugin not in component.declares
                ):
                    report.fail(
                        component.path, "A4",
                        f"`{plugin}:{name}` is named, but {component.plugin}'s manifest declares "
                        f"no dependency on '{plugin}'. It resolves in this repository and would "
                        "not at install time",
                    )
                continue
            if plugin in plugins:
                report.fail(
                    component.path, "A4",
                    f"`{plugin}:{name}` — plugin '{plugin}' is in the set and has no '{name}'",
                )
            elif slash or name in names:
                report.warn(
                    component.path, "A4",
                    f"`{'/' if slash else ''}{plugin}:{name}` is not in the audited set; "
                    "it needs a declared dependency on that plugin",
                )

        # Which agents does this component actually name, and which does it dispatch?
        named = {a for a in agents if a != component.name and re.search(rf"\b{re.escape(a)}\b", prose)}
        dispatched = {
            a for a in named
            if any(
                re.search(rf"\b{re.escape(a)}\b", line) and DISPATCH_VERB.search(line)
                for line in prose.splitlines()
            )
        }

        # A1 — a description must not promise a roster the body never dispatches.
        promised = {a for a in agents if a != component.name and re.search(rf"\b{re.escape(a)}\b", component.description)}
        missing = promised - named
        if missing:
            report.fail(
                component.path, "A1",
                "description names " + ", ".join(sorted(missing))
                + " but the body never dispatches them",
            )

        # A1b — a name listed in the description alongside real components, that exists
        # nowhere. The roster outlived the component; only the description still says so.
        for sentence in re.split(r"(?<=[.!?])\s+", component.description):
            if not any(re.search(rf"\b{re.escape(n)}\b", sentence) for n in named | promised):
                continue
            for token in set(re.findall(r"\b[a-z][a-z0-9]*(?:-[a-z0-9]+)+\b", sentence)):
                if token in known or token == component.name:
                    continue
                if re.search(rf"\b{re.escape(token)}\b", prose):
                    continue
                report.fail(
                    component.path, "A1",
                    f"description lists '{token}' beside real components, but nothing by that "
                    "name exists and the body never mentions it",
                )

        # A2 — a table listing two or more lanes must say when each one runs.
        for table in tables(prose):
            header = table[0]
            rows = "\n".join(table[1:])
            in_header = {a for a in agents if re.search(rf"\b{re.escape(a)}\b", header)}
            # Lanes named in the header are columns of a comparison, not rows of a fan-out.
            listed = {a for a in agents if re.search(rf"\b{re.escape(a)}\b", rows)} - in_header
            if len(listed) < 2:
                continue
            first_cell = header.strip().strip("|").split("|")[0]
            if CONDITION_HEADERS.search(header) or CONDITION_HEADERS.search(first_cell):
                continue
            report.fail(
                component.path, "A2",
                f"a table lists {len(listed)} lanes ({', '.join(sorted(listed))}) with no column "
                "saying when each one runs",
            )
            break

        # A3 — a fan-out of two or more must require one message, or it runs in series.
        if len(dispatched) >= 2 and not SINGLE_MESSAGE.search(prose):
            report.warn(
                component.path, "A3",
                f"dispatches {len(dispatched)} agents ({', '.join(sorted(dispatched))}) without "
                "requiring a single-message dispatch — they will run in series",
            )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip())
        return 2

    total = 0
    fails = 0
    warns = 0
    for raw in argv[1:]:
        root = Path(raw).resolve()
        if not root.is_dir():
            print(f"FAIL --  {raw}: not a directory")
            fails += 1
            continue
        components = collect(root)
        report = Report(root=root)
        check(components, report)
        for line in report.lines:
            print(line)
        total += len(components)
        fails += report.fails
        warns += report.warns

    print(f"Audited {total} component(s): {fails} fail(s), {warns} warning(s).")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
