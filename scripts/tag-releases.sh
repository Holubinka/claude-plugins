#!/usr/bin/env bash
# Cut a {plugin}--v{version} tag for every plugin whose manifest version has none.
#
# Run by the `Release tags` job in .github/workflows/pages.yml, on a push to main only.
# Safe to run by hand from a clean tree on main; it creates nothing that already exists.
#
# Two things it gets right that a loop over `plugins/*/` would not:
#
#   1. **Dependency order.** A dependent must not be tagged before what it depends on.
#      Between the two pushes a fresh install of the dependent resolves its constraint
#      against a tag that does not exist yet and fails with no-matching-tag. The window is
#      seconds, and someone will land in it.
#   2. **Idempotence.** Every push to main runs this. Only versions without a tag are cut,
#      so a run that changes no manifest does nothing and says so.
#
# It delegates the tag itself to `claude plugin tag`, which validates the plugin, checks
# that plugin.json and the marketplace entry agree on the version, and refuses a dirty
# tree — the same gate a human gets, rather than a bare `git tag` that skips all of it.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ -n "${CI:-}" ]; then
  git config user.name  "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
fi

# Plugin directories in dependency order: everything a plugin depends on comes first.
order=$(python3 - <<'PY'
import json
import pathlib
import sys

manifests = {}
for path in sorted(pathlib.Path("plugins").glob("*/.claude-plugin/plugin.json")):
    manifest = json.loads(path.read_text())
    name = manifest.get("name")
    if not name:
        sys.exit(f"{path} declares no name")
    deps = [
        dep if isinstance(dep, str) else dep.get("name")
        for dep in (manifest.get("dependencies") or [])
    ]
    manifests[name] = (path.parent.parent.name, [d for d in deps if d])

ordered, done = [], set()


def visit(name: str, stack: tuple = ()) -> None:
    if name in done:
        return
    if name in stack:
        sys.exit("dependency cycle: " + " -> ".join(stack + (name,)))
    entry = manifests.get(name)
    if entry is None:
        return  # a dependency from another marketplace; not ours to tag
    for dep in entry[1]:
        visit(dep, stack + (name,))
    done.add(name)
    ordered.append(entry[0])


for plugin in manifests:
    visit(plugin)
print("\n".join(ordered))
PY
)

read_field() { python3 -c "import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]])" "$1" "$2"; }

cut=0
for directory in $order; do
  manifest="plugins/$directory/.claude-plugin/plugin.json"
  name=$(read_field "$manifest" name)
  version=$(read_field "$manifest" version)
  tag="$name--v$version"

  if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
    printf '  %-28s %s already tagged\n' "$name" "$version"
    continue
  fi

  printf '::notice::cutting %s\n' "$tag"
  claude plugin tag "./plugins/$directory" --push
  cut=$((cut + 1))
done

if [ "$cut" -eq 0 ]; then
  echo "No manifest version is missing a tag."
else
  echo "Cut $cut tag(s)."
fi
