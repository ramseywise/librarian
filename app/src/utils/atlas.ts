/**
 * The atlas ring, as pure geometry: which sector each page is in, the angle of its spike, how
 * long the spike is, where the labels go and what a pointer is over. components/atlas draws it.
 *
 * Angles are radians clockwise from 12 o'clock.
 */

import { courseColor, domainColor } from "../theme/domains";
import type { Theme } from "./theme";
import type { Curriculum } from "../types";
import type { Grouping } from "./mapRoute";

export const BEYOND_SECTOR = "beyond";

/**
 * Spike length, in links to and from a page. An ordinal scale: 1,239 pages split 12 / 81 / 521 /
 * 377 / 248 here (2026-11), where one open-ended "9+" would have held half the wiki.
 */
export const BANDS: { label: string; max: number }[] = [
  { label: "0–1", max: 1 },
  { label: "2–3", max: 3 },
  { label: "4–8", max: 8 },
  { label: "9–15", max: 15 },
  { label: "16+", max: Infinity },
];

export function bandOf(degree: number): number {
  return BANDS.findIndex((b) => degree <= b.max);
}

export interface AtlasPage {
  id: string;
  domain: string;
}

export interface AtlasSector {
  id: string;
  label: string;
  /** A colour, or `var(--token)` for one the theme decides; the canvas resolves it at draw time. */
  color: string;
  /** Best-linked first, which is also the order of its spikes. */
  pageIds: string[];
}

const byDegree = (degree: Map<string, number>) => (a: string, b: string) =>
  (degree.get(b) ?? 0) - (degree.get(a) ?? 0) || a.localeCompare(b);

/**
 * Directory sectors run largest first. Course sectors keep the curriculum's order, with pages in
 * by main course (the one that colours their cards) so each page is in exactly one sector.
 */
export function sectorsOf(
  pages: AtlasPage[],
  degree: Map<string, number>,
  grouping: Grouping,
  curriculum: Curriculum | null,
  theme?: Theme,
): AtlasSector[] {
  const buckets = new Map<string, string[]>();
  const add = (key: string, id: string) => {
    const list = buckets.get(key);
    if (list) list.push(id);
    else buckets.set(key, [id]);
  };
  const rank = byDegree(degree);

  if (grouping === "course" && curriculum) {
    for (const p of pages) add(curriculum.primaryCourse[p.id] ?? BEYOND_SECTOR, p.id);
    const out: AtlasSector[] = curriculum.courses
      .filter((c) => buckets.has(c.id))
      .map((c) => ({
        id: c.id,
        label: c.title,
        color: courseColor(c.id, theme),
        pageIds: buckets.get(c.id)!.sort(rank),
      }));
    const beyond = buckets.get(BEYOND_SECTOR);
    if (beyond) {
      out.push({
        id: BEYOND_SECTOR,
        label: "Not in a course",
        color: "var(--text-dim)",
        pageIds: beyond.sort(rank),
      });
    }
    return out;
  }

  for (const p of pages) add(p.domain, p.id);
  return [...buckets.entries()]
    .sort(([a, x], [b, y]) => y.length - x.length || a.localeCompare(b))
    .map(([id, ids]) => ({ id, label: id, color: domainColor(id, theme), pageIds: ids.sort(rank) }));
}

/** Which sector a page is in; for a link that has a page but no sector yet. */
export function sectorIdOf(page: AtlasPage, grouping: Grouping, curriculum: Curriculum | null): string {
  if (grouping === "course" && curriculum) return curriculum.primaryCourse[page.id] ?? BEYOND_SECTOR;
  return page.domain;
}

const TAU = Math.PI * 2;
const DEG = Math.PI / 180;
/** The gap at 12 o'clock holds the band labels. */
export const TOP_GAP = 13 * DEG;
const SECTOR_GAP = 1.5 * DEG;
/** Smallest arc a sector gets, so nine pages still read as a sector beside 435. */
const MIN_ARC = 2.5 * DEG;

export interface SectorArc {
  sector: number;
  start: number;
  end: number;
  mid: number;
}

export interface Spike {
  id: string;
  sector: number;
  /** Position in the ring: spikes are sorted by angle. */
  index: number;
  angle: number;
}

export interface Ring {
  sectors: AtlasSector[];
  arcs: SectorArc[];
  spikes: Spike[];
}

/** Arcs proportional to page count, with `MIN_ARC` as a floor. */
function arcSizes(counts: number[], available: number): number[] {
  const floored = new Set<number>();
  for (;;) {
    const rest = available - floored.size * MIN_ARC;
    const pages = counts.reduce((sum, n, i) => (floored.has(i) ? sum : sum + n), 0);
    const perPage = pages ? rest / pages : 0;
    const under = counts.findIndex((n, i) => !floored.has(i) && n * perPage < MIN_ARC);
    if (under < 0) return counts.map((n, i) => (floored.has(i) ? MIN_ARC : n * perPage));
    floored.add(under);
  }
}

export function layoutRing(sectors: AtlasSector[]): Ring {
  const live = sectors.filter((s) => s.pageIds.length > 0);
  const available = TAU - TOP_GAP - SECTOR_GAP * Math.max(0, live.length - 1);
  const sizes = arcSizes(
    live.map((s) => s.pageIds.length),
    available,
  );
  const arcs: SectorArc[] = [];
  const spikes: Spike[] = [];
  let at = TOP_GAP / 2;
  live.forEach((s, sector) => {
    const size = sizes[sector];
    arcs.push({ sector, start: at, end: at + size, mid: at + size / 2 });
    s.pageIds.forEach((id, i) => {
      const angle = at + ((i + 0.5) / s.pageIds.length) * size;
      spikes.push({ id, sector, index: spikes.length, angle });
    });
    at += size + SECTOR_GAP;
  });
  return { sectors: live, arcs, spikes };
}

export interface RingGeometry {
  width: number;
  height: number;
  cx: number;
  cy: number;
  /** Radius spikes start from, and the radius of the longest band. */
  inner: number;
  outer: number;
  /** Room for a sector label beside the ring. */
  labelWidth: number;
  /** Below this the centre card can't fit in the hole and sits under the ring. */
  cardInside: boolean;
}

const MIN_OUTER = 56;
const ARC_OFFSET = 7;

export interface RingInsets {
  left: number;
  top: number;
  bottom: number;
  labelWidth: number;
}

export function ringGeometry(width: number, height: number, insets: RingInsets): RingGeometry {
  const availW = Math.max(0, width - insets.left);
  const availH = Math.max(0, height - insets.top - insets.bottom);
  const outer = Math.max(MIN_OUTER, Math.min(availW / 2 - insets.labelWidth - 22, availH / 2 - 14));
  const inner = outer * 0.54;
  return {
    width,
    height,
    cx: insets.left + availW / 2,
    cy: insets.top + availH / 2,
    inner,
    outer,
    labelWidth: insets.labelWidth,
    cardInside: inner >= 96,
  };
}

/** Radius of a band's outer end. */
export function bandRadius(g: Pick<RingGeometry, "inner" | "outer">, band: number): number {
  return g.inner + ((g.outer - g.inner) * (band + 1)) / BANDS.length;
}

export const polar = (g: { cx: number; cy: number }, angle: number, r: number) => ({
  x: g.cx + r * Math.sin(angle),
  y: g.cy - r * Math.cos(angle),
});

export interface SectorLabel {
  sector: number;
  text: string;
  count: number;
  /** Where the leader leaves the arc. */
  from: { x: number; y: number };
  /** Text anchor point. */
  x: number;
  y: number;
  anchor: "start" | "end";
}

export const LABEL_ROW = 17;
/** Rough width of a label character at the label's font size; only used to truncate. */
export const LABEL_CHAR = 6.2;

function fitText(text: string, count: number, width: number): string {
  const room = Math.floor(width / LABEL_CHAR) - String(count).length - 1;
  return text.length <= room ? text : `${text.slice(0, Math.max(1, room - 1))}…`;
}

/**
 * One label per sector, spread down each side of the ring like a pie chart's: start beside the
 * arc, push down to clear the label above, then push back up if the column ran off the bottom.
 * Each side is a single column, so labels can't collide however small their sectors are.
 */
export function layoutLabels(ring: Ring, g: RingGeometry): SectorLabel[] {
  const reach = g.outer + ARC_OFFSET + 16;
  const top = 6 + LABEL_ROW / 2;
  const bottom = g.height - LABEL_ROW;
  const out: SectorLabel[] = [];

  for (const side of [1, -1] as const) {
    const column = ring.arcs
      .filter((a) => (a.mid <= Math.PI ? 1 : -1) === side)
      .map((a) => ({ arc: a, y: polar(g, a.mid, reach).y }))
      .sort((a, b) => a.y - b.y);
    for (let i = 0; i < column.length; i++) {
      const min = i === 0 ? top : column[i - 1].y + LABEL_ROW;
      column[i].y = Math.max(column[i].y, min);
    }
    for (let i = column.length - 1; i >= 0; i--) {
      const max = i === column.length - 1 ? bottom : column[i + 1].y - LABEL_ROW;
      column[i].y = Math.min(column[i].y, max);
    }
    for (const { arc, y } of column) {
      const s = ring.sectors[arc.sector];
      const dy = y - g.cy;
      const dx = Math.sqrt(Math.max(0, reach * reach - dy * dy));
      const x = g.cx + side * Math.max(dx, 14);
      // All the room on this side, not just what the ring reserved: the left has a free column.
      const room = side === 1 ? g.width - x - 6 : x - 6;
      out.push({
        sector: arc.sector,
        count: s.pageIds.length,
        text: fitText(s.label, s.pageIds.length, Math.max(g.labelWidth, room)),
        from: polar(g, arc.mid, g.outer + ARC_OFFSET + 2),
        x,
        y,
        anchor: side === 1 ? "start" : "end",
      });
    }
  }
  return out.sort((a, b) => a.sector - b.sector);
}

/** Pointer position to angle and radius about the ring's centre. */
export function toPolar(g: { cx: number; cy: number }, x: number, y: number): { angle: number; r: number } {
  const dx = x - g.cx;
  const dy = y - g.cy;
  const angle = Math.atan2(dx, -dy);
  return { angle: angle < 0 ? angle + TAU : angle, r: Math.hypot(dx, dy) };
}

/** The spike nearest `angle`, if one is within `tolerance`. Spikes are sorted, so a binary search. */
export function spikeAt(spikes: Spike[], angle: number, tolerance: number): Spike | null {
  if (!spikes.length) return null;
  let lo = 0;
  let hi = spikes.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (spikes[mid].angle < angle) lo = mid + 1;
    else hi = mid;
  }
  const after = spikes[lo];
  const before = spikes[Math.max(0, lo - 1)];
  const best = Math.abs(before.angle - angle) <= Math.abs(after.angle - angle) ? before : after;
  return Math.abs(best.angle - angle) <= tolerance ? best : null;
}

export type RingHit = { kind: "spike"; spike: Spike } | { kind: "sector"; sector: number } | null;

/** What a pointer is over. Spikes take their whole radial lane, not just their drawn length. */
export function hitTest(ring: Ring, g: RingGeometry, x: number, y: number): RingHit {
  const { angle, r } = toPolar(g, x, y);
  if (r >= g.inner - 8 && r <= g.outer + 3) {
    const spike = spikeAt(ring.spikes, angle, 3 / Math.max(r, 1));
    return spike && { kind: "spike", spike };
  }
  if (r > g.outer + 3 && r <= g.outer + ARC_OFFSET + 9) {
    const arc = ring.arcs.find((a) => angle >= a.start && angle <= a.end);
    return arc ? { kind: "sector", sector: arc.sector } : null;
  }
  return null;
}

export const ARC_RADIUS_OFFSET = ARC_OFFSET;
