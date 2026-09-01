#!/usr/bin/env bash
# PreToolUse(Bash): refuse a `git push` that would land on a protected branch.
#
# Two cases, and the second is the one worth a hook:
#
#   1. An explicit destination — `git push origin main`, `git push origin HEAD:develop`.
#   2. A bare `git push` whose upstream silently resolves to a protected branch. Branching
#      with `git checkout -b feature origin/main` sets the upstream to main, so a later
#      plain `git push` lands there with nothing in the command text to grep for. That is
#      the incident this closes, and no amount of instruction prevents it — the command
#      the model wrote is correct, and the destination is a fact about the repository.
#
# Exit 2 is the only value Claude Code treats as a block; stderr is handed back as the
# reason. Any other non-zero exit is reported and the call proceeds, so every path here
# exits 0 or 2.
#
# It fails OPEN. A guardrail against a slip, not a control against an adversary: refusing
# every Bash call because `jq` is missing makes the plugin unusable, and a hook people
# disable protects nothing. `sdd-engineering`'s write-gate fails closed instead, because
# refusing a write it cannot verify is safe. The two differ on purpose.
set -uo pipefail

PROTECTED_DEFAULT="main master develop release"

warn() { printf 'hook-guardrails: %s\n' "$1" >&2; exit 0; }
deny() { printf '%s\n' "$1" >&2; exit 2; }

[ "${HOOK_ALLOW_PROTECTED_PUSH:-}" = "1" ] && {
  printf 'hook-guardrails: HOOK_ALLOW_PROTECTED_PUSH=1 — protected-branch check skipped.\n' >&2
  exit 0
}

payload=$(cat)
command -v jq >/dev/null 2>&1 || warn "jq is not installed, so the protected-branch check did not run."

cmd=$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null) || warn "could not read the command."
[ -n "$cmd" ] || exit 0

# `git push` only at the start of a command or after a separator — never inside a quoted
# string or an argument. The naive substring match refuses `echo "git push"`, and a hook
# that refuses harmless commands is one people turn off.
starts='(^|[;&|(]|`)[[:space:]]*'
[[ $cmd =~ ${starts}git([[:space:]]+-[^[:space:]]+)*[[:space:]]+push([[:space:]]|$) ]] || exit 0

protected="${HOOK_PROTECTED_BRANCHES:-$PROTECTED_DEFAULT}"

is_protected() { # branch -> 0 when protected
  local branch="$1" pattern
  [ -n "$branch" ] || return 1
  for pattern in $protected; do
    case "$pattern" in
      */*|*'*'*) case "$branch" in $pattern|$pattern/*) return 0 ;; esac ;;
      *)         [ "$branch" = "$pattern" ] && return 0
                 case "$branch" in "$pattern"/*) return 0 ;; esac ;;
    esac
  done
  return 1
}

refuse() { # branch, how it was resolved
  deny "Refused: this push lands on '$1' ($2), which hook-guardrails treats as protected.

Push to a branch and open a pull request instead:
    git switch -c <branch> && git push -u origin <branch>

Protected patterns: $protected  (override with HOOK_PROTECTED_BRANCHES)
To allow this one push: HOOK_ALLOW_PROTECTED_PUSH=1 <your command>"
}

# Case 1 — an explicit refspec. Take the last colon-separated segment of each argument
# that is not a flag and not the remote, which is where the destination branch lives.
read -r -a words <<< "$cmd"
seen_push=0
position=0
for word in "${words[@]}"; do
  [ "$word" = "push" ] && { seen_push=1; continue; }
  [ "$seen_push" = 1 ] || continue
  case "$word" in
    -*) continue ;;
  esac
  position=$((position + 1))
  [ "$position" = 1 ] && continue          # the remote
  dest="${word##*:}"                        # HEAD:main -> main; main -> main
  dest="${dest#refs/heads/}"
  is_protected "$dest" && refuse "$dest" "named in the command"
done

# Case 2 — a bare push. Resolve what it would actually do.
[ "$position" -gt 1 ] && exit 0
command -v git >/dev/null 2>&1 || warn "git is not on PATH, so the destination could not be resolved."
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
if [ -n "$upstream" ]; then
  is_protected "${upstream#*/}" && refuse "${upstream#*/}" "the current branch's upstream is $upstream"
  exit 0
fi

# No upstream. `push.default` decides, and `current`/`simple` mean the branch's own name.
current=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)
default=$(git config --get push.default 2>/dev/null || echo simple)
case "$default" in
  current|simple|upstream|tracking)
    is_protected "$current" && refuse "$current" "no upstream; push.default=$default uses the current branch name"
    ;;
  matching)
    is_protected "$current" && refuse "$current" "no upstream; push.default=matching"
    ;;
esac

# Anything else is unresolved, and an unresolved destination is not a reason to refuse.
# A hook that blocks on ambiguity is a hook people disable.
exit 0
