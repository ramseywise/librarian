import dagre from "dagre";
import type { Node, Edge } from "@xyflow/react";

const NODE_W = 190;
const NODE_H = 64;

/**
 * The edges dagre ranks on: at most one incoming edge per node (first wins), no
 * self-loops, both ends present. Dagre's crossing minimisation is superlinear in edge
 * count: the full wikilink graph (~760 nodes, ~4.4k edges) took minutes, which froze the
 * tab on "Hierarchy" and on every domain filter. One parent per node keeps it ~100 ms.
 * Only positions come from this; the rendered edges are unaffected.
 */
export function layoutEdges<E extends { source: string; target: string }>(
  nodeIds: Set<string>,
  edges: E[],
): E[] {
  const hasParent = new Set<string>();
  const out: E[] = [];
  for (const e of edges) {
    if (e.source === e.target || hasParent.has(e.target)) continue;
    if (!nodeIds.has(e.source) || !nodeIds.has(e.target)) continue;
    hasParent.add(e.target);
    out.push(e);
  }
  return out;
}

export function applyDagreLayout(nodes: Node[], edges: Edge[]): Node[] {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "TB", nodesep: 80, ranksep: 100, marginx: 40, marginy: 40 });
  g.setDefaultEdgeLabel(() => ({}));

  nodes.forEach((n) => g.setNode(n.id, { width: NODE_W, height: NODE_H }));
  layoutEdges(new Set(nodes.map((n) => n.id)), edges).forEach((e) => g.setEdge(e.source, e.target));

  dagre.layout(g);

  return nodes.map((n) => {
    const pos = g.node(n.id);
    return pos
      ? { ...n, position: { x: pos.x - NODE_W / 2, y: pos.y - NODE_H / 2 } }
      : n;
  });
}

export function applyUmapLayout(
  nodes: Node[],
  positions: Record<string, { x: number; y: number }>
): Node[] {
  return nodes.map((n) => {
    const pos = positions[n.id];
    return pos ? { ...n, position: pos } : n;
  });
}

export type XY = { x: number; y: number };

function centroid(points: XY[]): XY | null {
  if (!points.length) return null;
  let x = 0;
  let y = 0;
  for (const p of points) {
    x += p.x;
    y += p.y;
  }
  return { x: x / points.length, y: y / points.length };
}

/**
 * Fill in positions for nodes missing from a cached layout (e.g. pages added after the
 * UMAP projection was cached), so they do not all pile up at the origin.
 *
 * A missing node goes to the centroid of its wikilink neighbours that have a cached
 * position; failing that, the centroid of the cached nodes in its primary domain;
 * failing that, the origin. Only cached positions are used as anchors, so the result
 * does not depend on node order. Returns a new map covering every node.
 */
export function placeMissingNodes(
  nodes: { id: string; data: { domain: string[] } }[],
  positions: Record<string, XY>,
  edges: { source: string; target: string }[],
): Record<string, XY> {
  const out: Record<string, XY> = { ...positions };
  const missing = nodes.filter((n) => !(n.id in positions));
  if (!missing.length) return out;

  const missingIds = new Set(missing.map((n) => n.id));
  const neighbours = new Map<string, XY[]>();
  const addNeighbour = (id: string, other: string) => {
    const p = positions[other];
    if (!missingIds.has(id) || !p) return;
    const list = neighbours.get(id);
    if (list) list.push(p);
    else neighbours.set(id, [p]);
  };
  for (const e of edges) {
    addNeighbour(e.source, e.target);
    addNeighbour(e.target, e.source);
  }

  const byDomain = new Map<string, XY[]>();
  for (const n of nodes) {
    const p = positions[n.id];
    const d = n.data.domain[0];
    if (!p || d === undefined) continue;
    const list = byDomain.get(d);
    if (list) list.push(p);
    else byDomain.set(d, [p]);
  }

  for (const n of missing) {
    const d = n.data.domain[0];
    out[n.id] =
      centroid(neighbours.get(n.id) ?? []) ??
      centroid(d !== undefined ? byDomain.get(d) ?? [] : []) ??
      { x: 0, y: 0 };
  }
  return out;
}
