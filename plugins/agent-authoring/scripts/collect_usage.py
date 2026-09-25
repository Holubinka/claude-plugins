#!/usr/bin/env python3
"""What actually fired, read from the transcripts Claude Code already writes locally.

    collect_usage.py <log-dir> <all-projects:0|1> <days> <project-slug>
    collect_usage.py --report <log-dir>

The passive half of the feedback log. `feedback.sh record` needs someone to stop and compose
an entry, which is the friction that stops most reports existing at all. This needs nothing:
the transcripts are already on disk, and a scan turns them into the one number a maintainer
can never have — **how often a component fired out of sessions actually run**.

Structural facts only: component names, invocation counts, turn counts, token totals,
timestamps, branch. Never prompt text, never output text, never file contents. Read-only, no
network, and the result stays in the log directory until someone exports it deliberately.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import time

STRUCTURAL_NOTE = (
    "Structural facts only: component names, counts, turn counts and token totals.\n"
    "No prompt text, no output text, no file contents. Nothing was sent anywhere."
)


SOURCES = ("model", "slash", "subagent")
COMMAND = re.compile(r"<command-name>(/?)([A-Za-z0-9_-]+:[A-Za-z0-9_-]+)</command-name>")


def read_records(path: pathlib.Path):
    try:
        handle = path.open(errors="replace")
    except OSError:
        return
    with handle:
        for line in handle:
            try:
                yield json.loads(line)
            except Exception:
                continue


def invoked(message: dict) -> tuple[list[str], list[str]]:
    """Namespaced components a Skill or Agent call names, and the skill names given bare."""
    names, bare = [], []
    for block in message.get("content") or []:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        args = block.get("input") or {}
        name = None
        if block.get("name") == "Skill":
            name = args.get("skill")
        elif block.get("name") == "Agent":
            name = args.get("subagent_type")
        # Namespaced only — a plugin component, never a built-in agent.
        if name and ":" in str(name):
            names.append(str(name))
        elif name and block.get("name") == "Skill":
            bare.append(str(name))
    return names, bare


def commands(record: dict, slash: bool) -> list[str]:
    """Skills a user record loaded without a tool call.

    With a leading slash, the person typed it. Without one, it is a skill preloaded into a
    subagent by the agent's `skills:` frontmatter.
    """
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        texts = [content]
    elif isinstance(content, list):
        texts = [b.get("text") or "" for b in content if isinstance(b, dict) and b.get("type") == "text"]
    else:
        return []
    return [name for text in texts for lead, name in COMMAND.findall(text) if bool(lead) == slash]


def plugin_skills() -> dict[str, list[str]]:
    """Skill name -> the installed plugins that ship a skill by that name."""
    index: dict[str, list[str]] = {}
    registry = pathlib.Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    try:
        plugins = json.loads(registry.read_text()).get("plugins") or {}
    except (OSError, ValueError):
        return index
    for key, installs in plugins.items():
        plugin = key.split("@")[0]
        for install in installs or []:
            for skill in pathlib.Path(install.get("installPath") or "").glob("skills/*/SKILL.md"):
                owners = index.setdefault(skill.parent.name, [])
                if plugin not in owners:
                    owners.append(plugin)
    return index


def resolve(name: str, cwd: str | None, index: dict[str, list[str]]) -> str | None:
    """Attribute a bare skill name to a plugin only when nothing else could have answered it.

    A project or personal skill of the same name shadows the plugin one, and a name two plugins
    share is ambiguous. Either way it stays unattributed rather than guessed at.
    """
    local = [pathlib.Path.home() / ".claude" / "skills" / name]
    if cwd:
        local.append(pathlib.Path(cwd) / ".claude" / "skills" / name)
    if any((d / "SKILL.md").is_file() for d in local):
        return None
    owners = index.get(name) or []
    return f"{owners[0]}:{name}" if len(owners) == 1 else None


def tally(fired: dict, via: dict, name: str, source: str) -> None:
    fired[name] = fired.get(name, 0) + 1
    counts = via.setdefault(name, dict.fromkeys(SOURCES, 0))
    counts[source] += 1


def scan(out_dir: pathlib.Path, all_projects: bool, days: int, slug: str) -> int:
    root = pathlib.Path.home() / ".claude" / "projects"
    if not root.is_dir():
        print("no local transcripts at ~/.claude/projects", file=sys.stderr)
        return 0

    projects = sorted(p for p in root.iterdir() if p.is_dir()) if all_projects else [root / slug]
    cutoff = time.time() - days * 86400
    sessions, skipped = [], 0
    index = plugin_skills()

    for project in projects:
        if not project.is_dir():
            continue
        for f in sorted(project.glob("*.jsonl")):
            try:
                mtime = f.stat().st_mtime
            except OSError:
                continue
            if mtime < cutoff:
                skipped += 1
                continue
            fired, via, turns, branch = {}, {}, 0, None
            unqualified = 0
            tok = {"input": 0, "output": 0, "cache_read": 0}
            for record in read_records(f):
                branch = branch or record.get("gitBranch")
                if record.get("type") == "user":
                    # Typed by the person, never a tool call: `/<plugin>:<skill>`.
                    for name in commands(record, slash=True):
                        tally(fired, via, name, "slash")
                    continue
                if record.get("type") != "assistant":
                    continue
                turns += 1
                message = record.get("message") or {}
                usage = message.get("usage") or {}
                tok["input"] += usage.get("input_tokens") or 0
                tok["output"] += usage.get("output_tokens") or 0
                tok["cache_read"] += usage.get("cache_read_input_tokens") or 0
                names, bare = invoked(message)
                for name in names + bare:
                    full = name if ":" in name else resolve(name, record.get("cwd"), index)
                    if full:
                        tally(fired, via, full, "model")
                    else:
                        unqualified += 1
            # Subagents write their own transcripts beside the session's. A skill an agent
            # loads, or has preloaded by its frontmatter, never appears in the main file.
            for sub in sorted((project / f.stem / "subagents").glob("*.jsonl")):
                for record in read_records(sub):
                    if record.get("type") == "user":
                        for name in commands(record, slash=False):
                            tally(fired, via, name, "subagent")
                    elif record.get("type") == "assistant":
                        names, bare = invoked(record.get("message") or {})
                        for name in names + bare:
                            full = name if ":" in name else resolve(name, record.get("cwd"), index)
                            if full:
                                tally(fired, via, full, "subagent")
                            else:
                                unqualified += 1
            if turns:
                sessions.append({
                    "session": f.stem,
                    "project": project.name,
                    "branch": branch,
                    "date": time.strftime("%Y-%m-%d", time.localtime(mtime)),
                    "turns": turns,
                    "tokens": tok,
                    "fired": fired,
                    "via": via,
                    "unqualified_skill_calls": unqualified,
                })

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"usage-{time.strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps({
        "collected": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "window_days": days,
        "scope": "all-projects" if all_projects else slug,
        "sessions": sessions,
    }, indent=2) + "\n")

    total = sum(sum(s["fired"].values()) for s in sessions)
    print(f"{len(sessions)} session(s) in the last {days} day(s), "
          f"{total} plugin component invocation(s)")
    print(f"{skipped} transcript(s) outside the window")
    print(path)
    print()
    print(STRUCTURAL_NOTE)
    return 0


def report(out_dir: pathlib.Path) -> int:
    files = sorted(out_dir.glob("usage-*.json"))
    if not files:
        print("no collection yet — run: feedback.sh collect")
        return 0
    data = json.loads(files[-1].read_text())
    sessions = data["sessions"]
    fired, sessions_with, via = {}, {}, {}
    for s in sessions:
        for name, n in s["fired"].items():
            fired[name] = fired.get(name, 0) + n
            sessions_with[name] = sessions_with.get(name, 0) + 1
        # Collections written before the source split carry no `via`; count them as model.
        for name, counts in (s.get("via") or {n: {"model": c} for n, c in s["fired"].items()}).items():
            total = via.setdefault(name, dict.fromkeys(SOURCES, 0))
            for source, n in counts.items():
                total[source] += n
    unqualified = sum(s.get("unqualified_skill_calls", 0) for s in sessions)

    print(f"from {files[-1].name} · {len(sessions)} session(s) · "
          f"window {data['window_days']}d · scope {data['scope']}\n")

    if not fired:
        print("No plugin component fired in any session in the window.")
        print()
        print("That is a finding, not an empty result. Either nothing is installed, or the")
        print("descriptions are not matching the work being done — and the second one is")
        print("invisible from anywhere else.")
        return 0

    print(f"{'component':<46} {'fired':>6} {'sessions':>9} {'share':>7} "
          f"{'model':>6} {'slash':>6} {'subagent':>9}")
    for name, n in sorted(fired.items(), key=lambda kv: -kv[1]):
        share = sessions_with[name] / len(sessions)
        v = via[name]
        print(f"{name:<46} {n:>6} {sessions_with[name]:>9} {share:>6.0%} "
              f"{v['model']:>6} {v['slash']:>6} {v['subagent']:>9}")

    out = sum(s["tokens"]["output"] for s in sessions)
    cache = sum(s["tokens"]["cache_read"] for s in sessions)
    if out:
        print(f"\noutput {out:,} · cache-read {cache:,} · reread_ratio {cache / out:.0f}x")
    print()
    print("The share column is the denominator a maintainer can never have: how often a")
    print("component fired out of sessions you actually ran. A component sitting at 0% is")
    print("charging its description on every turn and returning nothing for it.")
    print()
    print("model = a Skill or Agent call in the main session · slash = typed by the person ·")
    print("subagent = called or preloaded inside a subagent. A subagent-only component is")
    print("reached through an agent that names it, not through its own description.")
    if unqualified:
        print()
        print(f"{unqualified} skill call(s) named a skill without its plugin prefix and are not in")
        print("the table. A bare name is credited to a plugin only when exactly one installed")
        print("plugin ships it and no project or personal skill shadows it; these did not")
        print("qualify. Check a zero against that before acting on it.")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[1] == "--report":
        return report(pathlib.Path(argv[2]))
    if len(argv) < 5:
        print(__doc__.strip())
        return 2
    return scan(pathlib.Path(argv[1]), argv[2] == "1", int(argv[3]), argv[4])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
