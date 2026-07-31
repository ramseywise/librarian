import dagre from "dagre";
import type { Node, Edge } from "@xyflow/react";

const NODE_W = 190;
const NODE_H = 64;

export function applyDagreLayout(nodes: Node[], edges: Edge[]): Node[] {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "TB", nodesep: 80, ranksep: 100, marginx: 40, marginy: 40 });
  g.setDefaultEdgeLabel(() => ({}));

  nodes.forEach((n) => g.setNode(n.id, { width: NODE_W, height: NODE_H }));
  edges.forEach((e) => {
    if (g.hasNode(e.source) && g.hasNode(e.target)) {
      g.setEdge(e.source, e.target);
    }
  });

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
