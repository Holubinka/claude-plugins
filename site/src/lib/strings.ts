/**
 * Every user-facing string on this site, in one place.
 *
 * Nothing in `components/`, `pages/`, `islands/` or `layouts/` may hold display copy
 * of its own. Two reasons, and the second is the one that bites:
 *
 * 1. A second locale is then a sibling object below, not a hunt through 17 files.
 * 2. Copy is reviewable. Wording that decides whether someone trusts a finding —
 *    "tracks latest", "no-matching-tag — this install fails" — is a decision, and a
 *    decision buried in JSX is a decision nobody re-reads.
 *
 * **Exports are grouped by area on purpose.** `Search` and `Palette` are client
 * islands: they import their own group and nothing else, so the bundler drops the rest
 * rather than shipping the whole catalogue to the browser. Importing a single
 * aggregate object here would defeat that and eat into the 60 KB budget CI enforces.
 *
 * Interpolation is a function, or a `{placeholder}` template where it must cross
 * `define:vars` — never a sentence assembled from fragments at the call site, because a
 * string split across two files cannot be translated as one sentence.
 *
 * ## Adding a locale
 *
 * Copy this file to `strings.<code>.ts`, translate the values, and re-export the chosen
 * one from here. `Strings` types every group, so a missing key fails the build rather
 * than rendering `undefined`. Keys stay English; only values translate.
 */

export const locale = 'en';

/**
 * Fill `{name}` placeholders.
 *
 * Most interpolated copy below is a function, which is both typed and readable. A few
 * strings cannot be: Astro's `define:vars` hands values to an inline `<script>` through
 * JSON, and **a function does not survive that serialisation** — it arrives as
 * `undefined` and the page renders blank text with no error. Those strings are plain
 * templates with `{placeholders}`, marked as such, and filled with this helper on the
 * server or with `.replace()` inside the script.
 */
export function fill(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key) => String(vars[key] ?? ''));
}

/** Chrome shared by every page. */
export const chrome = {
  skipToContent: 'Skip to content',
  sectionsLabel: 'Sections',
  themeLabel: 'Theme',
  themeSwitch: 'Switch theme',
  themeSystem: 'System',
  themeLight: 'Light',
  themeDark: 'Dark',
  copy: 'Copy',
  copied: 'Copied',
  copyFallback: 'Press ⌘C',
  fallbackName: 'catalogue',
  brandMeta: (plugins: number, artifacts: number) =>
    `${plugins} plugins · ${artifacts} artifacts`,
  releasesFeed: (name: string) => `${name} releases`,
  footer: 'Built from the repository — every page here is generated, none is written by hand.',
  backToCatalogue: '← Back to the catalogue',
  sourceOnGitHub: 'Source on GitHub →',
  editOnGitHub: 'Edit on GitHub →',
} as const;

/** Navigation, and the descriptions the palette offers for each destination. */
export const nav = {
  items: [
    { label: 'Catalogue', path: '/' },
    { label: 'Bundle', path: '/bundle/' },
    { label: 'Triggers', path: '/triggers/' },
    { label: 'Graph', path: '/graph/' },
    { label: 'Releases', path: '/releases/' },
  ],
  catalogueDesc: 'Search every artifact in the marketplace',
  pageDesc: (label: string) => `The ${label.toLowerCase()} page`,
} as const;

export const home = {
  title: 'Ask for what you need',
  lede:
    'Search every skill, agent, command, hook, server and doc in this marketplace — ' +
    'the index is built from the repository, so it is never out of date.',
  plugins: 'Plugins',
  documentation: 'Documentation',
  documentationLede:
    'How this marketplace is built, released and reviewed. Every section is indexed.',
  glance: 'Catalogue at a glance',
  statPlugins: 'Plugins',
  statArtifacts: 'Artifacts',
  statByType: 'By type',
  statAlwaysTokens: 'Always-on tokens',
  statCollisions: 'Trigger collisions',
  statUpdated: 'Last change',
  /** Pluralises an artifact-type count on a plugin tile: "3 skills", "1 agent". */
  countOfType: (n: number, type: string) => `${n} ${type}${n === 1 ? '' : 's'}`,
} as const;

export const emptyCatalogue = {
  eyebrow: 'No plugins yet',
  body:
    'The catalogue is empty. This page is generated from the repository, so the first ' +
    'plugin merged into plugins/ appears here without anyone editing the site.',
  docsNote: 'The repository docs below are already indexed and searchable.',
  howTo: 'How to add one',
} as const;

/** Client island. Imported into the browser bundle — keep it small. */
export const search = {
  placeholder: 'What do you need? e.g. a skill that reviews migrations',
  keyMove: 'move',
  keyOpen: 'open',
  keyJump: 'jump anywhere',
  keyClear: 'clear',
  loading: 'Loading index…',
  failed: 'Search index failed to load. The pages below still work.',
  noMatch: (query: string) => `Nothing matches “${query}”`,
  noMatchFiltered: 'Nothing matches those filters.',
  matchCount: (n: number) => `${n} ${n === 1 ? 'match' : 'matches'}`,
  /** Facet legends. The key is the field name; this is what a reader sees. */
  facetType: 'type',
  facetPlugin: 'plugin',
  facetCategory: 'category',
  facetKeyword: 'keyword',
  /** Shown under the keyword row when the tail is hidden — see FACET_LIMIT. */
  facetMore: (n: number) => `+${n} more, reachable by searching`,
  browsing: (n: number) => `Browsing ${n} artifacts. Type to search, or filter below.`,
  emptyTitle: 'No artifact in this marketplace matches that.',
  askForIt: 'Ask for it',
  emptyAside:
    'A search that finds nothing is the only demand signal a site without a backend can collect.',
  issueTitle: (query: string) => `Plugin request: ${query}`,
  issueBody: (query: string) =>
    `Searched the catalogue for:\n\n> ${query}\n\nNothing matched. Is this worth building?`,
  always: 'always',
} as const;

/** Client island. Imported into the browser bundle — keep it small. */
export const palette = {
  dialogLabel: 'Jump to',
  placeholder: 'Jump to a skill, a doc or a page…',
  loading: 'Loading…',
  empty: 'Nothing matches that.',
  groupRecent: 'Recently viewed',
  groupInvocable: 'Skills and agents',
  groupDocs: 'Documentation',
  groupPages: 'Pages',
  keyMove: 'move',
  keyOpen: 'open',
  keyClose: 'close',
} as const;

export const install = {
  label: 'Install',
  ariaLabel: 'Install',
  devSummary: 'Load it from a working tree instead',
  devNote: 'Run /reload-plugins after each edit.',
} as const;

export const tokens = {
  always: 'Always',
  alwaysNote: 'Carried in every turn while the plugin is enabled.',
  onLoad: 'On load',
  onLoadNote: 'Paid only when it fires.',
  inlineTitle: 'Always in context / paid on load',
  inlineAlways: 'always',
  inlineOnLoad: '· on load',
} as const;

export const health = {
  none: 'no findings',
  colCode: 'Code',
  colFinding: 'Finding',
  errors: (n: number) => `${n} error${n === 1 ? '' : 's'}`,
  warnings: (n: number) => `${n} warning${n === 1 ? '' : 's'}`,
} as const;

export const capabilities = {
  heading: 'What it does to your machine',
  nothingDeclared: 'nothing declared',
  factsNotScore: 'facts, not a score',
  empty:
    'This plugin declares no hooks, no servers and no bundled scripts. It adds ' +
    'instructions to the conversation and nothing else.',
  intercepts: 'Intercepts',
  runs: 'Runs',
  mcpServers: 'MCP servers',
  lspServers: 'LSP servers',
  network: 'Network',
  bundledScripts: 'Bundled scripts',
  declaredTools: 'Tools its skills declare',
  over: 'over',
  as: 'as',
  to: 'to',
  reads: 'reads',
  footnote: 'Environment variables are listed by name. Nothing here reads a value.',
} as const;

export const pluginPage = {
  eyebrow: 'Plugin',
  version: 'Version',
  author: 'Author',
  license: 'License',
  category: 'Category',
  alwaysCost: 'Always-on cost',
  alwaysCostUnit: 'tokens',
  updated: 'Updated',
  components: 'Components',
  noComponents:
    'This plugin exposes no components. That is almost always a layout mistake — see',
  noComponentsLink: 'plugin structure',
  healthHeading: 'Health',
  dependencies: 'Dependencies',
  colRequires: 'Requires',
  colRange: 'Range',
  colResolves: 'Resolves',
  unconstrained: 'unconstrained',
  tracksLatest: 'tracks latest',
  resolves: 'a tag satisfies it',
  noMatchingTag: 'no-matching-tag',
  requiredBy: 'Required by',
  releases: 'Releases',
  colVersion: 'Version',
  colDate: 'Date',
  colChanges: 'Changes',
  readme: 'README',
} as const;

export const artifactPage = {
  crumbRoot: 'catalogue',
  pluginVersion: 'Plugin version',
  updated: 'Updated',
  source: 'Source',
  triggerEyebrow: 'What makes it fire',
  noDescription:
    'No description. Claude has nothing to decide on, so this will not fire reliably.',
  triggerAside:
    'This sentence is the whole of what Claude sees when deciding whether to load it. ' +
    'The body below costs nothing until it does.',
  contextCost: 'Context cost',
  contextCostFormula: '≈ chars ÷ 4',
  bodyHeading: 'What Claude receives',
  frontmatter: 'Frontmatter',
  referencedFiles: 'Files it reads on demand',
} as const;

export const bundle = {
  title: 'Bundle builder',
  description:
    'Pick several plugins and get one install block, with their combined context cost and capabilities.',
  eyebrow: 'Bundle',
  heading: 'Set someone up in one paste',
  lede:
    'Tick the plugins a machine should have. You get one block of commands that installs ' +
    'them and everything they depend on, and the cost of carrying them before you commit ' +
    'to it. The selection lives in the URL, so the link itself is the instruction.',
  empty: 'Nothing to bundle yet — the catalogue is empty.',
  pick: 'Pick',
  takeItAway: 'What to paste',
  installBlock: 'Install block',
  placeholder:
    'Tick a plugin and the commands appear here — including anything it depends on, ' +
    'which you then do not have to go and look up.',
  selected: 'Selected',
  alwaysTokens: 'Always-on tokens',
  costNote:
    'Always-on cost is what these plugins add to every turn while they are enabled, ' +
    'before any skill fires. Conflicting version ranges are flagged here too.',
  /** Templates — all three cross `define:vars` into the bundle builder's script. */
  pulledIn: 'Pulled in as dependencies: {names}',
  conflict: 'range-conflict — {detail}',
  conflictDetail: '{dep}: {firstFrom} wants {firstRange}, {secondFrom} wants {secondRange}',
} as const;

export const graph = {
  title: 'Dependency graph',
  description: 'Which plugins depend on which, and which of those dependencies cannot resolve.',
  eyebrow: 'Graph',
  heading: 'What depends on what',
  lede:
    'Each box lists what that plugin installs; the arrows point at what it drags in with ' +
    'it, labelled with the range it asks for. Layout is computed by the indexer and drawn ' +
    'as static SVG — no graph library ships to your browser.',
  empty: 'No plugins yet, so there is nothing to draw.',
  figureLabel: (n: number) =>
    `Dependency graph: ${n} plugins, the components each installs, and the version range ` +
    'each dependency asks for',
  latest: 'latest',
  unversioned: 'unversioned',
  artifacts: 'artifacts',
  problems: 'Edges worth looking at',
  allClean: 'every dependency is constrained and resolves',
  colFrom: 'From',
  colTo: 'To',
  colRange: 'Range',
  colProblem: 'Problem',
  tracksLatest: 'tracks latest — an upstream release can change behaviour',
  noMatchingTag: 'no-matching-tag — this install fails',
} as const;

export const triggers = {
  title: 'Trigger inspector',
  description:
    'Which skills a prompt would plausibly reach, and which skill descriptions compete with each other.',
  eyebrow: 'Triggers',
  heading: 'Which skill would this reach?',
  lede:
    'Paste a prompt the way a user would type it. The ranking below is the same lexical ' +
    'engine the catalogue search uses, run against skill descriptions only.',
  cautionEyebrow: 'Read this before trusting the ranking',
  caution:
    "This approximates lexical overlap with skill descriptions. It is not Claude's " +
    'routing, and it cannot be — Claude weighs the whole conversation, not a bag of ' +
    'words. Use it to spot descriptions that are too vague or too similar, not to ' +
    'predict what will fire.',
  promptLabel: 'Prompt',
  promptPlaceholder: 'I need something that checks a database migration before it ships',
  noCandidates: 'No invocable components in the catalogue yet, so there is nothing to rank.',
  /** Template — crosses `define:vars`. `{n}` is the candidate count. */
  ranking: 'Ranking {n} invocable components.',
  noOverlap:
    'Nothing overlaps this prompt — which usually means a description is missing or too narrow.',
  /** Template — crosses `define:vars`. `{terms}` is a comma-separated list. */
  matched: 'matched: {terms}',
  collisions: 'Colliding triggers',
  collisionsLede:
    'Pairs whose descriptions overlap above the threshold, computed at build time. ' +
    'Two skills competing for the same prompt make each other unreliable, and nothing ' +
    'else in the toolchain looks for this.',
  noCollisions: 'no descriptions overlap above the threshold',
  colScore: 'Score',
  colOne: 'One',
  colOther: 'The other',
} as const;

export const releases = {
  title: 'Releases',
  description: 'Every tagged release across the catalogue, newest first.',
  eyebrow: 'Releases',
  heading: 'What changed, and when',
  ledePrefix: 'Built from',
  ledeSuffix:
    'tags. Nothing reaches an installed plugin until its version changes, so this list ' +
    'is also the list of what users actually received.',
  feedLink: 'Atom feed →',
  emptyPrefix: 'No tagged releases yet. Tags are what dependency constraints resolve against — see',
  emptyLink: 'releasing',
} as const;

export const docs = {
  eyebrow: 'Documentation',
  onThisPage: 'On this page',
} as const;

export const notFound = {
  title: 'Not found',
  eyebrow: '404',
  heading: 'That page is not here',
  lede:
    'It may have been renamed — renaming a skill is a major version change, and the old ' +
    'path stops working. Search for it instead.',
} as const;

/**
 * The shape every locale must satisfy. Add a translation by writing an object of this
 * type; a missing or renamed key is then a build error rather than a blank on a page.
 */
export interface Strings {
  locale: string;
  chrome: typeof chrome;
  nav: typeof nav;
  home: typeof home;
  emptyCatalogue: typeof emptyCatalogue;
  search: typeof search;
  palette: typeof palette;
  install: typeof install;
  tokens: typeof tokens;
  health: typeof health;
  capabilities: typeof capabilities;
  pluginPage: typeof pluginPage;
  artifactPage: typeof artifactPage;
  bundle: typeof bundle;
  graph: typeof graph;
  triggers: typeof triggers;
  releases: typeof releases;
  docs: typeof docs;
  notFound: typeof notFound;
}
