import type { FitViewOptions, Node } from "@xyflow/react";
import { cardSize } from "../utils/clusterLayout";
import type { AtlasSector } from "../utils/atlas";
import { layoutField, type Reach } from "../utils/hopField";
import type { XY } from "../utils/layout";

/** The tallest a subset's layout is stretched to fill the canvas. */
const MAX_STRETCH = 2.2;

/** Fit padding that clears the status pill and level bar over the top of the canvas. */
export function fitPadding(padding: number): FitViewOptions["padding"] {
  return { top: "110px", right: padding, bottom: padding, left: padding };
}

/**
 * A subset of a semantic layout keeps its wide shape, which leaves a nearly square canvas half
 * empty and cards small. Stretch it vertically: distances between pages were never exact, and
 * the same subset always gets the same shape.
 */
export function fitToCanvasShape(positions: Record<string, XY>, ids: Set<string>): Record<string, XY> {
  let minY = Infinity;
  let maxY = -Infinity;
  let minX = Infinity;
  let maxX = -Infinity;
  for (const id of ids) {
    const p = positions[id];
    if (!p) continue;
    minX = Math.min(minX, p.x);
    maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y);
    maxY = Math.max(maxY, p.y);
  }
  const height = maxY - minY;
  if (!(height > 0)) return positions;
  const stretch = Math.min(MAX_STRETCH, Math.max(1, (maxX - minX) / height));
  if (stretch === 1) return positions;
  const out: Record<string, XY> = {};
  for (const [id, p] of Object.entries(positions)) out[id] = { x: p.x, y: minY + (p.y - minY) * stretch };
  return out;
}

export function positionsOf(nodes: Node[]): Record<string, XY> {
  return Object.fromEntries(nodes.map((n) => [n.id, n.position]));
}

/**
 * The wiki around the open page's clusters: every page a point in a ring, sized to hold the cards'
 * bounding box. `positions` are the cards' top-left corners, `depth` picks each card's size.
 */
export function layoutClusterField(
  positions: Record<string, XY>,
  depth: Map<string, number>,
  reach: Map<string, Reach>,
  sectors: AtlasSector[],
  anchorId: string | null,
) {
  const centres = new Map<string, XY>();
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const [id, p] of Object.entries(positions)) {
    const { w, h } = cardSize(depth.get(id) ?? 1);
    centres.set(id, { x: p.x + w / 2, y: p.y + h / 2 });
    minX = Math.min(minX, p.x);
    minY = Math.min(minY, p.y);
    maxX = Math.max(maxX, p.x + w);
    maxY = Math.max(maxY, p.y + h);
  }
  const box = { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
  return layoutField(reach, new Set(centres.keys()), box, sectors, (id) => centres.get(id), anchorId ?? undefined);
}
