#!/usr/bin/env bash
# Exercises both hooks against the cases they exist for, in a throwaway repository.
#
# Run it before trusting them, and again after changing either script:
#
#     bash scripts/selftest.sh
#
# It creates and removes its own temporary directory and touches nothing else. Exit
# status is 1 if any case behaved differently from what is asserted here.
set -uo pipefail

here=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
push_hook="$here/block-protected-push.sh"
lint_hook="$here/scoped-lint-fix.sh"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

pass=0
fail=0

check() { # name, expected-exit, actual-exit
  if [ "$2" = "$3" ]; then
    pass=$((pass + 1))
    printf '  ok    %s\n' "$1"
  else
    fail=$((fail + 1))
    printf '  FAIL  %s — expected exit %s, got %s\n' "$1" "$2" "$3"
  fi
}

push() { # command, expected exit
  printf '{"tool_name":"Bash","tool_input":{"command":%s}}' "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/')" \
    | bash "$push_hook" >/dev/null 2>&1
  check "push: $1" "$2" "$?"
}

echo "block-protected-push.sh"
push 'git push origin main' 2
push 'git push origin HEAD:develop' 2
push 'git push --force-with-lease origin master' 2
push 'git push origin release/2.1' 2
push 'npm test && git push origin develop' 2
push 'git push -u origin feature/thing' 0
push 'echo "git push origin main"' 0
push 'git status' 0

# The case a hook exists for: a bare push whose upstream silently resolves to a
# protected branch. Nothing in the command text says "main".
git init -q --bare "$tmp/remote"
git init -q "$tmp/repo"
(
  cd "$tmp/repo" || exit 1
  git config user.email selftest@example.invalid
  git config user.name selftest
  git checkout -q -b main
  echo x > file.txt && git add -A && git commit -qm init
  git remote add origin "$tmp/remote" && git push -q -u origin main
  git checkout -q -b feature origin/main          # sets upstream to main
  echo '{"tool_name":"Bash","tool_input":{"command":"git push"}}' | bash "$push_hook" >/dev/null 2>&1
  exit $?
)
check "push: bare push whose upstream is origin/main" 2 "$?"

(
  cd "$tmp/repo" || exit 1
  git branch --unset-upstream >/dev/null 2>&1
  echo '{"tool_name":"Bash","tool_input":{"command":"git push"}}' | bash "$push_hook" >/dev/null 2>&1
  exit $?
)
check "push: bare push with no upstream on an unprotected branch" 0 "$?"

HOOK_ALLOW_PROTECTED_PUSH=1 bash -c "echo '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push origin main\"}}' | bash '$push_hook'" >/dev/null 2>&1
check "push: HOOK_ALLOW_PROTECTED_PUSH=1 lets it through" 0 "$?"

echo
echo "scoped-lint-fix.sh"
mkdir -p "$tmp/lint/src" "$tmp/lint/node_modules/pkg" "$tmp/lint/node_modules/.bin"
printf 'const x   =    1\n' > "$tmp/lint/src/a.ts"
printf '// @generated\nconst y   =   2\n' > "$tmp/lint/src/gen.ts"
printf 'const z   =   3\n' > "$tmp/lint/node_modules/pkg/index.js"
echo '{}' > "$tmp/lint/.prettierrc"
echo '{}' > "$tmp/lint/package-lock.json"

# A stand-in formatter, so the happy path is exercised rather than assumed.
cat > "$tmp/lint/node_modules/.bin/prettier" <<'STUB'
#!/usr/bin/env bash
for a in "$@"; do case "$a" in --*) ;; *) f="$a";; esac; done
[ -f "$f" ] && perl -pi -e 's/ {2,}/ /g' "$f"
STUB
chmod +x "$tmp/lint/node_modules/.bin/prettier"

lint() { echo "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$1\"}}" | bash "$lint_hook" >/dev/null 2>&1; }

lint "$tmp/lint/src/a.ts";                    check "lint: exits 0 on an edited file" 0 "$?"
lint "$tmp/lint/src/gen.ts";                  check "lint: exits 0 on a generated file" 0 "$?"
lint "$tmp/lint/node_modules/pkg/index.js";   check "lint: exits 0 on a vendored file" 0 "$?"
lint "$tmp/lint/nope.ts";                     check "lint: exits 0 on a missing file" 0 "$?"

[ "$(cat "$tmp/lint/src/a.ts")" = "const x = 1" ]
check "lint: formatted the file it was given" 0 "$?"
grep -q 'const y   =   2' "$tmp/lint/src/gen.ts"
check "lint: left the generated file alone" 0 "$?"
grep -q 'const z   =   3' "$tmp/lint/node_modules/pkg/index.js"
check "lint: left the vendored file alone" 0 "$?"

# The same happy path again, with timeout(1) on PATH. Whether that binary exists changes
# how the hook invokes the formatter, and a stock macOS has no coreutils — so every case
# above ran the branch CI does not, and the branch CI does ran no formatter at all. A
# stub keeps both reachable from either machine.
mkdir -p "$tmp/bin"
cat > "$tmp/bin/timeout" <<'STUB'
#!/usr/bin/env bash
shift                                           # the duration
exec "$@"
STUB
chmod +x "$tmp/bin/timeout"

printf 'const w   =    4\n' > "$tmp/lint/src/b.ts"
echo "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$tmp/lint/src/b.ts\"}}" \
  | PATH="$tmp/bin:$PATH" bash "$lint_hook" >/dev/null 2>&1
check "lint: exits 0 with timeout(1) present" 0 "$?"
[ "$(cat "$tmp/lint/src/b.ts")" = "const w = 4" ]
check "lint: formatted the file with timeout(1) present" 0 "$?"

echo
printf '%s passed, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
