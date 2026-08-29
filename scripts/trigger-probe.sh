#!/usr/bin/env bash
# Which skill actually loads for a real request?
#
# `build-index.py --check` measures lexical distance between skill descriptions, which is
# necessary for correct routing and not sufficient for it. This measures the thing itself:
# it sends a request to a session with the plugins loaded and records which skill fired.
#
#     scripts/trigger-probe.sh                       # every probe in the set
#     scripts/trigger-probe.sh review-diff           # probes for one skill
#
# Probes live in scripts/trigger-probes.tsv, one per line:
#     <expectation>  <the request>
#
# Three forms of expectation:
#     plugin:skill    a POSITIVE — that skill must load
#     -               a NEGATIVE — nothing at all may load
#     !plugin:skill   a DISPLACEMENT — that skill must NOT load; anything else, or nothing,
#                     is fine. For a request another skill legitimately owns.
#
# The negatives are the half that matters — recall is easy to buy by widening a description, and
# the price is paid on every turn by every other skill. The third form exists because "-" was
# too blunt twice: a request that a sibling skill correctly owns is not a request that must go
# unanswered, and labelling it "-" scores a correct routing decision as a failure.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

filter="${1:-}"
probes="scripts/trigger-probes.tsv"
[ -f "$probes" ] || { echo "no probe set at $probes" >&2; exit 1; }

dirs=()
for d in plugins/*/; do dirs+=(--plugin-dir "./${d%/}"); done

hit=0; miss=0; false_fire=0; clean=0
printf '%-34s %-40s %s\n' EXPECTED REQUEST RESULT
printf '%-34s %-40s %s\n' "--------" "-------" "------"

while IFS=$'\t' read -r expected request; do
  case "$expected" in ''|'#'*) continue ;; esac
  [ -n "$filter" ] && [ "$expected" != "$filter" ] && continue

  # Ask for the routing decision only, and stop before any work is done.
  answer=$(claude "${dirs[@]}" --permission-mode plan --output-format text \
    -p "$request

Before doing anything else, answer with ONE line and nothing else: the namespaced name of the skill you would load for this request (for example engineering-paved-path:security), or the word NONE if no skill applies. Do not load it, do not act, do not explain." \
    < /dev/null 2>/dev/null | tr -d '\r' | grep -oE '[a-z0-9-]+:[a-z0-9-]+|NONE' | head -1)
  answer="${answer:-NONE}"

  if [ "$expected" = "-" ]; then
    if [ "$answer" = "NONE" ]; then result="ok        stayed quiet"; clean=$((clean+1))
    else result="FALSE FIRE loaded $answer"; false_fire=$((false_fire+1)); fi
  elif [ "${expected#!}" != "$expected" ]; then
    forbidden="${expected#!}"
    if [ "$answer" = "$forbidden" ]; then result="FALSE FIRE loaded $forbidden"; false_fire=$((false_fire+1))
    else result="ok        $answer"; clean=$((clean+1)); fi
  else
    if [ "$answer" = "$expected" ]; then result="ok        $answer"; hit=$((hit+1))
    else result="MISS      got $answer"; miss=$((miss+1)); fi
  fi
  printf '%-34s %-40s %s\n' "$expected" "$(printf '%.40s' "$request")" "$result"
done < "$probes"

pos=$((hit + miss)); neg=$((clean + false_fire))
echo
[ "$pos" -gt 0 ] && printf 'recall    %d/%d positives loaded the right skill\n' "$hit" "$pos"
[ "$neg" -gt 0 ] && printf 'precision %d/%d negatives stayed quiet   <- the number to defend\n' "$clean" "$neg"
[ "$((miss + false_fire))" -gt 0 ] && exit 1
exit 0
