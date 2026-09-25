#!/usr/bin/env bash
# Exercises collect_usage.py against a synthetic transcript tree, one case per place a component
# can load from, and one per record that must not be counted.
#
#     bash scripts/selftest.sh
#
# Everything runs under a throwaway HOME in a temporary directory, which is removed on exit. No
# real transcript is read. Exit status is 1 if any count differs from what is asserted here.
set -uo pipefail

here=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

home="$tmp/home"
project="$home/.claude/projects/-proj"
repo="$tmp/repo"
mkdir -p "$project/s1/subagents" "$repo/.claude/skills/beta"
for skill in alpha beta; do
  mkdir -p "$home/.claude/plugins/cache/pp/skills/$skill"
  touch "$home/.claude/plugins/cache/pp/skills/$skill/SKILL.md"
done
# A project skill named `beta` shadows the plugin's, so a bare `beta` must stay unattributed.
touch "$repo/.claude/skills/beta/SKILL.md"
printf '{"plugins":{"pp@m":[{"installPath":"%s"}]}}\n' "$home/.claude/plugins/cache/pp" \
  > "$home/.claude/plugins/installed_plugins.json"

cat > "$project/s1.jsonl" <<EOF
{"type":"user","cwd":"$repo","message":{"role":"user","content":"<command-message>pp:alpha</command-message>\n<command-name>/pp:alpha</command-name>"}}
{"type":"user","message":{"role":"user","content":"<command-name>/clear</command-name>"}}
{"type":"assistant","cwd":"$repo","message":{"usage":{"output_tokens":10,"cache_read_input_tokens":100},"content":[{"type":"tool_use","name":"Skill","input":{"skill":"alpha"}},{"type":"tool_use","name":"Skill","input":{"skill":"beta"}},{"type":"tool_use","name":"Agent","input":{"subagent_type":"pp:worker"}},{"type":"tool_use","name":"Agent","input":{"subagent_type":"Explore"}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"<command-name>/pp:alpha</command-name>"}]}}
EOF
cat > "$project/s1/subagents/agent-x.jsonl" <<EOF
{"type":"user","isMeta":true,"message":{"role":"user","content":[{"type":"text","text":"<command-message>pp:alpha</command-message>\n<command-name>pp:alpha</command-name>"}]}}
{"type":"assistant","cwd":"$repo","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"pp:beta"}}]}}
EOF

HOME="$home" python3 "$here/collect_usage.py" "$tmp/out" 1 30 x > /dev/null
HOME="$home" python3 - "$tmp/out" <<'EOF'
import json, pathlib, sys

session = json.loads(next(pathlib.Path(sys.argv[1]).glob("usage-*.json")).read_text())["sessions"][0]
fired, via = session["fired"], session["via"]
cases = [
    ("typed /pp:alpha counts as slash", via.get("pp:alpha", {}).get("slash"), 1),
    ("bare alpha resolves to its only plugin", via.get("pp:alpha", {}).get("model"), 1),
    ("a skill preloaded into a subagent counts", via.get("pp:alpha", {}).get("subagent"), 1),
    ("a Skill call inside a subagent counts", via.get("pp:beta", {}).get("subagent"), 1),
    ("a shadowed bare name is not credited to the plugin", via.get("pp:beta", {}).get("model"), 0),
    ("the shadowed bare name is counted as unattributed", session["unqualified_skill_calls"], 1),
    ("a namespaced agent counts", fired.get("pp:worker"), 1),
    ("a built-in command and a built-in agent are ignored", sorted(fired), ["pp:alpha", "pp:beta", "pp:worker"]),
    ("tag text inside a tool result is not a slash command", fired.get("pp:alpha"), 3),
]
failed = 0
for name, got, want in cases:
    ok = got == want
    failed += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f" — expected {want!r}, got {got!r}"))
sys.exit(1 if failed else 0)
EOF
status=$?

# A collection written by 1.0.0 has no `via`; the report must still read it.
mkdir -p "$tmp/old"
printf '{"window_days":30,"scope":"x","sessions":[{"fired":{"pp:alpha":2},"tokens":{"output":1,"cache_read":1}}]}\n' \
  > "$tmp/old/usage-00000000-000000.json"
if python3 "$here/collect_usage.py" --report "$tmp/old" | grep -Eq '^pp:alpha +2 +1 +100% +2 +0 +0$'; then
  echo "  ok    a 1.0.0 collection reports with every count under model"
else
  echo "  FAIL  a 1.0.0 collection reports with every count under model"
  status=1
fi

exit "$status"
