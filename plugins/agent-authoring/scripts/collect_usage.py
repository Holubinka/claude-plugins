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

import json
import pathlib
import sys
import time

STRUCTURAL_NOTE = (
    "Structural facts only: component names, counts, turn counts and token totals.\n"
    "No prompt text, no output text, no file contents. Nothing was sent anywhere."
)


def scan(out_dir: pathlib.Path, all_projects: bool, days: int, slug: str) -> int:
    root = pathlib.Path.home() / ".claude" / "projects"
    if not root.is_dir():
        print("no local transcripts at ~/.claude/projects", file=sys.stderr)
        return 0

    projects = sorted(p for p in root.iterdir() if p.is_dir()) if all_projects else [root / slug]
    cutoff = time.time() - days * 86400
    sessions, skipped = [], 0

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
            fired, turns, branch = {}, 0, None
            tok = {"input": 0, "output": 0, "cache_read": 0}
            try:
                handle = f.open(errors="replace")
            except OSError:
                continue
            with handle:
                for line in handle:
                    try:
                        record = json.loads(line)
                    except Exception:
                        continue
                    branch = branch or record.get("gitBranch")
                    if record.get("type") != "assistant":
                        continue
                    turns += 1
                    message = record.get("message") or {}
                    usage = message.get("usage") or {}
                    tok["input"] += usage.get("input_tokens") or 0
                    tok["output"] += usage.get("output_tokens") or 0
                    tok["cache_read"] += usage.get("cache_read_input_tokens") or 0
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
                            fired[str(name)] = fired.get(str(name), 0) + 1
            if turns:
                sessions.append({
                    "session": f.stem,
                    "project": project.name,
                    "branch": branch,
                    "date": time.strftime("%Y-%m-%d", time.localtime(mtime)),
                    "turns": turns,
                    "tokens": tok,
                    "fired": fired,
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
    fired, sessions_with = {}, {}
    for s in sessions:
        for name, n in s["fired"].items():
            fired[name] = fired.get(name, 0) + n
            sessions_with[name] = sessions_with.get(name, 0) + 1

    print(f"from {files[-1].name} · {len(sessions)} session(s) · "
          f"window {data['window_days']}d · scope {data['scope']}\n")

    if not fired:
        print("No plugin component fired in any session in the window.")
        print()
        print("That is a finding, not an empty result. Either nothing is installed, or the")
        print("descriptions are not matching the work being done — and the second one is")
        print("invisible from anywhere else.")
        return 0

    print(f"{'component':<46} {'fired':>6} {'sessions':>9} {'share':>7}")
    for name, n in sorted(fired.items(), key=lambda kv: -kv[1]):
        share = sessions_with[name] / len(sessions)
        print(f"{name:<46} {n:>6} {sessions_with[name]:>9} {share:>6.0%}")

    out = sum(s["tokens"]["output"] for s in sessions)
    cache = sum(s["tokens"]["cache_read"] for s in sessions)
    if out:
        print(f"\noutput {out:,} · cache-read {cache:,} · reread_ratio {cache / out:.0f}x")
    print()
    print("The share column is the denominator a maintainer can never have: how often a")
    print("component fired out of sessions you actually ran. A component sitting at 0% is")
    print("charging its description on every turn and returning nothing for it.")
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
