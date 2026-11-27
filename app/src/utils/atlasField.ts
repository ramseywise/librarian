/**
 * The atlas's inner field: one dot per page, filling the hole inside the ring. A dot's area
 * follows its link count, and it sits under its sector's arc, pulled a little towards the pages it
 * links. Laid out once per ring in a unit circle (radius `FIELD_R`) and scaled to the hole when drawn, so a
 * resize or a zoom never lays it out again.
 *
 * Node `i` here is spike `i` in the ring, so the spike frame's colours and states apply as they are.
 */

import { forceCollide, forceLink, forceSimulation, forceX, forceY, type SimulationNodeDatum } from "d3-force";
import type { Ring } from "./atlas";

export const FIELD_R = 1000;
/** Share of the disc the dots' area covers: full, with room for the collision gaps. */
const FILL = 0.5;
const TICKS = 160;

export interface FieldLink {
  // A link d3 has already resolved elsewhere carries the node itself; its id is what counts here.
  source: string | { id: string };
  target: string | { id: string };
}

const endId = (end: FieldLink["source"]) => (typeof end === "string" ? end : end?.id);

export interface AtlasField {
  x: Float64Array;
  y: Float64Array;
  /** Dot radius, in the same units as x and y. */
  r: Float64Array;
  /** Wikilinks as pairs of node indices: [a0, b0, a1, b1, ...]. */
  links: Int32Array;
  /** Per node, the indices of the pages it links or is linked from. */
  neighbours: number[][];
}

/** Relative dot size: a page with no links is still a dot, and a hub is a few times wider. */
export const dotWeight = (degree: number) => 1 + 0.45 * Math.sqrt(degree);

// Seeded, so the same wiki draws the same field every time.
function lcg(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

interface Body extends SimulationNodeDatum {
  i: number;
  r: number;
  tx: number;
  ty: number;
}

export function layoutField(ring: Ring, degree: Map<string, number>, edges: FieldLink[]): AtlasField {
  const n = ring.spikes.length;
  const index = new Map(ring.spikes.map((s, i) => [s.id, i]));
  const weights = ring.spikes.map((s) => dotWeight(degree.get(s.id) ?? 0));
  const scale = Math.sqrt((FILL * FIELD_R * FIELD_R) / Math.max(1, weights.reduce((sum, w) => sum + w * w, 0)));

  // Hubs towards the middle, small pages out under their arc: a page's rank in its sector (pages
  // are best-linked first) sets how far out it starts.
  const rankInSector = new Map<number, number>();
  const bodies: Body[] = ring.spikes.map((s, i) => {
    const sector = ring.sectors[s.sector];
    const rank = rankInSector.get(s.sector) ?? 0;
    rankInSector.set(s.sector, rank + 1);
    const out = FIELD_R * (0.18 + 0.72 * Math.sqrt((rank + 0.5) / sector.pageIds.length));
    const tx = out * Math.sin(s.angle);
    const ty = -out * Math.cos(s.angle);
    return { i, r: weights[i] * scale, tx, ty, x: tx, y: ty };
  });

  const pairs: number[] = [];
  const neighbours: number[][] = Array.from({ length: n }, () => []);
  const seen = new Set<string>();
  for (const e of edges) {
    const a = index.get(endId(e.source));
    const b = index.get(endId(e.target));
    if (a == null || b == null || a === b) continue;
    const key = a < b ? `${a}|${b}` : `${b}|${a}`;
    if (seen.has(key)) continue;
    seen.add(key);
    pairs.push(a, b);
    neighbours[a].push(b);
    neighbours[b].push(a);
  }

  if (n) {
    const links = [];
    for (let k = 0; k < pairs.length; k += 2) links.push({ source: pairs[k], target: pairs[k + 1] });
    const sim = forceSimulation<Body>(bodies)
      .randomSource(lcg(n * 7919 + pairs.length))
      .force("x", forceX<Body>((d) => d.tx).strength(0.09))
      .force("y", forceY<Body>((d) => d.ty).strength(0.09))
      .force(
        "link",
        forceLink<Body, { source: number; target: number }>(links)
          .id((d) => d.i)
          .distance((l) => ((l.source as unknown as Body).r + (l.target as unknown as Body).r) * 1.6)
          .strength(0.02),
      )
      .force("collide", forceCollide<Body>((d) => d.r + scale * 0.35).iterations(2))
      .stop();
    for (let t = 0; t < TICKS; t++) {
      sim.tick();
      // The ring is a wall: a dot that drifts out is put back just inside it.
      for (const b of bodies) {
        const room = FIELD_R - b.r;
        const d = Math.hypot(b.x!, b.y!);
        if (d > room) {
          b.x! *= room / d;
          b.y! *= room / d;
        }
      }
    }
  }

  const field: AtlasField = {
    x: new Float64Array(n),
    y: new Float64Array(n),
    r: new Float64Array(n),
    links: Int32Array.from(pairs),
    neighbours,
  };
  for (const b of bodies) {
    field.x[b.i] = b.x!;
    field.y[b.i] = b.y!;
    field.r[b.i] = b.r;
  }
  return field;
}

/** Ring pixels per field unit: the field fills the hole with a small margin inside the ring. */
export const fieldScale = (g: { inner: number }) => Math.max(0, g.inner - 6) / FIELD_R;

/** The dot under a point in ring coordinates, if any; `slop` widens small dots for the pointer. */
export function fieldHit(
  field: AtlasField,
  g: { cx: number; cy: number; inner: number },
  x: number,
  y: number,
  slop: number,
): number | null {
  const k = fieldScale(g);
  if (!k) return null;
  const fx = (x - g.cx) / k;
  const fy = (y - g.cy) / k;
  if (Math.hypot(fx, fy) > FIELD_R + slop / k) return null;
  let best: number | null = null;
  let bestGap = Infinity;
  for (let i = 0; i < field.x.length; i++) {
    const gap = Math.hypot(field.x[i] - fx, field.y[i] - fy) - Math.max(field.r[i], slop / k);
    if (gap <= 0 && gap < bestGap) {
      best = i;
      bestGap = gap;
    }
  }
  return best;
}
