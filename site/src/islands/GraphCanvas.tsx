/** The dependency graph, draggable.
 *
 * The server renders this same SVG, so the boxes and their links work with no JavaScript
 * at all — dragging is the part that needs the island. Positions live in state, edges are
 * recomputed from them on every frame, and a drag that moves less than a few pixels is
 * treated as a click so a box can be both grabbable and a link.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'preact/hooks';
import { href } from '../lib/url';

interface Row { type: string; name: string }
interface Node {
  id: string; label: string; depth: number; x: number; y: number;
  width: number; height: number; version: string | null;
  typeColumn: number; rows: Row[]; more: number;
}
interface Edge {
  from: string; to: string; range: string | null;
  constrained: boolean; resolvable: boolean; external: boolean;
  span: number; lane: number | null;
}
interface Graph {
  nodes: Node[]; edges: Edge[]; width: number; height: number;
  laneTop: number; laneGap: number; laneCount: number;
}

type Point = { x: number; y: number };
const CLICK_SLOP = 4;          // a pointer that moved less than this was a click, not a drag
const STORE = 'graph-positions:v1';

export default function GraphCanvas(
  { graph, label, hint, resetLabel }:
  { graph: Graph; label: string; hint: string; resetLabel: string },
) {
  const [moved, setMoved] = useState<Record<string, Point>>({});
  const svgRef = useRef<SVGSVGElement>(null);
  const drag = useRef<{ id: string; dx: number; dy: number; from: Point; slipped: boolean } | null>(null);

  // Restore an arrangement from a previous visit. A stored value can be absent, stale or
  // unreadable in a private window — none of which should stop the graph rendering.
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORE);
      if (raw) setMoved(JSON.parse(raw));
    } catch { /* no stored arrangement */ }
  }, []);

  const persist = useCallback((next: Record<string, Point>) => {
    try { localStorage.setItem(STORE, JSON.stringify(next)); } catch { /* not storable */ }
  }, []);

  const nodes = useMemo(
    () => graph.nodes.map((n) => (moved[n.id] ? { ...n, x: moved[n.id].x, y: moved[n.id].y } : n)),
    [graph.nodes, moved],
  );
  const byId = useMemo(() => new Map(nodes.map((n) => [n.id, n])), [nodes]);
  const outgoing = useMemo(() => {
    const m = new Map<string, string[]>();
    for (const e of graph.edges) m.set(e.from, (m.get(e.from) ?? []).concat(e.to));
    return m;
  }, [graph.edges]);

  /** Screen pixels to viewBox units. The SVG scales to its container, so a drag of 10
   *  screen pixels is not 10 units unless the two happen to match. */
  const toCanvas = (event: PointerEvent): Point => {
    const svg = svgRef.current;
    if (!svg) return { x: event.clientX, y: event.clientY };
    const box = svg.getBoundingClientRect();
    const scale = box.width / graph.width || 1;
    return { x: (event.clientX - box.left) / scale, y: (event.clientY - box.top) / scale };
  };

  const onDown = (event: PointerEvent, node: Node) => {
    if (event.button !== 0) return;
    const p = toCanvas(event);
    drag.current = { id: node.id, dx: p.x - node.x, dy: p.y - node.y, from: p, slipped: false };
    (event.currentTarget as Element).setPointerCapture?.(event.pointerId);
  };

  const onMove = (event: PointerEvent) => {
    const d = drag.current;
    if (!d) return;
    const p = toCanvas(event);
    if (!d.slipped && Math.hypot(p.x - d.from.x, p.y - d.from.y) < CLICK_SLOP) return;
    d.slipped = true;
    event.preventDefault();
    setMoved((prev) => ({
      ...prev,
      [d.id]: { x: Math.round(p.x - d.dx), y: Math.round(p.y - d.dy) },
    }));
  };

  const onUp = (event: PointerEvent) => {
    const d = drag.current;
    drag.current = null;
    if (!d) return;
    // A pointer that never slipped is a click, and the browser's own <a> handles it.
    if (d.slipped) { event.preventDefault(); setMoved((prev) => { persist(prev); return prev; }); }
  };

  const reset = () => { setMoved({}); try { localStorage.removeItem(STORE); } catch { /* nothing stored */ } };

  const edgePath = (edge: Edge) => {
    const from = byId.get(edge.from); const to = byId.get(edge.to);
    if (!from || !to) return null;
    const siblings = outgoing.get(edge.from) ?? [];
    const spread = (siblings.indexOf(edge.to) + 1) / (siblings.length + 1);
    const y1 = from.y + from.height * spread;
    const x1 = from.x;
    const x2 = to.x + to.width;
    const y2 = to.y + to.height / 2;
    if (edge.lane === null || edge.lane === undefined) {
      const bend = Math.max(48, Math.abs(x1 - x2) / 2);
      return { d: `M${x1} ${y1} C${x1 - bend} ${y1}, ${x2 + bend} ${y2}, ${x2 + 9} ${y2}`,
               label: { x: x1 - 10, y: y1 - 5, anchor: 'end' as const, text: edge.range ?? 'latest' } };
    }
    const r = 7;
    const laneY = graph.laneTop + edge.lane * graph.laneGap;
    const xa = x1 - 16; const xb = x2 + 22;
    return {
      d: [`M${x1} ${y1}`, `L${xa + r} ${y1}`, `Q${xa} ${y1} ${xa} ${y1 + r}`,
          `L${xa} ${laneY - r}`, `Q${xa} ${laneY} ${xa - r} ${laneY}`,
          `L${xb + r} ${laneY}`, `Q${xb} ${laneY} ${xb} ${laneY - r}`,
          `L${xb} ${y2 + r}`, `Q${xb} ${y2} ${xb - r} ${y2}`,
          `L${x2 + 9} ${y2}`].join(' '),
      label: { x: (xa + xb) / 2, y: laneY - 4, anchor: 'middle' as const,
               text: `${edge.from} → ${edge.to} ${edge.range ?? 'latest'}` },
    };
  };

  const dirty = Object.keys(moved).length > 0;

  return (
    <>
      <div class="graph-tools">
        <span class="hint">{hint}</span>
        {dirty && <button type="button" onClick={reset}>{resetLabel}</button>}
      </div>
      <div class="scroll figure">
        <svg ref={svgRef} viewBox={`0 0 ${graph.width} ${graph.height}`} role="img" aria-label={label}
             onPointerMove={onMove} onPointerUp={onUp} onPointerCancel={onUp}>
          <defs>
            <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M0 0 L8 4 L0 8 z" fill="currentColor" />
            </marker>
          </defs>
          <g class="edges">
            {graph.edges.map((edge) => {
              const geom = edgePath(edge);
              if (!geom) return null;
              const state = !edge.constrained ? 'loose' : edge.resolvable ? 'ok' : 'broken';
              const routed = edge.lane !== null && edge.lane !== undefined;
              return (
                <g class={`edge edge--${state}${routed ? ' edge--routed' : ''}`}>
                  <path d={geom.d} marker-end="url(#arrow)" />
                  <text x={geom.label.x} y={geom.label.y} text-anchor={geom.label.anchor}>{geom.label.text}</text>
                </g>
              );
            })}
          </g>
          <g class="nodes">
            {nodes.map((node) => (
              <g class="node" onPointerDown={(e: PointerEvent) => onDown(e, node)}>
                <rect x={node.x} y={node.y} width={node.width} height={node.height} rx="4" />
                <a href={href(`/p/${node.id}/`)}>
                  <text x={node.x + 14} y={node.y + 25} class="title">{node.label}</text>
                </a>
                <text x={node.x + 14} y={node.y + 40} class="sub">
                  {node.version ? `v${node.version}` : 'unversioned'}
                </text>
                <line x1={node.x} y1={node.y + 50} x2={node.x + node.width} y2={node.y + 50} />
                {node.rows.map((row, index) => (
                  <a href={href(`/p/${node.id}/${row.type}/${row.name}/`)}>
                    <text x={node.x + 14} y={node.y + 68 + index * 17} class="kind">{row.type}</text>
                    <text x={node.x + 14 + node.typeColumn} y={node.y + 68 + index * 17} class="part">{row.name}</text>
                  </a>
                ))}
                {node.more > 0 && (
                  <a href={href(`/p/${node.id}/`)}>
                    <text x={node.x + 14} y={node.y + 68 + node.rows.length * 17} class="sub">+{node.more} more</text>
                  </a>
                )}
              </g>
            ))}
          </g>
        </svg>
      </div>
    </>
  );
}
