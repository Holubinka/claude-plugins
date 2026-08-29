#!/usr/bin/env python3
"""Builds the catalogue site's data from the repository.

Everything the site shows is derived here: the marketplace manifest, every plugin's
components, the repository docs, and the git history behind them. The site is a dumb
consumer of the JSON this writes, so nothing about the repository layout leaks into
the Astro app.

It doubles as a metadata check. `--check` reports the same E1xx/W1xx codes without
writing anything, which is what runs on pull requests that never deploy — see
docs/tmp/site.md. Codes live at 1xx so they never collide with lint-structure.py's
E001-E008 and W001-W004.

Usage: python3 scripts/build-index.py [marketplace-root] [--check] [--site-dir DIR]
Exit code 1 if any error is reported; warnings alone do not fail the run.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

# The branch blob links point at. A published site should reference a stable ref,
# not whatever commit CI happens to be building.
BLOB_REF = "main"

DOC_FILES = ("README.md", "CONTRIBUTING.md")

# Skill descriptions are meant to read as trigger conditions, not summaries
# (docs/plugin-structure.md). W104 looks for any sign of one.
TRIGGER_HINTS = ("use when", "when the user", "for when", "trigger", "invoke when", "call when")

# Two skills whose descriptions overlap this much will both fire unreliably.
COLLISION_THRESHOLD = 0.55

# Past the first budget the search payload wants splitting into tiers; past the
# second it is no longer a defensible thing to ship at all.
INDEX_SPLIT_BYTES = 150 * 1024
INDEX_FAIL_BYTES = 400 * 1024

STOPWORDS = frozenset("""
a an and are as at be by for from has have how in into is it its of on or that the
this to use used uses user when where which who will with without you your not no
""".split())

# Components the manifest may relocate. Only `skills` adds to the default scan;
# every other field replaces it outright, which is easy to get wrong by hand and
# would otherwise make the site list components the install does not have.
ADDITIVE_FIELDS = {"skills"}

TOKENED_TYPES = ("skill", "agent", "command")

VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.\-]+))?(?:\+[0-9A-Za-z.\-]+)?$")
RANGE_RE = re.compile(
    r"^(>=|<=|>|<|=|\^|~)?\s*v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([0-9A-Za-z.\-]+))?$"
)
WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-]*")
NON_PROSE = re.compile(r"^(```|\||>|#|[-*+]\s|\d+[.)]\s)")
INLINE_MARKDOWN = (
    (re.compile(r"!\[[^\]]*\]\([^)]*\)"), ""),
    (re.compile(r"\[([^\]]+)\]\([^)]*\)"), r"\1"),
    (re.compile(r"`([^`]+)`"), r"\1"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"\1"),
    (re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)"), r"\1"),
)
PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s\"']+)")


# --------------------------------------------------------------------------- report


class Report:
    """Findings, keyed by plugin so they can be rendered as health badges."""

    def __init__(self) -> None:
        self.entries: list[dict] = []

    def error(self, where: str, code: str, message: str, plugin: str | None = None) -> None:
        self.entries.append(
            {"level": "error", "where": where, "code": code, "message": message, "plugin": plugin}
        )

    def warn(self, where: str, code: str, message: str, plugin: str | None = None) -> None:
        self.entries.append(
            {"level": "warn", "where": where, "code": code, "message": message, "plugin": plugin}
        )

    @property
    def errors(self) -> list[dict]:
        return [e for e in self.entries if e["level"] == "error"]

    @property
    def warnings(self) -> list[dict]:
        return [e for e in self.entries if e["level"] == "warn"]

    def health(self, plugin: str) -> list[dict]:
        return [
            {"code": e["code"], "level": e["level"], "message": e["message"]}
            for e in self.entries
            if e["plugin"] == plugin
        ]


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# ----------------------------------------------------------------------- frontmatter


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Read the leading `---` block. Frontmatter in this repository is flat keys,
    simple lists and the occasional block scalar, so a real YAML dependency would
    buy nothing a build script needs."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
    if end is None:
        return {}, text

    data: dict = {}
    key: str | None = None
    block: list[str] | None = None
    block_fold = False
    items: list[str] | None = None

    def flush() -> None:
        nonlocal key, block, items, block_fold
        if key is not None:
            if block is not None:
                joined = " ".join(l.strip() for l in block if l.strip()) if block_fold else "\n".join(block)
                data[key] = joined.strip()
            elif items is not None:
                data[key] = items
        key, block, items, block_fold = None, None, None, False

    for raw in lines[1:end]:
        if block is not None and (raw.startswith("  ") or not raw.strip()):
            block.append(raw[2:] if raw.startswith("  ") else "")
            continue
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and items is not None:
            items.append(scalar(stripped[2:]))
            continue
        if ":" not in stripped:
            continue
        flush()
        name, _, value = stripped.partition(":")
        key = name.strip()
        value = value.strip()
        if value in ("|", "|-", ">", ">-"):
            block, block_fold = [], value.startswith(">")
        elif value == "":
            items = []
        elif value.startswith("[") and value.endswith("]"):
            data[key] = [scalar(p) for p in value[1:-1].split(",") if p.strip()]
            key = None
        else:
            data[key] = scalar(value)
            key = None
    flush()

    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return data, body


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [p.strip() for p in str(value).split(",") if p.strip()]


def estimate_tokens(text: str) -> int:
    """Roughly four characters to a token. Rendered with a `≈` and footnoted on the
    site; it is never presented as exact."""
    return math.ceil(len(text) / 4) if text else 0


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-") or "section"


def first_sentence(text: str, limit: int = 220) -> str:
    """The lead paragraph of a doc section, as a card would show it: prose only, with
    inline markdown flattened so the snippet reads as a sentence rather than source."""
    para = ""
    for block in text.split("\n\n"):
        block = block.strip()
        if block and not NON_PROSE.match(block):
            para = " ".join(block.split())
            break
    if not para:
        para = " ".join(text.split())
    for pattern, replacement in INLINE_MARKDOWN:
        para = pattern.sub(replacement, para)
    cut = para[:limit]
    return cut if len(para) <= limit else cut.rsplit(" ", 1)[0] + "…"


def load_json(path: Path, root: Path, report: Report, plugin: str | None = None):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        report.error(rel(path, root), "E105", f"invalid JSON: {exc}", plugin)
    except OSError as exc:
        report.error(rel(path, root), "E105", f"unreadable: {exc}", plugin)
    return None


# ------------------------------------------------------------------------------ git


def git(root: Path, *args: str) -> str | None:
    try:
        done = subprocess.run(
            ("git", "-C", str(root)) + args,
            capture_output=True, text=True, check=False,
        )
    except (OSError, ValueError):
        return None
    return done.stdout.rstrip("\n") if done.returncode == 0 else None


def commit_dates(root: Path) -> dict[str, str]:
    """Newest commit date per path, from one walk of the log rather than a
    subprocess per artifact."""
    log = git(root, "log", "--pretty=format:%x00%cI", "--name-only")
    if not log:
        return {}
    dates: dict[str, str] = {}
    current = None
    for line in log.splitlines():
        if line.startswith("\x00"):
            current = line[1:].strip()
        elif line.strip() and current:
            dates.setdefault(line.strip(), current)
    return dates


def repo_slug(root: Path, catalogue: dict) -> str | None:
    remote = git(root, "remote", "get-url", "origin")
    if remote:
        match = re.search(r"(?:github\.com[:/])([^/]+/[^/\s]+?)(?:\.git)?$", remote.strip())
        if match:
            return match.group(1)
    owner = (catalogue.get("owner") or {}).get("url", "")
    match = re.search(r"github\.com/([^/\s]+)", owner)
    return f"{match.group(1)}/{root.name}" if match else None


def releases(root: Path, plugin: str, tags: dict[str, list[tuple]]) -> list[dict]:
    """Version, date and the commit subjects touching this plugin since the previous
    tag. Tags are `{plugin}--v{version}` so one repository can host several plugins
    on independent version lines (docs/releasing.md)."""
    out = []
    entries = tags.get(plugin, [])
    for index, (version, tag, date) in enumerate(entries):
        previous = entries[index - 1][1] if index else None
        span = f"{previous}..{tag}" if previous else tag
        log = git(root, "log", "--format=%s", span, "--", f"plugins/{plugin}") or ""
        out.append(
            {
                "version": ".".join(str(p) for p in version[:3]) + (f"-{version[3]}" if version[3] else ""),
                "tag": tag,
                "date": date,
                "changes": [line for line in log.splitlines() if line.strip()][:20],
            }
        )
    out.reverse()
    return out


def plugin_tags(root: Path) -> dict[str, list[tuple]]:
    listing = git(root, "for-each-ref", "--format=%(refname:short)%09%(creatordate:iso-strict)", "refs/tags")
    if not listing:
        return {}
    found: dict[str, list[tuple]] = {}
    for line in listing.splitlines():
        tag, _, date = line.partition("\t")
        name, sep, version_text = tag.rpartition("--v")
        if not sep:
            continue
        version = parse_version(version_text)
        if version:
            found.setdefault(name, []).append((version, tag, date.strip()))
    for entries in found.values():
        entries.sort(key=lambda entry: version_key(entry[0]))
    return found


# --------------------------------------------------------------------------- semver


def parse_version(text: str):
    match = VERSION_RE.match(str(text).strip())
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)), match.group(4))


def version_key(version):
    core, pre = version[:3], version[3]
    # A release outranks any prerelease of the same core version.
    return (core, 1 if pre is None else 0, pre or "")


def parse_range(text: str):
    """Bounds for the range forms docs/plugin-structure.md documents: ~2.1.0, ^2.0,
    >=1.4, =2.1.0 and a bare version. Returns None for anything else, which the
    caller treats as unresolvable rather than guessing."""
    match = RANGE_RE.match(str(text).strip())
    if not match:
        return None
    op = match.group(1) or "="
    major = int(match.group(2))
    minor = int(match.group(3)) if match.group(3) is not None else None
    patch = int(match.group(4)) if match.group(4) is not None else None
    pre = match.group(5)
    base = (major, minor or 0, patch or 0, pre)
    allows_pre = pre is not None

    if op in (">=", ">", "<=", "<"):
        if op.startswith(">"):
            return (base, op == ">=", None, False, allows_pre)
        return (None, False, base, op == "<=", allows_pre)
    if op == "^":
        upper = (major + 1, 0, 0, None) if major else (
            (0, (minor or 0) + 1, 0, None) if minor is not None else (1, 0, 0, None)
        )
        return (base, True, upper, False, allows_pre)
    if op == "~":
        upper = (major, (minor or 0) + 1, 0, None) if minor is not None else (major + 1, 0, 0, None)
        return (base, True, upper, False, allows_pre)
    # `=` and bare: exact when fully specified, otherwise the implied range.
    if patch is not None:
        return (base, True, base, True, allows_pre)
    upper = (major, minor + 1, 0, None) if minor is not None else (major + 1, 0, 0, None)
    return (base, True, upper, False, allows_pre)


def satisfies(version, spec) -> bool:
    lower, lower_ok, upper, upper_ok, allows_pre = spec
    if version[3] is not None and not allows_pre:
        return False  # prereleases are excluded unless the range opts in
    key = version_key(version)
    if lower is not None:
        low = version_key(lower)
        if key < low or (key == low and not lower_ok):
            return False
    if upper is not None:
        high = version_key(upper)
        if key > high or (key == high and not upper_ok):
            return False
    return True


# ---------------------------------------------------------------------- components


def component_paths(plugin: Path, manifest: dict, field: str, subdir: str, pattern: str) -> list[Path]:
    """Resolve where a component type lives, honouring the manifest override. The
    add-versus-replace split is the manifest's sharpest edge: setting `agents` stops
    `agents/` being scanned at all."""
    declared = manifest.get(field)
    found: list[Path] = []

    if declared is None or field in ADDITIVE_FIELDS:
        directory = plugin / subdir
        if directory.is_dir():
            found += sorted(p for p in directory.glob(pattern) if p.is_file())

    for entry in as_list(declared):
        target = (plugin / entry.lstrip("./")).resolve()
        if target.is_dir():
            found += sorted(p for p in target.glob(pattern) if p.is_file())
        elif target.is_file():
            found.append(target)

    unique: list[Path] = []
    for path in found:
        if path not in unique:
            unique.append(path)
    return unique


def read_component(path: Path, plugin_name: str, kind: str, root: Path, subdir: str) -> dict:
    text = path.read_text()
    front, body = split_frontmatter(text)
    name = path.parent.name if subdir == "skills" else path.stem
    description = str(front.get("description") or "").strip()
    return {
        "id": f"{kind}:{plugin_name}/{name}",
        "type": kind,
        "plugin": plugin_name,
        "name": name,
        "title": str(front.get("name") or name),
        "invocation": f"/{plugin_name}:{name}" if kind in ("skill", "command") else None,
        "description": description,
        "keywords": as_list(front.get("keywords")),
        "body": body,
        "headings": re.findall(r"^#{2,3}\s+(.+)$", body, re.M),
        "path": rel(path, root),
        "url": f"/p/{plugin_name}/{kind}/{name}/",
        "tokens": {"always": estimate_tokens(description), "onLoad": estimate_tokens(body)},
        "frontmatter": front,
        "referencedFiles": sorted(set(re.findall(r"\]\((?!https?:|#)([^)]+)\)", body))),
    }


def capabilities(plugin: Path, root: Path, report: Report, name: str, skills: list[dict]) -> dict:
    events: list[str] = []
    commands: list[str] = []
    servers: list[dict] = []
    lsp: list[dict] = []
    hosts: set[str] = set()

    hooks_path = plugin / "hooks" / "hooks.json"
    if hooks_path.is_file():
        data = load_json(hooks_path, root, report, name) or {}
        table = data.get("hooks") if isinstance(data.get("hooks"), dict) else data
        for event, matchers in sorted((table or {}).items()):
            events.append(event)
            for matcher in matchers if isinstance(matchers, list) else []:
                for hook in (matcher or {}).get("hooks", []):
                    if isinstance(hook, dict) and hook.get("command"):
                        commands.append(str(hook["command"]))

    mcp_path = plugin / ".mcp.json"
    if mcp_path.is_file():
        data = load_json(mcp_path, root, report, name) or {}
        for server, config in sorted((data.get("mcpServers") or {}).items()):
            config = config if isinstance(config, dict) else {}
            url = config.get("url")
            host = urlparse(url).hostname if url else None
            if host:
                hosts.add(host)
            servers.append(
                {
                    "name": server,
                    "transport": config.get("type") or config.get("transport") or ("stdio" if config.get("command") else "http"),
                    "command": config.get("command"),
                    "args": config.get("args") or [],
                    # Key names only. A build script has no business reading values.
                    "envKeys": sorted((config.get("env") or {}).keys()),
                    "url": url,
                    "host": host,
                }
            )

    lsp_path = plugin / ".lsp.json"
    if lsp_path.is_file():
        data = load_json(lsp_path, root, report, name) or {}
        for server, config in sorted((data.get("lspServers") or {}).items()):
            config = config if isinstance(config, dict) else {}
            lsp.append({"name": server, "command": config.get("command"), "args": config.get("args") or []})

    scripts = {ref for command in commands for ref in PLUGIN_ROOT_REF.findall(command)}
    if (plugin / "scripts").is_dir():
        scripts.update(rel(p, plugin) for p in sorted((plugin / "scripts").rglob("*")) if p.is_file())

    tools: set[str] = set()
    for skill in skills:
        front = skill["frontmatter"]
        tools.update(as_list(front.get("allowed-tools") or front.get("allowedTools")))

    return {
        "interceptsEvents": events,
        "hookCommands": commands,
        "mcpServers": servers,
        "lspServers": lsp,
        "networkHosts": sorted(hosts),
        "bundledScripts": sorted(scripts),
        "allowedTools": sorted(tools),
    }


def derived_artifacts(name: str, caps: dict, plugin: Path, root: Path) -> list[dict]:
    """Hook sets and servers are artifacts too — they are what a reader most wants to
    find when asking what a plugin does to their machine — but they carry no authored
    description, so theirs is stated from the configuration."""
    out = []
    if caps["interceptsEvents"]:
        events = ", ".join(caps["interceptsEvents"])
        out.append(
            {
                "id": f"hook:{name}/hooks", "type": "hook", "plugin": name, "name": "hooks",
                "title": "hooks", "invocation": None,
                "description": f"Intercepts {events}.",
                "keywords": [e.lower() for e in caps["interceptsEvents"]],
                "body": "\n".join(caps["hookCommands"]),
                "headings": [], "path": rel(plugin / "hooks" / "hooks.json", root),
                "url": f"/p/{name}/hook/hooks/", "tokens": None,
                "frontmatter": {}, "referencedFiles": [],
            }
        )
    for server in caps["mcpServers"]:
        target = server["host"] or server["command"] or "local process"
        out.append(
            {
                "id": f"mcp:{name}/{server['name']}", "type": "mcp", "plugin": name,
                "name": server["name"], "title": server["name"], "invocation": None,
                "description": f"MCP server over {server['transport']}, run as {target}.",
                "keywords": ["mcp", server["transport"]],
                "body": " ".join([server.get("command") or ""] + list(server.get("args") or [])),
                "headings": [], "path": rel(plugin / ".mcp.json", root),
                "url": f"/p/{name}/mcp/{server['name']}/", "tokens": None,
                "frontmatter": {}, "referencedFiles": [],
            }
        )
    for server in caps["lspServers"]:
        out.append(
            {
                "id": f"lsp:{name}/{server['name']}", "type": "lsp", "plugin": name,
                "name": server["name"], "title": server["name"], "invocation": None,
                "description": f"LSP server, run as {server.get('command') or 'a local process'}.",
                "keywords": ["lsp"], "body": "", "headings": [],
                "path": rel(plugin / ".lsp.json", root),
                "url": f"/p/{name}/lsp/{server['name']}/", "tokens": None,
                "frontmatter": {}, "referencedFiles": [],
            }
        )
    return out


# --------------------------------------------------------------------------- docs


def doc_artifacts(root: Path) -> list[dict]:
    """Repository docs, split at `##` so a search hit lands on the section that
    answers the question rather than the top of a long page."""
    sources = [root / f for f in DOC_FILES] + sorted((root / "docs").glob("*.md"))
    out = []
    for path in sources:
        if not path.is_file():
            continue
        slug = slugify(path.stem)
        lines = path.read_text().splitlines()
        title = next((l[2:].strip() for l in lines if l.startswith("# ")), path.stem)

        sections: list[tuple[str, int, list[str]]] = [(title, 1, [])]
        for number, line in enumerate(lines, start=1):
            if line.startswith("## "):
                sections.append((line[3:].strip(), number, []))
            elif not line.startswith("# "):
                sections[-1][2].append(line)

        for heading, line_number, content in sections:
            body = "\n".join(content).strip()
            if not body:
                continue
            anchor = slugify(heading)
            out.append(
                {
                    "id": f"doc:{slug}#{anchor}", "type": "doc", "plugin": None,
                    "name": anchor, "title": heading, "invocation": None,
                    "description": first_sentence(body),
                    "keywords": [], "body": body,
                    "headings": re.findall(r"^#{3}\s+(.+)$", body, re.M),
                    "path": rel(path, root), "line": line_number,
                    "url": f"/docs/{slug}/#{anchor}", "tokens": None,
                    "frontmatter": {}, "referencedFiles": [],
                    "doc": {"slug": slug, "title": title},
                }
            )
    return out


# --------------------------------------------------------------------- collisions


def tokenize(text: str) -> list[str]:
    return [w for w in WORD_RE.findall(text.lower()) if len(w) > 1 and w not in STOPWORDS]


def collisions(skills: list[dict]) -> list[dict]:
    """Overlapping triggers are the failure mode that makes two good skills both
    unreliable, and nothing else in the toolchain looks for them. TF-IDF cosine over
    the descriptions, which is what the triggers actually are."""
    documents = [(s, tokenize(s["description"])) for s in skills if s["description"]]
    if len(documents) < 2:
        return []

    total = len(documents)
    frequency: dict[str, int] = {}
    for _, words in documents:
        for word in set(words):
            frequency[word] = frequency.get(word, 0) + 1

    vectors = []
    for skill, words in documents:
        counts: dict[str, int] = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        vector = {
            word: (1 + math.log(count)) * (math.log((total + 1) / (frequency[word] + 1)) + 1)
            for word, count in counts.items()
        }
        norm = math.sqrt(sum(v * v for v in vector.values())) or 1.0
        vectors.append((skill, {w: v / norm for w, v in vector.items()}))

    found = []
    for i in range(len(vectors)):
        left_skill, left = vectors[i]
        for j in range(i + 1, len(vectors)):
            right_skill, right = vectors[j]
            smaller, larger = (left, right) if len(left) < len(right) else (right, left)
            score = sum(weight * larger.get(word, 0.0) for word, weight in smaller.items())
            if score >= COLLISION_THRESHOLD:
                found.append(
                    {
                        "score": round(score, 3),
                        "a": {"id": left_skill["id"], "plugin": left_skill["plugin"],
                              "name": left_skill["name"], "description": left_skill["description"]},
                        "b": {"id": right_skill["id"], "plugin": right_skill["plugin"],
                              "name": right_skill["name"], "description": right_skill["description"]},
                    }
                )
    found.sort(key=lambda c: -c["score"])
    return found


# -------------------------------------------------------------------------- graph


# IBM Plex Mono advances 0.6em, so a box can be sized from its longest line rather
# than guessed at. Guessing is what made the labels overflow.
GRAPH_TITLE_PX = 13.0
GRAPH_LINE_PX = 11.0
GRAPH_SUB_PX = 9.5
MONO_ADVANCE = 0.6
GRAPH_PAD = 14
GRAPH_GUTTER = 118
GRAPH_ROW_GAP = 26
GRAPH_MAX_ROWS = 7


def _text_w(text: str, size: float) -> float:
    return len(text) * size * MONO_ADVANCE


def build_graph(plugins: list[dict], artifacts: list[dict]) -> dict:
    """Plugin boxes carrying the components they install, laid out in columns by
    dependency depth. Every box is sized from its own longest line and every edge label
    sits in a gutter, so nothing can overlap anything."""
    by_name = {p["name"]: p for p in plugins}
    depth: dict[str, int] = {}

    def resolve(name: str, seen: frozenset) -> int:
        if name in depth:
            return depth[name]
        if name in seen or name not in by_name:
            return 0  # a cycle, or a dependency outside this marketplace
        deps = [d["name"] for d in by_name[name]["dependencies"]]
        value = 1 + max((resolve(d, seen | {name}) for d in deps), default=-1)
        depth[name] = value
        return value

    for plugin in plugins:
        resolve(plugin["name"], frozenset())

    # What each plugin actually installs, which is the question the page is asked.
    owned: dict[str, list[dict]] = {}
    for artifact in artifacts:
        if artifact["plugin"]:
            owned.setdefault(artifact["plugin"], []).append(artifact)

    order = {"skill": 0, "agent": 1, "command": 2, "hook": 3, "mcp": 4, "lsp": 5}
    parts: dict[str, dict] = {}
    for plugin in plugins:
        items = sorted(owned.get(plugin["name"], []),
                       key=lambda a: (order.get(a["type"], 9), a["name"]))
        shown = [{"type": a["type"], "name": a["name"]} for a in items[:GRAPH_MAX_ROWS]]
        parts[plugin["name"]] = {"rows": shown, "more": max(0, len(items) - len(shown))}

    type_col = max(
        (_text_w(row["type"], GRAPH_LINE_PX) for p in parts.values() for row in p["rows"]),
        default=0.0,
    ) + 10

    layers: dict[int, list[str]] = {}
    for plugin in plugins:
        layers.setdefault(depth.get(plugin["name"], 0), []).append(plugin["name"])

    def node_size(name: str) -> tuple[float, float]:
        plugin = by_name[name]
        body = parts[name]
        sub = f"v{plugin['version']}" if plugin["version"] else "unversioned"
        widest = max(
            _text_w(name, GRAPH_TITLE_PX),
            _text_w(sub, GRAPH_SUB_PX),
            max((type_col + _text_w(row["name"], GRAPH_LINE_PX) for row in body["rows"]), default=0.0),
        )
        rows = len(body["rows"]) + (1 if body["more"] else 0)
        return widest + GRAPH_PAD * 2, 44 + rows * 17 + (GRAPH_PAD if rows else 4)

    sizes = {name: node_size(name) for name in by_name}

    # Columns are as wide as their widest box, so a long plugin name never runs into
    # the gutter its edges are labelled in.
    column_w = {
        level: max(sizes[name][0] for name in names) for level, names in layers.items()
    }
    column_x: dict[int, float] = {}
    cursor = 16.0
    for level in sorted(layers):
        column_x[level] = cursor
        cursor += column_w[level] + GRAPH_GUTTER

    nodes = []
    for level in sorted(layers):
        y = 16.0
        for name in sorted(layers[level]):
            w, h = sizes[name]
            plugin = by_name[name]
            nodes.append(
                {
                    "id": name, "label": name, "depth": level,
                    "x": round(column_x[level], 1), "y": round(y, 1),
                    "width": round(w, 1), "height": round(h, 1),
                    "version": plugin["version"],
                    "artifacts": len(plugin["artifacts"]),
                    "typeColumn": round(type_col, 1),
                    "rows": parts[name]["rows"],
                    "more": parts[name]["more"],
                }
            )
            y += h + GRAPH_ROW_GAP

    edges = []
    for plugin in plugins:
        for dep in plugin["dependencies"]:
            edges.append(
                {
                    "from": plugin["name"], "to": dep["name"], "range": dep["range"],
                    "constrained": dep["constrained"], "resolvable": dep["resolvable"],
                    "external": dep["name"] not in by_name,
                }
            )

    width = round(cursor - GRAPH_GUTTER + 16, 1) if layers else 0
    height = round(
        16 + max(
            (sum(sizes[n][1] for n in names) + GRAPH_ROW_GAP * (len(names) - 1)
             for names in layers.values()),
            default=0,
        ) + 16,
        1,
    )
    return {"nodes": nodes, "edges": edges, "width": width, "height": height}


# --------------------------------------------------------------------------- build


def build(root: Path, report: Report) -> dict:
    catalogue_path = root / ".claude-plugin" / "marketplace.json"
    catalogue = load_json(catalogue_path, root, report) or {}
    entries = {e.get("name"): e for e in catalogue.get("plugins", []) if e.get("name")}

    slug = repo_slug(root, catalogue)
    dates = commit_dates(root)
    tags = plugin_tags(root)

    def blob(path: str, line: int | None = None) -> str | None:
        if not slug:
            return None
        anchor = f"#L{line}" if line else ""
        return f"https://github.com/{slug}/blob/{BLOB_REF}/{path}{anchor}"

    artifacts: list[dict] = []
    plugins: list[dict] = []

    plugins_dir = root / "plugins"
    directories = sorted(p for p in plugins_dir.iterdir() if p.is_dir()) if plugins_dir.is_dir() else []

    for directory in directories:
        name = directory.name
        manifest_path = directory / ".claude-plugin" / "plugin.json"
        manifest = load_json(manifest_path, root, report, name) if manifest_path.is_file() else None
        if manifest is None:
            manifest = {}

        components: list[dict] = []
        for kind, field, subdir, pattern in (
            ("skill", "skills", "skills", "*/SKILL.md"),
            ("agent", "agents", "agents", "*.md"),
            ("command", "commands", "commands", "*.md"),
            ("workflow", "workflows", "workflows", "*"),
            ("output-style", "outputStyles", "output-styles", "*.md"),
        ):
            for path in component_paths(directory, manifest, field, subdir, pattern):
                component = read_component(path, name, kind, root, subdir)
                if kind not in TOKENED_TYPES:
                    component["tokens"] = None
                components.append(component)

        skills = [c for c in components if c["type"] == "skill"]
        caps = capabilities(directory, root, report, name, skills)
        components += derived_artifacts(name, caps, directory, root)

        for component in components:
            component["updatedAt"] = dates.get(component["path"])
            component["githubUrl"] = blob(component["path"])
            component["category"] = (entries.get(name) or {}).get("category")
        artifacts += components

        description = str(manifest.get("description") or "").strip()
        entry = entries.get(name, {})
        where = rel(manifest_path, root)

        if len(description) < 40:
            report.error(
                where, "E101",
                "description is missing or under 40 characters. It is the whole of what a "
                "reader sees in the listing when deciding whether to install.", name,
            )
        entry_description = str(entry.get("description") or "").strip()
        if entry_description and description and entry_description != description:
            report.error(
                ".claude-plugin/marketplace.json", "E102",
                f"entry '{name}' description disagrees with plugin.json. The listing and the "
                "installed plugin would describe themselves differently.", name,
            )
        if not components:
            report.error(
                rel(directory, root), "E103",
                "registered but exposes zero components. Check that skills/ and agents/ sit at "
                "the plugin root and not inside .claude-plugin/.", name,
            )
        keywords = as_list(manifest.get("keywords"))
        if len(keywords) < 2:
            report.warn(where, "W101", "fewer than two keywords — the plugin is hard to find by browsing.", name)
        if not (directory / "README.md").is_file():
            report.warn(rel(directory, root), "W102", "no README.md.", name)
        if not (directory / "evals").is_dir():
            report.warn(rel(directory, root), "W103", "no evals/ — nothing scores this plugin's skills.", name)

        for skill in skills:
            text = skill["description"].lower()
            if not text:
                report.warn(skill["path"], "W104", f"skill '{skill['name']}' has no description.", name)
            elif not any(hint in text for hint in TRIGGER_HINTS) and "when" not in text:
                report.warn(
                    skill["path"], "W104",
                    f"skill '{skill['name']}' description reads as a summary, not a trigger "
                    "condition. It is the only thing Claude sees when deciding to load it.", name,
                )

        version = str(manifest.get("version") or "").strip()
        parsed = parse_version(version) if version else None
        tagged = {".".join(str(p) for p in v[:3]) + (f"-{v[3]}" if v[3] else "") for v, _, _ in tags.get(name, [])}
        if version and version not in tagged:
            report.warn(
                where, "W105",
                f"version {version} has no {name}--v{version} tag. Dependency constraints "
                "resolve against tags, so an untagged release cannot be depended on.", name,
            )

        dependencies = []
        for raw in manifest.get("dependencies") or []:
            dep_name = raw if isinstance(raw, str) else str(raw.get("name") or "")
            dep_range = None if isinstance(raw, str) else raw.get("version")
            constrained = bool(dep_range)
            resolvable = True
            if constrained:
                spec = parse_range(dep_range)
                resolvable = bool(spec) and any(
                    satisfies(v, spec) for v, _, _ in tags.get(dep_name, [])
                )
            else:
                report.warn(
                    where, "W106",
                    f"dependency '{dep_name}' is unconstrained, so it tracks latest and an "
                    "upstream release can change behaviour under you.", name,
                )
            dependencies.append(
                {
                    "name": dep_name, "range": dep_range, "constrained": constrained,
                    "resolvable": resolvable,
                    "marketplace": None if isinstance(raw, str) else raw.get("marketplace"),
                }
            )
            if constrained and not resolvable:
                report.warn(
                    where, "W109",
                    f"no {dep_name}--v* tag satisfies '{dep_range}' — this install fails with "
                    "no-matching-tag.", name,
                )

        readme = directory / "README.md"
        plugins.append(
            {
                "name": name,
                "description": description or entry_description,
                "version": version or None,
                "author": manifest.get("author"),
                "license": manifest.get("license"),
                "homepage": manifest.get("homepage"),
                "category": entry.get("category"),
                "keywords": sorted(set(keywords) | set(as_list(entry.get("keywords")))),
                "registered": name in entries,
                "dependencies": dependencies,
                "dependents": [],
                "artifacts": [c["id"] for c in components],
                "counts": _counts(components),
                "tokens": {"always": sum((c["tokens"] or {}).get("always", 0) for c in components)},
                "capabilities": caps,
                "hasEvals": (directory / "evals").is_dir(),
                "readme": readme.read_text() if readme.is_file() else None,
                "releases": releases(root, name, tags),
                "updatedAt": dates.get(rel(manifest_path, root)),
                "githubUrl": f"https://github.com/{slug}/tree/{BLOB_REF}/plugins/{name}" if slug else None,
                "url": f"/p/{name}/",
                "semver": parsed and list(parsed[:3]),
            }
        )

    for plugin in plugins:
        for dep in plugin["dependencies"]:
            target = next((p for p in plugins if p["name"] == dep["name"]), None)
            if target:
                target["dependents"].append(plugin["name"])

    docs = doc_artifacts(root)
    for doc in docs:
        doc["updatedAt"] = dates.get(doc["path"])
        doc["githubUrl"] = blob(doc["path"], doc.get("line"))
        doc["category"] = "documentation"
    artifacts += docs

    all_skills = [a for a in artifacts if a["type"] == "skill"]
    overlaps = collisions(all_skills)
    for overlap in overlaps:
        for side, other in (("a", "b"), ("b", "a")):
            report.warn(
                f"plugins/{overlap[side]['plugin']}", "W107",
                f"skill '{overlap[side]['name']}' overlaps '{overlap[other]['name']}' at "
                f"{overlap['score']:.2f}. Both fire unreliably while their triggers compete.",
                overlap[side]["plugin"],
            )

    for plugin in plugins:
        plugin["health"] = report.health(plugin["name"])

    newest = max((a["updatedAt"] for a in artifacts if a.get("updatedAt")), default=None)
    marketplace = {
        "name": catalogue.get("name"),
        "description": catalogue.get("description"),
        "owner": catalogue.get("owner"),
        "repo": slug,
        "ref": BLOB_REF,
        "install": {
            "add": f"/plugin marketplace add {slug}" if slug else None,
            "install": f"/plugin install {{plugin}}@{catalogue.get('name')}",
            "dev": "claude --plugin-dir ./plugins/{plugin}",
        },
    }

    return {
        "marketplace": marketplace,
        "generatedAt": newest,
        "plugins": plugins,
        "artifacts": artifacts,
        "collisions": overlaps,
        "graph": build_graph(plugins, artifacts),
        "stats": _stats(plugins, artifacts, overlaps, newest),
    }


def _counts(components: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for component in components:
        counts[component["type"]] = counts.get(component["type"], 0) + 1
    return dict(sorted(counts.items()))


def _stats(plugins: list[dict], artifacts: list[dict], overlaps: list[dict], newest) -> dict:
    categories: dict[str, int] = {}
    keywords: dict[str, int] = {}
    for plugin in plugins:
        if plugin["category"]:
            categories[plugin["category"]] = categories.get(plugin["category"], 0) + 1
        for keyword in plugin["keywords"]:
            keywords[keyword] = keywords.get(keyword, 0) + 1
    return {
        "plugins": len(plugins),
        "artifacts": len(artifacts),
        "byType": _counts(artifacts),
        "categories": dict(sorted(categories.items())),
        "keywords": dict(sorted(keywords.items(), key=lambda kv: (-kv[1], kv[0]))),
        "alwaysTokens": sum(p["tokens"]["always"] for p in plugins),
        "collisions": len(overlaps),
        "updatedAt": newest,
    }


def search_documents(artifacts: list[dict]) -> list[dict]:
    """What the browser indexes. Arrays stay arrays; the site joins them through
    MiniSearch's extractField rather than shipping two shapes of the same data."""
    return [
        {
            "id": a["id"], "type": a["type"], "plugin": a["plugin"], "name": a["name"],
            "title": a["title"], "description": a["description"], "keywords": a["keywords"],
            "headings": a["headings"], "body": a["body"], "url": a["url"],
            "invocation": a.get("invocation"), "tokens": a["tokens"],
            "category": a.get("category"),
        }
        for a in artifacts
    ]


# --------------------------------------------------------------------------- output


def dump(payload) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n").encode()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build the catalogue site's data.")
    parser.add_argument("root", nargs="?", default=".", help="marketplace root (default: .)")
    parser.add_argument("--check", action="store_true", help="validate only, write nothing")
    parser.add_argument("--site-dir", default="site", help="site directory (default: site)")
    args = parser.parse_args(argv[1:])

    root = Path(args.root).resolve()
    report = Report()

    if not (root / ".claude-plugin" / "marketplace.json").is_file():
        print(f"error: no .claude-plugin/marketplace.json under {root}", file=sys.stderr)
        return 1

    catalog = build(root, report)
    documents = search_documents(catalog["artifacts"])

    payloads = {
        Path(args.site_dir) / "src" / "data" / "catalog.json": dump(catalog),
        Path(args.site_dir) / "public" / "data" / "search-docs.json": dump(documents),
        Path(args.site_dir) / "public" / "data" / "graph.json": dump(catalog["graph"]),
        Path(args.site_dir) / "public" / "data" / "collisions.json": dump(catalog["collisions"]),
        Path(args.site_dir) / "public" / "data" / "stats.json": dump(catalog["stats"]),
    }

    search_path = Path(args.site_dir) / "public" / "data" / "search-docs.json"
    packed = len(gzip.compress(payloads[search_path]))
    if packed > INDEX_FAIL_BYTES:
        report.error(
            rel(root / search_path, root), "E104",
            f"search payload is {packed // 1024} KB gzipped, over the {INDEX_FAIL_BYTES // 1024} KB "
            "ceiling. Split the index into tiers before shipping this.",
        )
    elif packed > INDEX_SPLIT_BYTES:
        report.warn(
            rel(root / search_path, root), "W108",
            f"search payload is {packed // 1024} KB gzipped, over the {INDEX_SPLIT_BYTES // 1024} KB "
            "single-file budget. Time to split into an eager tier and a body tier.",
        )

    for entry in report.warnings:
        print(f"warning: {entry['where']}: [{entry['code']}] {entry['message']}")
    for entry in report.errors:
        print(f"error: {entry['where']}: [{entry['code']}] {entry['message']}", file=sys.stderr)

    if not args.check and not report.errors:
        for path, blob in payloads.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            print(f"wrote {rel(target, root)} ({len(blob) // 1024 or 1} KB)")

    plural = "" if catalog["stats"]["plugins"] == 1 else "s"
    print(
        f"\nIndexed {catalog['stats']['plugins']} plugin{plural}, "
        f"{catalog['stats']['artifacts']} artifact(s), search payload {packed // 1024 or 1} KB gzipped: "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
