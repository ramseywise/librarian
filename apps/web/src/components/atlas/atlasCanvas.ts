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
    ctx.globalAlpha = f.alpha * (dim ? 0.55 : state === SPIKE_LIT ? 1 : f.anyActive ? 0.95 : 0.85);
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
  if (f.cursor) spike(f.cursor, 2);
  if (f.hover && f.hover !== f.cursor) spike(f.hover, 1.6);
}
