import { layoutRing, polar, type AtlasSector } from "./atlas";
import type { XY } from "./layout";

/**
 * The wiki around a page's level, behind its cards: the atlas ring drawn as points. Every page of
 * the wiki is a point in a circular band round the cards, in its sector's wedge of the band, and
 * a point is bigger and brighter the fewer links its page is from the open one. Points within
 * `FIELD_HOPS` are tied by a line to the page they are reached through, so the links across the
 * circle show which clusters the open page pulls together.
 *
 * The cards are not in the middle of the circle: the open page's card sits out towards that
 * page's own point, as far as the cards round it fit inside the band, so the level is seen from
 * where the page is in the wiki. `growDir` says which way its clusters should run for that.
 *
 * The band's width comes from the number of pages, so points keep the same spacing whatever the
 * size of the wiki.
 */

type Link = { source: string; target: string };

export const FIELD_HOPS = 4;
export const NEAR_HOPS = 2;

/** Clear space between the cards and the band, and between two points in it. */
const BAND_GAP = 70;
/** The circle is this much wider than the cards need, which is the room they have to sit off-centre. */
const ROOM = 1.2;
const SPACING = 30;
/** The sector arcs sit this far outside the band, and the labels outside them. */
const ARC_OUT = 26;
/** Flow units: the level fits at about half zoom, where these read as 12px. */
export const LABEL_SIZE = 24;
const LABEL_CHAR = LABEL_SIZE * 0.62;
const LABEL_OUT = ARC_OUT + 22;
const LABEL_GAP = 20;

export interface Reach {
  hop: number;
  /** The page one link nearer the anchor that it was reached through. */
  via: string;
}

/** Breadth-first over the links, either direction: every page within `max` hops of the anchor. */
export function hopsFrom(anchor: string, edges: Link[], max = Infinity): Map<string, Reach> {
  const adj = new Map<string, string[]>();
  const add = (a: string, b: string) => {
    const list = adj.get(a);
    if (list) list.push(b);
    else adj.set(a, [b]);
  };
  for (const e of edges) {
    if (e.source === e.target) continue;
    add(e.source, e.target);
    add(e.target, e.source);
  }
  const out = new Map<string, Reach>();
  let frontier = [anchor];
  for (let hop = 1; hop <= max && frontier.length; hop++) {
    const next: string[] = [];
    for (const from of frontier) {
      for (const to of adj.get(from) ?? []) {
        if (to === anchor || out.has(to)) continue;
        out.set(to, { hop, via: from });
        next.push(to);
      }
    }
    frontier = next;
  }
  return out;
}

export interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
}

/**
 * Which way a page's clusters should run so that they grow into the circle from where the page is
 * on it: left (-1) for a page on the right of the ring, right (1) for one on the left, and both
 * ways (0) for one near the top or bottom, or not on the ring.
 */
export function growDir(sectors: AtlasSector[], id: string): -1 | 0 | 1 {
  const spike = layoutRing(sectors).spikes.find((s) => s.id === id);
  const side = spike ? Math.sin(spike.angle) : 0;
  return side > 0.5 ? -1 : side < -0.5 ? 1 : 0;
}

export interface FieldDot {
  id: string;
  x: number;
  y: number;
  /** Index into `Field.sectors`. */
  sector: number;
  /** Links from the open page; absent for a page no link reaches, 0 for the open page. */
  hop?: number;
  /** The page has a card on the canvas. */
  card: boolean;
  /** The page it is reached through and where that is drawn: a card's middle or another point. */
  via: string;
  from?: XY;
}

export interface FieldArc {
  sector: number;
  /** The sector's arc outside the band, as an SVG path. */
  d: string;
  /** Some page of the sector is a card or within `NEAR_HOPS`. */
  lit: boolean;
  /** What its points cover: what the view moves to when the sector is picked. */
  box: Box;
}

export interface FieldLabel {
  sector: number;
  text: string;
  x: number;
  y: number;
  anchor: "start" | "middle" | "end";
}

export interface Field {
  sectors: AtlasSector[];
  dots: FieldDot[];
  arcs: FieldArc[];
  labels: FieldLabel[];
  /** The band of points: its middle and its inner and outer radius. */
  circle: { x: number; y: number; inner: number; outer: number };
  /** The circle and its labels: what the level fits to. */
  frame: Box;
  /** Pages without a card within `NEAR_HOPS`, within `FIELD_HOPS`, and past that. */
  near: number;
  far: number;
  beyond: number;
}

const round = (n: number) => Math.round(n * 10) / 10;

/**
 * `box` is the cards' bounding box and `centreOf` the middle of a page's card, for the pages that
 * have one (`onCanvas`). Sector labels count every page of the sector within reach, cards included.
 */
export function layoutField(
  reach: Map<string, Reach>,
  onCanvas: Set<string>,
  box: Box,
  sectors: AtlasSector[],
  centreOf: (id: string) => XY | undefined,
  anchor?: string,
): Field {
  const ring = layoutRing(sectors);
  // The cards' corners from the open page's card: the circle is sized to hold them wherever on
  // it that page is, with room to spare so the cards can sit towards the page's own point.
  const home = (anchor && centreOf(anchor)) || { x: box.x + box.w / 2, y: box.y + box.h / 2 };
  const corners = [0, 1, 2, 3].map((i) => ({ x: box.x + (i % 2) * box.w - home.x, y: box.y + (i >> 1) * box.h - home.y }));
  const fit = Math.max(...corners.map((c) => Math.hypot(c.x, c.y))) * ROOM;
  const inner = fit + BAND_GAP;
  const origin = { cx: 0, cy: 0 };
  // As wide as gives every page SPACING squared of the band.
  const turn = ring.arcs.reduce((sum, a) => sum + a.end - a.start, 0);
  const outer = Math.sqrt(inner * inner + (2 * ring.spikes.length * SPACING * SPACING) / Math.max(turn, 0.01));
  const rows = Math.max(1, Math.round((outer - inner) / SPACING));
  const radii = Array.from({ length: rows }, (_, k) => inner + ((k + 0.5) * (outer - inner)) / rows);
  const total = radii.reduce((sum, r) => sum + r, 0);

  // A sector's pages fill its wedge row by row from the inside, best linked first, each row
  // taking a share in proportion to its length.
  const at = new Map<string, XY>();
  const sectorOf = new Map<string, number>();
  for (const arc of ring.arcs) {
    const ids = ring.sectors[arc.sector].pageIds;
    const size = arc.end - arc.start;
    const pad = Math.min(size * 0.2, (SPACING * 0.6) / outer);
    let done = 0;
    let share = 0;
    radii.forEach((r, k) => {
      share += r / total;
      const upTo = k === rows - 1 ? ids.length : Math.round(ids.length * share);
      const n = upTo - done;
      for (let j = 0; j < n; j++) {
        at.set(ids[done + j], polar(origin, arc.start + pad + ((j + 0.5) / n) * (size - 2 * pad), r));
        sectorOf.set(ids[done + j], arc.sector);
      }
      done = upTo;
    });
  }

  // The circle goes where the open page's own point is as near its card as the cards allow: the
  // card slides out along the line to its point until a corner of the cards meets the band.
  const own = anchor ? at.get(anchor) : undefined;
  const far = own ? Math.hypot(own.x, own.y) : 0;
  const u = own && far > 0 ? { x: own.x / far, y: own.y / far } : { x: 0, y: 0 };
  const out = own
    ? Math.min(...corners.map((c) => {
        const along = u.x * c.x + u.y * c.y;
        return -along + Math.sqrt(Math.max(0, along * along - c.x * c.x - c.y * c.y + fit * fit));
      }))
    : 0;
  const centre = { cx: home.x - u.x * out, cy: home.y - u.y * out };
  for (const [id, p] of at) at.set(id, { x: round(centre.cx + p.x), y: round(centre.cy + p.y) });

  const counts = new Map<number, number>();
  const lit = new Set<number>();
  const boxes = new Map<number, { x0: number; y0: number; x1: number; y1: number }>();
  let near = 0;
  let further = 0;
  let beyond = 0;
  const dots: FieldDot[] = [];
  for (const [id, p] of at) {
    const sector = sectorOf.get(id)!;
    const r = reach.get(id);
    const card = onCanvas.has(id);
    const hop = r?.hop ?? (card ? 0 : undefined);
    if (r || card) counts.set(sector, (counts.get(sector) ?? 0) + 1);
    if (card || (hop !== undefined && hop <= NEAR_HOPS)) lit.add(sector);
    if (r && !card) {
      if (r.hop <= NEAR_HOPS) near++;
      else if (r.hop <= FIELD_HOPS) further++;
      else beyond++;
    }
    const b = boxes.get(sector);
    if (b) {
      b.x0 = Math.min(b.x0, p.x);
      b.y0 = Math.min(b.y0, p.y);
      b.x1 = Math.max(b.x1, p.x);
      b.y1 = Math.max(b.y1, p.y);
    } else boxes.set(sector, { x0: p.x, y0: p.y, x1: p.x, y1: p.y });
    const via = card ? id : r?.via ?? "";
    dots.push({ id, x: p.x, y: p.y, sector, hop, card, via, from: card ? centreOf(id) : centreOf(via) ?? at.get(via) });
  }

  const arcR = outer + ARC_OUT;
  const arcs: FieldArc[] = ring.arcs.map((a) => {
    const from = polar(centre, a.start, arcR);
    const to = polar(centre, a.end, arcR);
    const b = boxes.get(a.sector)!;
    return {
      sector: a.sector,
      d: `M${round(from.x)} ${round(from.y)}A${round(arcR)} ${round(arcR)} 0 ${a.end - a.start > Math.PI ? 1 : 0} 1 ${round(to.x)} ${round(to.y)}`,
      lit: lit.has(a.sector),
      box: { x: b.x0 - SPACING, y: b.y0 - SPACING, w: b.x1 - b.x0 + SPACING * 2, h: b.y1 - b.y0 + SPACING * 2 },
    };
  });

  // Biggest sectors first; one that would run into a label already placed goes without.
  const labels: (FieldLabel & { mid: number; half: number })[] = [];
  let widest = 0;
  for (const [sector, n] of [...counts].sort(([a, x], [b, y]) => y - x || a - b)) {
    const angle = ring.arcs[sector].mid;
    const p = polar(centre, angle, outer + LABEL_OUT + LABEL_SIZE / 2);
    const text = `${ring.sectors[sector].label} · ${n}`;
    const width = text.length * LABEL_CHAR;
    const side = Math.sin(angle);
    const anchor = Math.abs(side) < 0.3 ? "middle" : side > 0 ? "start" : "end";
    const mid = p.x + (anchor === "middle" ? 0 : anchor === "start" ? width / 2 : -width / 2);
    if (labels.some((l) => Math.abs(l.y - p.y) < LABEL_SIZE + LABEL_GAP && Math.abs(l.mid - mid) < l.half + width / 2 + LABEL_GAP)) continue;
    widest = Math.max(widest, anchor === "middle" ? width / 2 : width);
    labels.push({ sector, text, x: round(p.x), y: round(p.y), anchor, mid, half: width / 2 });
  }

  const reachX = outer + LABEL_OUT + LABEL_SIZE + widest;
  const reachY = outer + LABEL_OUT + LABEL_SIZE * 2;
  return {
    sectors: ring.sectors,
    dots,
    arcs,
    labels: labels.map(({ sector, text, x, y, anchor }) => ({ sector, text, x, y, anchor })),
    circle: { x: round(centre.cx), y: round(centre.cy), inner, outer },
    frame: { x: centre.cx - reachX, y: centre.cy - reachY, w: reachX * 2, h: reachY * 2 },
    near,
    far: further,
    beyond,
  };
}
