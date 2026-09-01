#!/usr/bin/env bash
# Run the eval cases for some or all plugins, and report what actually ran.
#
# Used by the `Evals` workflow in .github/workflows/evals.yml, and safe to run by hand:
#
#     scripts/run-evals.sh                          # every plugin that has cases
#     scripts/run-evals.sh review-lenses            # one plugin
#     scripts/run-evals.sh --changed-since origin/main
#     scripts/run-evals.sh --case 'verifier-*' review-lenses
#
# Three things it gets right that a loop over `claude plugin eval` would not:
#
#   1. **Early access is a skip, not a failure.** `claude plugin eval` exits 1 with
#      "currently in early access" on an account without it. That is indistinguishable
#      from a failing suite by exit code alone, and a red check nobody can turn green
#      teaches people to ignore the check.
#   2. **A plugin with no cases is reported, never silently passed.** An empty run and a
#      run that found nothing to do produce the same exit code and mean opposite things.
#   3. **A bundled self-test counts.** hook-guardrails ships no model-graded cases —
#      its behaviour is two shell scripts — so its selftest.sh is what there is to run.
#
# Exit 0 when everything that could run passed, 1 when something failed, 2 when a cost
# ceiling aborted a run.
set -uo pipefail

cd "$(git rev-parse --show-toplevel)"

case_glob=""
max_cost=""
changed_since=""
judge_model=""
targets=()
named=()          # what the caller typed, as opposed to what a diff derived

while [ $# -gt 0 ]; do
  case "$1" in
    --case)           case_glob="${2:-}"; shift 2 ;;
    --max-cost-usd)   max_cost="${2:-}"; shift 2 ;;
    --changed-since)  changed_since="${2:-}"; shift 2 ;;
    --judge-model)    judge_model="${2:-}"; shift 2 ;;
    -h|--help)        sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*)               echo "unknown option: $1" >&2; exit 1 ;;
    *)                targets+=("$1"); named+=("$1"); shift ;;
  esac
done

# --- which plugins
if [ -n "$changed_since" ]; then
  if ! git rev-parse --verify --quiet "$changed_since" >/dev/null; then
    echo "run-evals: '$changed_since' is not a ref this clone knows; evaluating everything instead." >&2
  else
    while IFS= read -r name; do
      [ -n "$name" ] && targets+=("$name")
    done < <(git diff --name-only "$changed_since"...HEAD -- 'plugins/*' \
             | awk -F/ 'NF>1 {print $2}' | sort -u)
    if [ ${#targets[@]} -eq 0 ]; then
      echo "No plugin changed since $changed_since — nothing to evaluate."
      exit 0
    fi
  fi
fi

if [ ${#targets[@]} -eq 0 ]; then
  while IFS= read -r dir; do
    targets+=("$(basename "$dir")")
  done < <(find plugins -mindepth 1 -maxdepth 1 -type d | sort)
fi

# --- run
ran=0; passed=0; failed=0; skipped=0; gated=0
summary=()

note() { summary+=("$1"); printf '%s\n' "$1"; }

for name in "${targets[@]}"; do
  dir="plugins/$name"
  if [ ! -d "$dir" ]; then
    # A name the caller typed is a typo and must fail: reporting "passed" for a plugin
    # nobody evaluated is the failure this whole marketplace keeps writing rules about.
    # A name a diff derived is a plugin that was deleted, which is a skip.
    if printf '%s\n' "${named[@]:-}" | grep -qxF "$name"; then
      note "FAIL     $name — no such plugin"
      failed=$((failed+1))
    else
      note "skip     $name — no longer present"
      skipped=$((skipped+1))
    fi
    continue
  fi

  # A bundled self-test is a real check and runs regardless of eval availability.
  selftested=0
  if [ -x "$dir/scripts/selftest.sh" ]; then
    selftested=1
    if bash "$dir/scripts/selftest.sh" >/tmp/selftest.$$.log 2>&1; then
      note "ok       $name — selftest.sh: $(tail -1 /tmp/selftest.$$.log)"
      passed=$((passed+1))
    else
      note "FAIL     $name — selftest.sh"
      sed 's/^/         /' /tmp/selftest.$$.log
      failed=$((failed+1))
    fi
    ran=$((ran+1))
    rm -f /tmp/selftest.$$.log
  fi

  cases=$(find "$dir/evals" -mindepth 1 -maxdepth 1 -type d \
          ! -name fixtures ! -name results ! -name mocks 2>/dev/null | wc -l | tr -d ' ')
  if [ "$cases" = "0" ]; then
    # Not a skip when a self-test already covered it — that plugin's behaviour is two
    # shell scripts, and its evals/README.md says why there is nothing to model-grade.
    if [ "$selftested" = "1" ]; then
      note "         $name — no model-graded cases by design; covered by selftest.sh"
    else
      note "none     $name — no eval cases (see $dir/evals/README.md)"
      skipped=$((skipped+1))
    fi
    continue
  fi

  args=(plugin eval "./$dir" --allow-tools Bash Write Edit)
  [ -n "$case_glob" ]   && args+=(--case "$case_glob")
  [ -n "$max_cost" ]    && args+=(--max-cost-usd "$max_cost")
  [ -n "$judge_model" ] && args+=(--judge-model "$judge_model")
  args+=(--json "$dir/evals/results/run.json")

  mkdir -p "$dir/evals/results"
  output=$(claude "${args[@]}" 2>&1); code=$?
  ran=$((ran+1))

  # Early access is a skip. Checked before the exit code, because the gate exits 1 and
  # a failing suite exits 1, and only the message tells them apart.
  if printf '%s' "$output" | grep -qi 'early access'; then
    note "gated    $name — plugin eval is in early access on this account; $cases cases not run"
    gated=$((gated+1)); ran=$((ran-1))
    continue
  fi

  case $code in
    0) note "ok       $name — $cases cases"; passed=$((passed+1)) ;;
    2) note "BUDGET   $name — cost ceiling hit, partial results"
       printf '%s\n' "$output" | tail -20 | sed 's/^/         /'
       failed=$((failed+1)) ;;
    *) note "FAIL     $name — $cases cases, exit $code"
       printf '%s\n' "$output" | tail -40 | sed 's/^/         /'
       failed=$((failed+1)) ;;
  esac
done

echo
echo "$ran run · $passed passed · $failed failed · $gated gated · $skipped skipped"

# The summary goes to the job page when there is one, so a reader does not have to open the log.
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "### Evals"
    echo
    echo '```'
    printf '%s\n' "${summary[@]}"
    echo '```'
    echo
    echo "$ran run · $passed passed · $failed failed · $gated gated · $skipped skipped"
    [ "$gated" -gt 0 ] && echo && echo "> \`claude plugin eval\` is in early access. Gated plugins were not evaluated; this is not a failure."
  } >> "$GITHUB_STEP_SUMMARY"
fi

[ "$failed" -gt 0 ] && exit 1
exit 0
