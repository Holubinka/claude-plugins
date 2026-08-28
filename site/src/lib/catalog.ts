/** Types for what scripts/build-index.py writes. This mirrors the data contract in
 *  docs/tmp/site.md; if the two disagree, the Python side is authoritative. */

import raw from '../data/catalog.json';

export type ArtifactType =
  | 'skill' | 'agent' | 'command' | 'workflow' | 'output-style'
  | 'hook' | 'mcp' | 'lsp' | 'doc';

export interface TokenCost {
  /** Carried in every turn while the plugin is enabled. */
  always: number;
  /** Paid only when the component fires. */
  onLoad: number;
}

export interface Artifact {
  id: string;
  type: ArtifactType;
  plugin: string | null;
  name: string;
  title: string;
  invocation: string | null;
  description: string;
  keywords: string[];
  body: string;
  headings: string[];
  path: string;
  url: string;
  /** null where the always/on-load split is meaningless: hooks, servers, docs. */
  tokens: TokenCost | null;
  frontmatter: Record<string, unknown>;
  referencedFiles: string[];
  updatedAt: string | null;
  githubUrl: string | null;
  category: string | null;
  line?: number;
  doc?: { slug: string; title: string };
}

export interface Dependency {
  name: string;
  range: string | null;
  constrained: boolean;
  resolvable: boolean;
  marketplace: string | null;
}

export interface McpServer {
  name: string;
  transport: string;
  command: string | null;
  args: string[];
  /** Names only — the indexer never reads a value. */
  envKeys: string[];
  url: string | null;
  host: string | null;
}

export interface LspServer { name: string; command: string | null; args: string[] }

export interface Capabilities {
  interceptsEvents: string[];
  hookCommands: string[];
  mcpServers: McpServer[];
  lspServers: LspServer[];
  networkHosts: string[];
  bundledScripts: string[];
  allowedTools: string[];
}

export interface HealthEntry { code: string; level: 'error' | 'warn'; message: string }
export interface Release { version: string; tag: string; date: string; changes: string[] }

export interface Plugin {
  name: string;
  description: string;
  version: string | null;
  author: { name?: string; url?: string } | string | null;
  license: string | null;
  homepage: string | null;
  category: string | null;
  keywords: string[];
  registered: boolean;
  dependencies: Dependency[];
  dependents: string[];
  artifacts: string[];
  counts: Record<string, number>;
  tokens: { always: number };
  capabilities: Capabilities;
  hasEvals: boolean;
  readme: string | null;
  releases: Release[];
  updatedAt: string | null;
  githubUrl: string | null;
  url: string;
  semver: number[] | null;
}

export interface GraphNode {
  id: string; label: string; depth: number;
  x: number; y: number; width: number; height: number;
  version: string | null; artifacts: number;
}
export interface GraphEdge {
  from: string; to: string; range: string | null;
  constrained: boolean; resolvable: boolean; external: boolean;
}
export interface Graph { nodes: GraphNode[]; edges: GraphEdge[]; width: number; height: number }

export interface CollisionSide { id: string; plugin: string | null; name: string; description: string }
export interface Collision { score: number; a: CollisionSide; b: CollisionSide }

export interface Stats {
  plugins: number;
  artifacts: number;
  byType: Record<string, number>;
  categories: Record<string, number>;
  keywords: Record<string, number>;
  alwaysTokens: number;
  collisions: number;
  updatedAt: string | null;
}

export interface Marketplace {
  name: string | null;
  description: string | null;
  owner: { name?: string; url?: string } | null;
  repo: string | null;
  ref: string;
  install: { add: string | null; install: string; dev: string };
}

export interface Catalog {
  marketplace: Marketplace;
  generatedAt: string | null;
  plugins: Plugin[];
  artifacts: Artifact[];
  collisions: Collision[];
  graph: Graph;
  stats: Stats;
}

export const catalog = raw as unknown as Catalog;

export const { marketplace, plugins, artifacts, collisions, graph, stats } = catalog;

export const invocable: ArtifactType[] = ['skill', 'agent', 'command'];

export function plugin(name: string): Plugin | undefined {
  return plugins.find((p) => p.name === name);
}

export function artifactsOf(name: string): Artifact[] {
  return artifacts.filter((a) => a.plugin === name);
}

export function docSections(slug: string): Artifact[] {
  return artifacts.filter((a) => a.type === 'doc' && a.doc?.slug === slug);
}

export function docSlugs(): { slug: string; title: string }[] {
  const seen = new Map<string, string>();
  for (const a of artifacts) {
    if (a.doc && !seen.has(a.doc.slug)) seen.set(a.doc.slug, a.doc.title);
  }
  return [...seen].map(([slug, title]) => ({ slug, title }));
}

/** Newest release across every plugin, newest first. */
export function timeline(): { plugin: string; release: Release }[] {
  return plugins
    .flatMap((p) => p.releases.map((release) => ({ plugin: p.name, release })))
    .sort((a, b) => (a.release.date < b.release.date ? 1 : -1));
}

export function healthOf(p: Plugin, level: HealthEntry['level']): number {
  return (p as unknown as { health?: HealthEntry[] }).health?.filter((h) => h.level === level).length ?? 0;
}

export function health(p: Plugin): HealthEntry[] {
  return (p as unknown as { health?: HealthEntry[] }).health ?? [];
}
