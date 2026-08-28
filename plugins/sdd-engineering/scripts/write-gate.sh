#!/usr/bin/env bash
# PreToolUse gate for the `spec-creator` agent. Wired from that agent's own
# frontmatter, so it is active only while that subagent runs — no other agent,
# and not the main session, ever reaches this script.
#
# What it enforces:
#   Write/Edit/NotebookEdit  exactly one file directly inside a specs directory,
#                            either at the repository root or one level down in a
#                            package. Anything else is refused.
#   Bash                     refuses commands that mutate. This is a second line,
#                            not the first: redirections are not parsed, so the
#                            wall is on Write/Edit.
#
# The specs directory name comes from `specsDir` in ${CLAUDE_PROJECT_DIR}/sdd.config.json
# and defaults to "specs". Nothing else is read from that file here.
#
# Exit 2 is the only value Claude Code treats as a block; stderr is handed back
# to the agent as the reason. Any other non-zero exit is reported to the user
# and the tool call proceeds, so every failure path here must exit 0 or 2.
set -uo pipefail

payload=$(cat)

deny() { printf '%s\n' "$1" >&2; exit 2; }

command -v jq >/dev/null 2>&1 || deny "spec-creator write-gate cannot run: jq is not installed. Install jq, or the gate cannot verify where you are writing."

tool=$(printf '%s' "$payload" | jq -r '.tool_name // empty')
repo="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# specsDir: from sdd.config.json when present and sane, else "specs". A value with
# a slash, a leading dot or a shell metacharacter is ignored rather than trusted —
# this string goes into a path pattern.
specs_dir="specs"
config="$repo/sdd.config.json"
if [ -f "$config" ]; then
  candidate=$(jq -r '.specsDir // empty' "$config" 2>/dev/null)
  if [[ $candidate =~ ^[A-Za-z0-9_-]+$ ]]; then
    specs_dir="$candidate"
  fi
fi

relative_to_repo() { # absolute-or-relative path -> repo-relative, or the input unchanged
  local p="$1"
  case "$p" in
    "$repo"/*) printf '%s' "${p#"$repo"/}" ;;
    /*)        printf '%s' "$p" ;;
    ./*)       printf '%s' "${p#./}" ;;
    *)         printf '%s' "$p" ;;
  esac
}

case "$tool" in
  Write|Edit|NotebookEdit)
    path=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
    [ -z "$path" ] && deny "spec-creator write-gate: the call carries no file_path, so the gate cannot tell where it writes. Refused."
    rel=$(relative_to_repo "$path")

    case "$rel" in
      /*|../*|*/../*)
        deny "spec-creator may not write outside the repository. Refused: $path" ;;
      *)
        # A case pattern's * spans slashes, so the allowed shape is matched by
        # regex instead: a markdown file directly inside <specsDir>/ at the root,
        # or inside <package>/<specsDir>/ one level down.
        if [[ $rel =~ ^${specs_dir}/[^/]+\.md$ ]] ||
           [[ $rel =~ ^[^/]+/${specs_dir}/[^/]+\.md$ ]]; then
          exit 0
        fi
        deny "spec-creator writes specifications and nothing else. Allowed: ${specs_dir}/<name>.md for work spanning packages, or <module>/${specs_dir}/<name>.md for work inside one. Refused: $rel

If the specification is right and some other file is wrong, that is a finding for your report, not an edit you make." ;;
    esac
    ;;

  Bash)
    # Bash is for reading. A mutator counts only where a command actually starts:
    # the beginning of the string, or just after ; & | ( or a newline. Matching the
    # bare substring refused `ls src/platform src/modules`, because "platform "
    # ends in "rm ". Redirections are still not parsed, so `cmd > file` gets
    # through. The wall is on Write/Edit; this is a second line, not the first.
    cmd=$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')
    starts='(^|[;&|(]|`)[[:space:]]*'

    if [[ $cmd =~ ${starts}(rm|rmdir|mv|mkdir|tee|truncate)([[:space:]]|$) ]] ||
       [[ $cmd =~ ${starts}sed[[:space:]]+-i ]] ||
       [[ $cmd =~ ${starts}git[[:space:]]+(add|commit|push|checkout|stash|mv|rm|restore)([[:space:]]|$) ]] ||
       [[ $cmd =~ ${starts}(npm|pnpm|yarn|bun)[[:space:]]+(run|install|add|exec|i)([[:space:]]|$) ]] ||
       [[ $cmd =~ ${starts}gh[[:space:]]+pr[[:space:]]+create([[:space:]]|$) ]]; then
      deny "spec-creator's Bash is for reading only — git log, git show, git diff, rg, ls, cat, find. This command writes or runs a script. Refused: $cmd"
    fi
    exit 0
    ;;

  *)
    exit 0 ;;
esac
