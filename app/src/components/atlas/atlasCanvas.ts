/**
 * Drawing the atlas. No React and no layout reads. Two stacked canvases: `drawRing` paints the
 * spikes and only runs when they change (or per frame during a morph); `drawHot` paints what the
 * pointer or keyboard is on and runs on hover, so hover never repaints 1,239 spikes.
 */

import {
  ARC_RADIUS_OFFSET,
  bandRadius,
  BANDS,
  type Ring,
  type RingGeometry,
  type Spike,
} from "../../utils/atlas";
import { fieldScale, FIELD_R, type AtlasField } from "../../utils/atlasField";

/** UI colours as the theme has them right now. */
export interface Palette {
  guide: string;
  dim: string;
  hot: string;
  bg: string;
}

export function readPalette(): Palette {
  const css = getComputedStyle(document.documentElement);
  const read = (name: string, fallback: string) => css.getPropertyValue(name).trim() || fallback;
  return {
    guide: read("--border-strong", "#333"),
    dim: read("--border-emphasis", "#444"),
    hot: read("--text-strong", "#f0f0f0"),
    bg: read("--bg", "#0f0f0f"),
  };
}

/** A sector colour: a literal, or `var(--token)` the canvas can't read by itself. */
export function resolveColor(color: string): string {
  const m = /^var\((--[\w-]+)\)$/.exec(color);
  if (!m) return color;
  return getComputedStyle(document.documentElement).getPropertyValue(m[1]).trim() || "#888";
}

export interface Camera {
  x: number;
  y: number;
  k: number;
}

export const homeCamera = (g: RingGeometry): Camera => ({ x: g.width / 2, y: g.height / 2, k: 1 });

function applyCamera(ctx: CanvasRenderingContext2D, g: RingGeometry, cam: Camera, dpr: number): void {
  const k = cam.k * dpr;
  ctx.setTransform(k, 0, 0, k, dpr * (g.width / 2 - cam.k * cam.x), dpr * (g.height / 2 - cam.k * cam.y));
}

export function clear(ctx: CanvasRenderingContext2D, g: RingGeometry, dpr: number): void {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, g.width, g.height);
}

export const SPIKE_NORMAL = 0;
export const SPIKE_DIM = 1;
export const SPIKE_LIT = 2;
/** A page no lesson links yet: its sector's colour, but faint, so the course gaps show. */
export const SPIKE_FAINT = 3;
const FAINT_ALPHA = 0.32;

/** Per spike, parallel arrays: what a frame needs, without allocating per spike. */
export interface SpikeFrame {
  angle: Float64Array;
  /** Radius of the spike's tip. */
  tip: Float64Array;
  color: string[];
  state: Uint8Array;
}

export interface RingFrame {
  g: RingGeometry;
  ring: Ring;
  spikes: SpikeFrame;
  palette: Palette;
  cam: Camera;
  dpr: number;
  /** Sector arcs and guides are hidden mid-morph, when spikes are between sectors. */
  showStructure: boolean;
  /** Sectors with no match while a filter or search is active. */
  dimSectors: Set<number> | null;
  alpha: number;
  anyActive: boolean;
  /** The inner field of page dots, or null while it is not laid out (or mid-morph). */
  field: AtlasField | null;
  /** The view's zoom: labels and strokes are divided by it, so they stay one size on screen. */
  viewK: number;
  titles: string[];
}

export function drawRing(ctx: CanvasRenderingContext2D, f: RingFrame): void {
  const { g, spikes, palette, cam, dpr } = f;
  clear(ctx, g, dpr);
  applyCamera(ctx, g, cam, dpr);
  ctx.globalAlpha = f.alpha;
  ctx.lineCap = "butt";

  // Level guides, behind the spikes: a labelled scale, broken only by the label gap.
  ctx.strokeStyle = palette.guide;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(g.cx + g.inner, g.cy);
  ctx.arc(g.cx, g.cy, g.inner, 0, Math.PI * 2);
  for (let b = 0; b < BANDS.length; b++) {
    const r = bandRadius(g, b);
    ctx.moveTo(g.cx + r, g.cy);
    ctx.arc(g.cx, g.cy, r, 0, Math.PI * 2);
  }
  ctx.stroke();

  // Batched by colour and state: one path per bucket, whatever the spike count.
  const buckets = new Map<string, number[]>();
  const n = spikes.angle.length;
  for (let i = 0; i < n; i++) {
    const state = spikes.state[i];
    const key = state === SPIKE_DIM ? "dim" : `${state}|${spikes.color[i]}`;
    const list = buckets.get(key);
    if (list) list.push(i);
    else buckets.set(key, [i]);
  }
  const { cx, cy, inner } = g;
  for (const [key, list] of buckets) {
    const dim = key === "dim";
    const state = dim ? SPIKE_DIM : Number(key[0]);
    ctx.strokeStyle = dim ? palette.dim : key.slice(2);
    ctx.lineWidth = state === SPIKE_LIT ? 1.6 : 1;
    ctx.globalAlpha =
      f.alpha * (dim ? 0.55 : state === SPIKE_LIT ? 1 : state === SPIKE_FAINT ? FAINT_ALPHA : f.anyActive ? 0.95 : 0.85);
    ctx.beginPath();
    for (const i of list) {
      const s = Math.sin(spikes.angle[i]);
      const c = Math.cos(spikes.angle[i]);
      ctx.moveTo(cx + inner * s, cy - inner * c);
      ctx.lineTo(cx + spikes.tip[i] * s, cy - spikes.tip[i] * c);
    }
    ctx.stroke();
    if (state === SPIKE_LIT) {
      ctx.fillStyle = key.slice(2);
      ctx.beginPath();
      for (const i of list) {
        const px = cx + spikes.tip[i] * Math.sin(spikes.angle[i]);
        const py = cy - spikes.tip[i] * Math.cos(spikes.angle[i]);
        ctx.moveTo(px + 2.2, py);
        ctx.arc(px, py, 2.2, 0, Math.PI * 2);
      }
      ctx.fill();
    }
  }

  if (f.showStructure && f.field) drawField(ctx, f, f.field);

  if (f.showStructure) {
    ctx.lineWidth = 3;
    for (const arc of f.ring.arcs) {
      const dim = f.dimSectors?.has(arc.sector);
      ctx.globalAlpha = f.alpha * (dim ? 0.5 : 1);
      ctx.strokeStyle = dim ? palette.dim : resolveColor(f.ring.sectors[arc.sector].color);
      ctx.beginPath();
      ctx.arc(cx, cy, g.outer + ARC_RADIUS_OFFSET, arc.start - Math.PI / 2, arc.end - Math.PI / 2);
      ctx.stroke();
    }
  }
  ctx.globalAlpha = 1;
}

/** On-screen radius a dot needs before it gets a label; zooming in grows dots past it. */
export const LABEL_MIN_PX = 9;
const MAX_LABELS = 140;
const LABEL_PX = 11;

/**
 * Labels for `order` (most important first), each beside its dot, skipping any that would overlap
 * one already placed. Sizes are in ring units divided by the zoom, so text reads the same at any zoom.
 */
function drawLabels(
  ctx: CanvasRenderingContext2D,
  g: RingGeometry,
  field: AtlasField,
  order: number[],
  titles: string[],
  viewK: number,
  palette: Palette,
  color: string,
  max: number,
): void {
  const k = fieldScale(g);
  const px = LABEL_PX / viewK;
  ctx.font = `500 ${px}px system-ui, sans-serif`;
  ctx.textBaseline = "middle";
  ctx.lineJoin = "round";
  ctx.lineWidth = 3 / viewK;
  ctx.strokeStyle = palette.bg;
  ctx.fillStyle = color;
  const placed: [number, number, number, number][] = [];
  for (const i of order) {
    if (placed.length >= max) break;
    const text = titles[i];
    if (!text) continue;
    const label = text.length > 28 ? `${text.slice(0, 27)}…` : text;
    const x = g.cx + field.x[i] * k + field.r[i] * k + 2 / viewK;
    const y = g.cy + field.y[i] * k;
    const w = ctx.measureText(label).width;
    const box: [number, number, number, number] = [x, y - px / 2, x + w, y + px / 2];
    if (placed.some((b) => box[0] < b[2] && box[2] > b[0] && box[1] < b[3] && box[3] > b[1])) continue;
    placed.push(box);
    ctx.strokeText(label, x, y);
    ctx.fillText(label, x, y);
  }
}

/** The page dots inside the ring, their links faint behind them, and labels on the dots big enough to carry one. */
function drawField(ctx: CanvasRenderingContext2D, f: RingFrame, field: AtlasField): void {
  const { g, spikes, palette } = f;
  const k = fieldScale(g);
  const { cx, cy } = g;

  ctx.globalAlpha = f.alpha * 0.28;
  ctx.strokeStyle = palette.guide;
  ctx.lineWidth = 0.6 / f.viewK;
  ctx.beginPath();
  const links = field.links;
  for (let e = 0; e < links.length; e += 2) {
    const a = links[e];
    const b = links[e + 1];
    ctx.moveTo(cx + field.x[a] * k, cy + field.y[a] * k);
    ctx.lineTo(cx + field.x[b] * k, cy + field.y[b] * k);
  }
  ctx.stroke();

  const buckets = new Map<string, number[]>();
  for (let i = 0; i < field.x.length; i++) {
    const state = spikes.state[i];
    const key = state === SPIKE_DIM ? "dim" : `${state}|${spikes.color[i]}`;
    const list = buckets.get(key);
    if (list) list.push(i);
    else buckets.set(key, [i]);
  }
  for (const [key, list] of buckets) {
    const dim = key === "dim";
    const state = dim ? SPIKE_DIM : Number(key[0]);
    ctx.fillStyle = dim ? palette.dim : key.slice(2);
    ctx.globalAlpha = f.alpha * (dim ? 0.4 : state === SPIKE_FAINT ? 0.45 : state === SPIKE_LIT ? 1 : 0.88);
    ctx.beginPath();
    for (const i of list) {
      const x = cx + field.x[i] * k;
      const y = cy + field.y[i] * k;
      const r = field.r[i] * k;
      ctx.moveTo(x + r, y);
      ctx.arc(x, y, r, 0, Math.PI * 2);
    }
    ctx.fill();
  }

  // Labels: the biggest dots first, and only those large enough on screen at this zoom.
  const minR = LABEL_MIN_PX / (k * f.viewK);
  const order = [];
  for (let i = 0; i < field.x.length; i++) if (field.r[i] >= minR && spikes.state[i] !== SPIKE_DIM) order.push(i);
  order.sort((a, b) => field.r[b] - field.r[a]);
  ctx.globalAlpha = f.alpha;
  drawLabels(ctx, g, field, order, f.titles, f.viewK, palette, palette.hot, MAX_LABELS);
  ctx.globalAlpha = 1;
}

export interface HotFrame {
  g: RingGeometry;
  ring: Ring;
  spikes: SpikeFrame;
  palette: Palette;
  dpr: number;
  hover: Spike | null;
  cursor: Spike | null;
  /** Sector whose arc to thicken. */
  sector: number | null;
  field: AtlasField | null;
  viewK: number;
  titles: string[];
  /** Draw the selected page's wikilinks; off, only its similar pages show. */
  wikiLines?: boolean;
  /** The selected page's most similar pages, drawn dashed. */
  similar?: number[];
}

/**
 * The selected page and its neighbours: everything else in the field is veiled, the links to the
 * neighbours drawn in the page's colour, and each neighbour labelled.
 */
function drawFocus(ctx: CanvasRenderingContext2D, f: HotFrame, field: AtlasField, focus: number): void {
  const { g, spikes, palette, viewK } = f;
  const k = fieldScale(g);
  const { cx, cy } = g;
  const linked = f.wikiLines === false ? [] : (field.neighbours[focus] ?? []);
  const similar = (f.similar ?? []).filter((j) => j !== focus);
  const near = [...new Set([...linked, ...similar])];
  const at = (i: number) => ({ x: cx + field.x[i] * k, y: cy + field.y[i] * k, r: field.r[i] * k });

  ctx.globalAlpha = 0.78;
  ctx.fillStyle = palette.bg;
  ctx.beginPath();
  ctx.arc(cx, cy, FIELD_R * k + 3, 0, Math.PI * 2);
  ctx.fill();

  const self = at(focus);
  ctx.globalAlpha = 0.75;
  ctx.strokeStyle = spikes.color[focus];
  ctx.lineWidth = 1.2 / viewK;
  ctx.beginPath();
  for (const j of linked) {
    const p = at(j);
    ctx.moveTo(self.x, self.y);
    ctx.lineTo(p.x, p.y);
  }
  ctx.stroke();
  if (similar.length) {
    ctx.setLineDash([4 / viewK, 4 / viewK]);
    ctx.beginPath();
    for (const j of similar) {
      const p = at(j);
      ctx.moveTo(self.x, self.y);
      ctx.lineTo(p.x, p.y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
  }

  ctx.globalAlpha = 1;
  for (const j of [...near, focus]) {
    const p = at(j);
    ctx.fillStyle = spikes.color[j];
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.strokeStyle = palette.hot;
  ctx.lineWidth = 2.5 / viewK;
  ctx.beginPath();
  ctx.arc(self.x, self.y, self.r + 1.5 / viewK, 0, Math.PI * 2);
  ctx.stroke();

  // Their spikes on the rim too, so the ring shows where the neighbours sit.
  ctx.lineWidth = 1.4;
  for (const j of near) {
    const s = f.ring.spikes[j];
    if (!s) continue;
    const sin = Math.sin(s.angle);
    const cos = Math.cos(s.angle);
    ctx.strokeStyle = spikes.color[j];
    ctx.beginPath();
    ctx.moveTo(cx + g.inner * sin, cy - g.inner * cos);
    ctx.lineTo(cx + spikes.tip[j] * sin, cy - spikes.tip[j] * cos);
    ctx.stroke();
  }

  const order = [focus, ...[...near].sort((a, b) => field.r[b] - field.r[a])];
  drawLabels(ctx, g, field, order, f.titles, viewK, palette, palette.hot, 60);
}

/** Hovered and keyboard-selected spikes, drawn full length, and the current sector's arc. */
export function drawHot(ctx: CanvasRenderingContext2D, f: HotFrame): void {
  const { g, spikes, palette, dpr } = f;
  clear(ctx, g, dpr);
  const { cx, cy, inner } = g;

  const spike = (s: Spike, width: number) => {
    const sin = Math.sin(s.angle);
    const cos = Math.cos(s.angle);
    const tip = spikes.tip[s.index];
    ctx.lineWidth = width;
    ctx.strokeStyle = palette.hot;
    ctx.beginPath();
    ctx.moveTo(cx + (inner - 5) * sin, cy - (inner - 5) * cos);
    ctx.lineTo(cx + (tip + 3) * sin, cy - (tip + 3) * cos);
    ctx.stroke();
    ctx.fillStyle = palette.hot;
    ctx.beginPath();
    ctx.arc(cx + (tip + 3) * sin, cy - (tip + 3) * cos, width + 0.8, 0, Math.PI * 2);
    ctx.fill();
  };

  if (f.sector != null && f.ring.arcs[f.sector]) {
    const arc = f.ring.arcs[f.sector];
    ctx.lineWidth = 6;
    ctx.strokeStyle = resolveColor(f.ring.sectors[arc.sector].color);
    ctx.beginPath();
    ctx.arc(cx, cy, g.outer + ARC_RADIUS_OFFSET, arc.start - Math.PI / 2, arc.end - Math.PI / 2);
    ctx.stroke();
  }
  if (f.field && f.cursor) drawFocus(ctx, f, f.field, f.cursor.index);
  if (f.cursor) spike(f.cursor, 2);
  if (f.hover && f.hover !== f.cursor) {
    spike(f.hover, 1.6);
    if (f.field) {
      const k = fieldScale(g);
      const i = f.hover.index;
      ctx.globalAlpha = 1;
      ctx.strokeStyle = palette.hot;
      ctx.lineWidth = 1.6 / f.viewK;
      ctx.beginPath();
      ctx.arc(cx + f.field.x[i] * k, cy + f.field.y[i] * k, f.field.r[i] * k + 1.5 / f.viewK, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
  ctx.globalAlpha = 1;
}
