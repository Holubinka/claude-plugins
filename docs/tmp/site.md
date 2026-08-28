# The catalogue site

A static site on GitHub Pages that makes this marketplace searchable and inspectable.
Everything it shows is derived from the repository at build time — there is no second
source of truth and nothing to keep in sync by hand.

For what a plugin must look like see [plugin-structure.md](../plugin-structure.md); for
what a plugin is allowed to do see [security.md](../security.md); for tags and versions see
[releasing.md](../releasing.md).

## Goals

1. **Find the right artifact from a natural question.** "I need a skill that reviews
   migrations" must return the skill, not force the user to guess a keyword.
2. **Answer "should I install this?" on one screen.** What it triggers on, what it costs
   in context, what it does to the machine, what it depends on.
3. **Cost nothing to maintain.** A new plugin appears on the site because it was merged,
   not because someone edited the site.

## Non-goals

No accounts, no ratings, no download counters, no server-side search, no hosting of
plugin artifacts — the site links to GitHub and to `/plugin install`. No embeddings in
v1 (see [Later](#later)). The site never becomes a place where content lives that the
repository does not already contain.

## Constraints

GitHub Pages serves static files and nothing else. That produces four hard rules:

| Constraint | Rule |
| :--- | :--- |
| No backend | The search index is built in CI and queried in the browser |
| No server-side routing | Every artifact gets a **prerendered** HTML page, not an SPA route |
| No write path | Anything a user submits goes through GitHub (prefilled issue links) |
| GitHub API is rate-limited from the browser (60/h/IP) | The site never calls it at runtime |

The index is **never committed**. It is generated on every deploy, so it cannot drift
from `plugins/`.

---

## Architecture

Two stages, deliberately separated.

```
plugins/ docs/ .claude-plugin/ git tags
            │
            ▼
   scripts/build-index.py          ← Python, no third-party deps
            │
            ├─ site/src/data/catalog.json      (build-time input to Astro)
            └─ site/public/data/*.json         (runtime input to the browser)
            │
            ▼
        Astro build                ← prerenders one page per artifact
            │
            ▼
   actions/deploy-pages
```

**Why the split.** The parser is the interesting, repository-specific part; it belongs
next to `lint-structure.py`, in the same language, with the same error-code discipline,
and it must be runnable as a CI gate on pull requests that never deploy anything. The
Astro app is then a dumb consumer of one JSON file.

**Stack.** Astro + TypeScript for the site, one React (or Preact) island for search,
MiniSearch for the engine, plain CSS with custom properties for theming. No CSS
framework, no chart or graph library — the dependency surface of a security-conscious
marketplace is itself a signal.

---

## Data contract

`scripts/build-index.py` emits `catalog.json`. This schema is the contract between the
two stages; changing it is a breaking change for the site.

### Artifact record

Every skill, agent, command, hook set, MCP server and doc section is one artifact.

```jsonc
{
  "id": "skill:review-kit/migrations",     // stable, url-safe
  "type": "skill",                          // skill|agent|command|hook|mcp|lsp|workflow|output-style|monitor|doc
  "plugin": "review-kit",                   // null for repo-level docs
  "name": "migrations",
  "title": "migrations",                    // frontmatter name if present, else name
  "invocation": "/review-kit:migrations",   // skills and commands only
  "description": "Use when the user asks to review a database migration.",
  "keywords": ["sql", "migration", "review"],
  "category": "development",
  "body": "…markdown after frontmatter…",
  "headings": ["Checklist", "What to flag"],
  "path": "plugins/review-kit/skills/migrations/SKILL.md",
  "githubUrl": "https://github.com/Holubinka/claude-plugins/blob/main/…",
  "tokens": { "always": 14, "onLoad": 380 },
  "updatedAt": "2026-08-14T09:12:03Z",      // last commit touching the path
  "frontmatter": { … },                     // verbatim, for the detail page table
  "referencedFiles": ["references/dialects.md"]
}
```

`tokens.always` is the frontmatter `description` — Claude carries it in every turn while
the plugin is enabled. `tokens.onLoad` is the body, paid only when the skill fires. The
distinction is the whole point of the badge; the site labels them **Always** and
**On load** and never sums them into one number.

Estimation is `ceil(chars / 4)`, rendered with a `≈` and a footnote naming the
heuristic. It is not presented as exact.

### Plugin record

```jsonc
{
  "name": "review-kit",
  "description": "…",                       // from plugin.json; must match marketplace entry
  "version": "1.2.0",
  "author": { "name": "…" },
  "license": "MIT",
  "category": "development",
  "keywords": [...],
  "dependencies": [{ "name": "audit-logger", "range": "~2.1.0", "constrained": true }],
  "dependents": ["deploy-kit"],
  "artifacts": ["skill:review-kit/migrations", …],
  "tokens": { "always": 62 },               // Σ description tokens of all components
  "capabilities": { … },
  "health": [ … ],
  "releases": [ … ],
  "readme": "…markdown…",
  "hasEvals": true
}
```

### Capabilities

Facts extracted from `hooks/hooks.json`, `.mcp.json`, `.lsp.json` and skill frontmatter.

```jsonc
{
  "interceptsEvents": ["PreToolUse", "SessionStart"],
  "hookCommands": ["${CLAUDE_PLUGIN_ROOT}/scripts/guard.sh"],
  "mcpServers": [
    { "name": "jira", "transport": "stdio", "command": "npx", "args": [...],
      "envKeys": ["JIRA_TOKEN"], "hosts": [] }
  ],
  "lspServers": [...],
  "networkHosts": ["api.atlassian.com"],    // from http/sse MCP URLs only
  "bundledScripts": ["scripts/guard.sh"],
  "allowedTools": ["Read", "Grep"]          // union of skill frontmatter, when declared
}
```

**Design decision: facts, not a score.** The panel never renders "risk: medium". It
lists what the plugin intercepts, what it executes and which environment variables it
reads by name. A score invites the reader to stop reading; a list makes them look.
Environment variable **values** are never read, only key names.

### Health checks

Per plugin, each `{ code, level, message }`, rendered as badges.

| Code | Level | Check |
| :--- | :--- | :--- |
| `E101` | error | Plugin has no `description`, or it is shorter than 40 characters |
| `E102` | error | Marketplace entry `description` disagrees with `plugin.json` |
| `E103` | error | Plugin registered but exposes zero components |
| `W101` | warn | Fewer than two `keywords` |
| `W102` | warn | No plugin `README.md` |
| `W103` | warn | No `evals/` directory |
| `W104` | warn | Skill `description` reads as a summary, not a trigger condition |
| `W105` | warn | Current `version` has no matching `<plugin>--v<version>` git tag |
| `W106` | warn | Unconstrained dependency on a plugin the manifest relies on |
| `W107` | warn | Two skill descriptions overlap above the collision threshold |
| `W108` | warn | Search payload is over the single-file budget — time to split into tiers |
| `W109` | warn | No `<dep>--v*` tag satisfies a constrained dependency (`no-matching-tag`) |
| `E105` | error | A manifest, hook, MCP or LSP config is unreadable or invalid JSON |

Codes are namespaced at `1xx` so they never collide with `lint-structure.py`'s `E001`–
`E008` / `W003`–`W004`. `W104` is a heuristic: the description does not open with a
trigger phrase (`use when`, `when the user`, `for when`, …) and contains no `when`.

`--check` mode exits 1 on any error and prints warnings, matching `lint-structure.py`'s
behaviour exactly.

### Output files

| File | Where | Consumed |
| :--- | :--- | :--- |
| `catalog.json` | `site/src/data/` | At build, by Astro, for prerendering |
| `search-docs.json` | `site/public/data/` | At runtime, by the search island |
| `graph.json` | `site/public/data/` | Dependency graph page (precomputed layout) |
| `collisions.json` | `site/public/data/` | Trigger inspector |
| `stats.json` | `site/public/data/` | Home page counters |

`search-docs.json` holds the documents, not a serialized index: MiniSearch's `toJSON`
format is a JavaScript structure tied to the library version, so producing it from
Python would couple the indexer to a dependency it does not have. The browser builds the
index from these documents on load — milliseconds at this catalogue size. Once the
payload approaches the tier split, a small Node step in the Astro build pre-serializes
them with `MiniSearch.loadJSON`, and nothing about the Python contract changes.

Array fields (`keywords`, `headings`) stay arrays. The site joins them through
MiniSearch's `extractField` rather than shipping the same data in two shapes.

---

## Search

### Engine configuration

```js
{
  fields: ['title', 'description', 'keywords', 'headings', 'body'],
  storeFields: ['id','type','plugin','name','title','description','keywords','tokens','url'],
  searchOptions: {
    boost:  { title: 6, keywords: 4, description: 4, headings: 2, body: 1 },
    prefix: true,
    fuzzy:  term => term.length > 4 ? 0.2 : 0,
    combineWith: 'AND'
  }
}
```

`combineWith: 'AND'` with an automatic fallback to `'OR'` when AND returns nothing —
long natural-language queries otherwise return zero results.

**Why field weights work here.** `docs/plugin-structure.md` already requires a skill's
`description` to be written as a trigger condition, not a summary. The user's query
("I need a skill that…") and the field we rank against are therefore the same genre of
sentence. That alignment, not the algorithm, is what makes lexical search sufficient at
this catalogue size.

### Query preprocessing

1. Lowercase, strip diacritics, collapse whitespace.
2. Remove boilerplate lead-ins from a maintained phrase list: `i need`, `i want`,
   `is there a`, `something to`, `help me`, `how do i`, `a skill for`, `a plugin that`.
3. If a type word survives (`skill`, `agent`, `command`, `hook`, `mcp`), apply a **soft
   boost ×1.5** to that type — never a hard filter, because the user is guessing at our
   taxonomy.
4. An exact plugin or artifact name match is pinned to the top of the results.
5. Queries shorter than two characters return the browse view, not an empty result.

### Result presentation

Each card shows: type badge, owning plugin, title, the trigger line, keyword chips, the
**Always** token badge, and a highlighted snippet **taken from the field that actually
matched**. Showing why a result matched is a correctness requirement, not decoration —
without it a fuzzy hit is indistinguishable from a wrong one.

### URL state

`?q=&type=&plugin=&category=&kw=` — every facet is in the query string, so a search is
shareable and the README can link into a pre-filtered view. State is written with
`replaceState` (debounced 300 ms) so search does not flood browser history.

### Index budget

Single index file while it stays under **150 KB gzipped**. Past that, split into a
tier-A index (`title`, `description`, `keywords`, `headings`) loaded eagerly and a
tier-B body index fetched on idle, with results merged once B arrives. The build fails
with `E104` if tier A alone exceeds 400 KB gzipped.

---

## Pages

| Route | Contents |
| :--- | :--- |
| `/` | Search, facets, browse-by-category, catalogue stats |
| `/p/<plugin>/` | Overview, components, capabilities, health, dependencies, releases, README |
| `/p/<plugin>/<type>/<name>/` | One artifact: frontmatter table, rendered body, tokens, source link |
| `/bundle/` | Bundle builder |
| `/triggers/` | Trigger inspector and collision report |
| `/graph/` | Dependency graph |
| `/releases/` | What's new across the catalogue; `feed.xml` alongside |
| `/docs/<slug>/` | Repository docs, rendered, section-anchored, and indexed |
| `/404.html` | Search box seeded with the attempted path |

All prerendered via `getStaticPaths` from `catalog.json`. Only `/`, `/bundle/` and
`/triggers/` hydrate an island.

### Artifact page

Sections, in order: identity (type, plugin, invocation, version, last updated) → install
block → **what makes it fire** (the description, verbatim, framed as the trigger) →
token cost, both numbers, explained → rendered body → frontmatter table → referenced
files → capabilities, if any → source link.

The "what Claude actually sees" framing on this page is the site's most useful
educational surface: the description is always in context, the body is not.

### Install block

On every card and every page, one click copies:

```
/plugin marketplace add Holubinka/claude-plugins
/plugin install <plugin>@dev-workbench
```

with a secondary, collapsed variant for local development:

```
claude --plugin-dir ./plugins/<plugin>
```

`dev-workbench` and the repository slug come from `marketplace.json` and the git remote —
never hardcoded in the site.

---

## Features beyond search

### Bundle builder — `/bundle/`

Select plugins, get one copy-paste install block. Shows the union of their capabilities,
the resolved dependency closure, the combined **Always** token cost, and a warning when
two selected plugins declare incompatible version ranges for a shared dependency
(`range-conflict` — see [plugin-structure.md](../plugin-structure.md)). State lives in
`?plugins=a,b,c`, so a team lead can share an onboarding link.

### Trigger inspector — `/triggers/`

A textarea for a real user prompt. Runs the same engine restricted to invocable types
and renders the ranked candidates with score bars and the matched phrase.

It carries a permanent, non-dismissible disclaimer: **this approximates lexical overlap
with skill descriptions; it is not Claude's routing.** Presenting a heuristic as ground
truth would be worse than not shipping the page.

Below it, the **collision report**: pairs of skill descriptions whose TF-IDF cosine
similarity exceeds `0.55`, computed at build time in pure Python. Overlapping triggers
are the failure mode that makes two good skills both unreliable, and nothing else in the
toolchain looks for them.

### Dependency graph — `/graph/`

Nodes are plugins, edges are declared dependencies labelled with their version range.
Layout (layered, by dependency depth) is computed in Python and emitted as coordinates;
the site renders static SVG with hover states. No graph library.

Edges are marked when the dependency is unconstrained (`W106`) or when a constrained
dependency has no satisfying `<plugin>--v<version>` tag — the `no-matching-tag` failure,
made visible before someone hits it at install time.

### Releases — `/releases/` and `feed.xml`

Built from tags matching `<plugin>--v<version>`: version, date, and the commit subjects
touching that plugin's path since the previous tag. Per-plugin history on the plugin
page, a combined feed on `/releases/`, and an Atom file so the catalogue can be
subscribed to without a backend.

### Health badges

The `health` array rendered on plugin pages and, as a compact row, on plugin cards.
This makes the site a third check alongside `claude plugin validate` and
`lint-structure.py`, and it is why `build-index.py --check` runs on pull requests.

### Empty results → prefilled issue

When a search returns nothing, offer a button that opens
`github.com/Holubinka/claude-plugins/issues/new` with the title and body prefilled from
the query. Failed searches are the only demand signal a backendless site can collect,
and this converts them into a roadmap instead of discarding them.

### Empty catalogue

`plugins/` is currently empty. The build must succeed, the home page must render a
deliberate empty state pointing at [CONTRIBUTING.md](../../CONTRIBUTING.md), and every
counter must read zero rather than crash. This is the state the site ships in, so it is
a first-class acceptance case, not an edge case.

---

## Interaction details

- `/` focuses the search box; `Cmd/Ctrl+K` opens it from anywhere; `Esc` clears.
- `↑`/`↓` move through results, `Enter` opens, `Cmd+Enter` copies the install command.
- Results region is `aria-live="polite"`; the input follows the ARIA combobox pattern.
- Facets are real checkboxes in a `fieldset`, usable and readable without JavaScript.
- Theme follows `prefers-color-scheme` with a manual toggle persisted in `localStorage`.
- A service worker precaches the shell and the index — the catalogue works offline.
- "Recently viewed" in `localStorage`, shown on the home page. No analytics, no cookies,
  no third-party requests at runtime.
- Respects `prefers-reduced-motion`. Contrast meets WCAG AA in both themes.

## Performance budgets

| Metric | Budget |
| :--- | :--- |
| Initial JS (island + MiniSearch), gzipped | ≤ 60 KB |
| Search index, gzipped | ≤ 150 KB before the tier split kicks in |
| Keystroke → rendered results, ≤ 2000 docs | < 50 ms |
| LCP, prerendered page, cable | < 1.5 s |

Budgets are asserted in CI; exceeding one fails the build rather than quietly shipping.

---

## Build and deploy

### `scripts/build-index.py`

Standard library only, consistent with `lint-structure.py`. Walks
`.claude-plugin/marketplace.json`, `plugins/*/`, `docs/*.md`, `README.md`,
`CONTRIBUTING.md`, and `git for-each-ref refs/tags` plus `git log` for dates and release
notes. Parses YAML frontmatter with a minimal reader (frontmatter here is flat
key/value and simple lists — no third-party YAML dependency).

```sh
python3 scripts/build-index.py            # write outputs
python3 scripts/build-index.py --check    # validate only, exit 1 on E1xx
```

### `.github/workflows/pages.yml`

Triggers: push to `main` (paths `plugins/**`, `docs/**`, `site/**`,
`.claude-plugin/**`, `README.md`, `CONTRIBUTING.md`), push of tags `*--v*`, and
`workflow_dispatch`.

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
```

Steps: checkout with `fetch-depth: 0` (tags and dates are part of the data) → `python3
scripts/build-index.py` → `npm ci` → `npm run build` → `actions/upload-pages-artifact`
→ `actions/deploy-pages`.

On pull requests the same build runs **without** deploying and uploads the site as a
workflow artifact, so a reviewer can download and open it.

### `validate.yml`

Add one step: `python3 scripts/build-index.py --check`. Metadata errors then block a
pull request even when the site is not being deployed.

### Hosting

Custom domain: `site/public/CNAME`, Astro `base: '/'`, `site:` set to the canonical
origin (used for `feed.xml` and canonical tags). `site/public/.nojekyll` so paths
beginning with `_` survive.

> **Open item.** The domain name is not yet chosen. Until it is, build with
> `base: '/claude-plugins/'` and no `CNAME`; switching is a two-line change plus a DNS
> record.

---

## Definition of done

- [ ] `build-index.py` produces a valid `catalog.json` from the current, empty repository
      and from a repository with at least two plugins, one of which declares hooks, an
      MCP server and a dependency.
- [ ] `--check` fails on a plugin missing a description and passes otherwise.
- [ ] Every artifact has a prerendered page reachable without JavaScript.
- [ ] Search returns the right skill for five natural-language probe queries written
      against the seeded catalogue, recorded as fixtures in `site/tests/queries.json`.
- [ ] Every result card explains its match with a highlighted snippet.
- [ ] Install command copies correctly from a card, an artifact page and the bundle page.
- [ ] Capability panel reports events, commands, MCP servers and env key names for the
      seeded plugin, and reports nothing at all for a plugin that declares none.
- [ ] Both token numbers appear, labelled, with the heuristic footnoted.
- [ ] Bundle builder round-trips through `?plugins=` and flags a range conflict.
- [ ] Trigger inspector shows its disclaimer and lists a seeded collision pair.
- [ ] Graph renders, marks an unconstrained edge, and marks a missing tag.
- [ ] `/releases/` and `feed.xml` reflect a pushed `<plugin>--v<version>` tag.
- [ ] Empty catalogue renders the empty state instead of failing.
- [ ] Keyboard path — `Cmd+K`, arrows, `Enter` — works with no mouse.
- [ ] Performance budgets pass in CI.
- [ ] Lighthouse accessibility ≥ 95 on home, plugin and artifact pages.

## Later

Deliberately out of v1, in rough priority order:

1. **Semantic search.** Precomputed embeddings plus `transformers.js`, behind an opt-in
   toggle. Costs ~25 MB of model download and buys nothing at the current catalogue
   size — but the artifact record reserves an `embedding` field so it can be added
   without a schema change.
2. **giscus on plugin pages.** GitHub Discussions as the backend for comments and
   reactions — the only route to anything resembling a rating without a server.
3. **Nightly GitHub stats bake.** Stars and contributor counts fetched in a scheduled
   workflow and committed to a data file, since the browser cannot fetch them.
4. **Scaffold generator.** A form that emits a ready `plugin.json` and `SKILL.md` to
   copy, lowering the barrier described in [CONTRIBUTING.md](../../CONTRIBUTING.md).
5. **Side-by-side skill comparison.**
6. **Localisation.** The UI ships English-only, matching the repository's docs.
