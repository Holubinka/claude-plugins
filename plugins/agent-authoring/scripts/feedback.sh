#!/usr/bin/env bash
# A local log of how a plugin behaved, and two ways to hand it on.
#
#     feedback.sh collect [--all-projects] [--days N]    scan local transcripts; nothing to compose
#     feedback.sh usage                                  which components actually fired, and how often
#     feedback.sh record <plugin> <verdict> <<'ENTRY'   append an entry from stdin
#     feedback.sh list [plugin]                          what is in the log
#     feedback.sh show <id>                              one entry
#     feedback.sh export-issue <id>                      a paste-ready GitHub issue body
#     feedback.sh export-case <id> <dir>                 an eval case, ready for a pull request
#
# verdict: worked | misfired | did-not-fire
#
# Nothing here touches the network. The log is yours, it stays on your machine, and it moves
# only when you run an export and paste the result somewhere yourself.
#
# WHERE IT LIVES, AND THE CATCH. Default is $CLAUDE_PLUGIN_DATA — a per-plugin directory that
# Claude Code **deletes when the plugin is uninstalled from its last scope**. Which means the
# log explaining why you uninstalled something disappears at the moment you uninstall it. Set
# PLUGIN_FEEDBACK_DIR to somewhere you own if you want it to outlive that, or export before you
# uninstall. Writing outside the project or the plugin data dir without you asking would breach
# this marketplace's own security policy, so the default stays where the policy allows.
set -uo pipefail

dir="${PLUGIN_FEEDBACK_DIR:-${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/agent-authoring}/feedback}"
mkdir -p "$dir" 2>/dev/null || { echo "cannot write to $dir" >&2; exit 1; }

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; }

case "${1:-}" in
  record)
    plugin="${2:-}"; verdict="${3:-}"
    [ -n "$plugin" ] && [ -n "$verdict" ] || { echo "usage: feedback.sh record <plugin> <verdict>" >&2; exit 1; }
    case "$verdict" in worked|misfired|did-not-fire) ;; *) echo "verdict must be worked | misfired | did-not-fire" >&2; exit 1 ;; esac
    id="$(date +%Y%m%d-%H%M%S)-$plugin-$verdict"
    file="$dir/$id.md"
    {
      echo "---"
      echo "id: $id"
      echo "plugin: $plugin"
      echo "verdict: $verdict"
      echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "claude_code: $(claude --version 2>/dev/null | head -1 || echo unknown)"
      echo "---"
      cat
    } > "$file"
    echo "$file"
    ;;

  collect)
    shift
    all=0; days=90
    while [ $# -gt 0 ]; do
      case "$1" in
        --all-projects) all=1; shift ;;
        --days) days="${2:-90}"; shift 2 ;;
        *) echo "unknown option: $1" >&2; exit 1 ;;
      esac
    done
    python3 "$(dirname "$0")/collect_usage.py" "$dir" "$all" "$days" "$(pwd | sed 's|/|-|g')"
    ;;

  usage)
    python3 "$(dirname "$0")/collect_usage.py" --report "$dir"
    ;;

  list)
    filter="${2:-}"
    printf '%-40s %-14s %s\n' ID VERDICT SUMMARY
    for f in "$dir"/*.md; do
      [ -e "$f" ] || { echo "(the log is empty)"; break; }
      id=$(grep -m1 '^id: ' "$f" | cut -d' ' -f2-)
      v=$(grep -m1 '^verdict: ' "$f" | cut -d' ' -f2-)
      p=$(grep -m1 '^plugin: ' "$f" | cut -d' ' -f2-)
      [ -n "$filter" ] && [ "$p" != "$filter" ] && continue
      s=$(awk '/^## What happened/{f=1;next} f&&NF{print;exit}' "$f")
      printf '%-40s %-14s %s\n' "$id" "$v" "$(printf '%.60s' "${s:-—}")"
    done
    ;;

  show)
    f="$dir/${2:-}.md"; [ -f "$f" ] || { echo "no entry ${2:-}" >&2; exit 1; }; cat "$f" ;;

  export-issue)
    f="$dir/${2:-}.md"; [ -f "$f" ] || { echo "no entry ${2:-}" >&2; exit 1; }
    v=$(grep -m1 '^verdict: ' "$f" | cut -d' ' -f2-)
    echo "# Paste into the '$([ "$v" = did-not-fire ] && echo "A component did NOT fire" || echo "A component did something wrong")' issue form."
    echo "# Read it once for anything you would rather not publish before you do."
    echo
    sed -n '/^---$/,/^---$/!p' "$f"
    echo
    echo "---"
    grep -E '^(plugin|claude_code|date):' "$f" | sed 's/^/Reported from a local feedback log · /'
    ;;

  export-case)
    f="$dir/${2:-}.md"; out="${3:-}"
    [ -f "$f" ] || { echo "no entry ${2:-}" >&2; exit 1; }
    [ -n "$out" ] || { echo "usage: feedback.sh export-case <id> <case-dir>" >&2; exit 1; }
    mkdir -p "$out/graders"
    sed -n '/^## What you asked/,/^## /p' "$f" | sed '1d;$d' | sed '/^$/d' > "$out/prompt.md"
    {
      echo "Sourced from a real run. Reported $(grep -m1 '^date: ' "$f" | cut -d' ' -f2-)."
      echo
      echo "The response passes only if **all** of the following hold."
      echo
      sed -n '/^## What it should have done/,/^## /p' "$f" | sed '1d;$d' | sed '/^$/d'
      echo
      echo "<!-- Numbered, bold-assertion criteria are required. Rewrite the lines above into that"
      echo "     shape before opening the pull request — see docs/evals.md §1.3 and §1.4. -->"
    } > "$out/graders/criteria.md"
    echo "wrote $out/prompt.md and $out/graders/criteria.md"
    echo "Rewrite the criteria into numbered bold assertions, then open a pull request."
    ;;

  ""|-h|--help) usage ;;
  *) echo "unknown command: $1" >&2; usage; exit 1 ;;
esac
