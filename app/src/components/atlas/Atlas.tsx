import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  bandOf,
  bandRadius,
  BANDS,
  hitTest,
  layoutLabels,
  layoutRing,
  polar,
  ringGeometry,
  type AtlasSector,
  type Ring,
  type RingGeometry,
  type RingInsets,
  type Spike,
  BEYOND_SECTOR,
} from "../../utils/atlas";
import { DEFAULT_CAP, mapPath, type Grouping } from "../../utils/mapRoute";
import {
  clear,
  drawHot,
  drawRing,
  homeCamera,
  readPalette,
  resolveColor,
  SPIKE_DIM,
  SPIKE_LIT,
  SPIKE_NORMAL,
  type Camera,
  type HotFrame,
  type Palette,
  type RingFrame,
  type SpikeFrame,
} from "./atlasCanvas";
import { AtlasList } from "./AtlasList";

export interface AtlasPageInfo {
  title: string;
  summary: string;
}

interface Props {
  sectors: AtlasSector[];
  grouping: Grouping;
  info: Map<string, AtlasPageInfo>;
  degree: Map<string, number>;
  totalLinks: number;
  termCount: number;
  /** Pages the filter selects (others dim); null without a filter. */
  matches: Set<string> | null;
  /** Pages lit by search or chat; null when nothing is. */
  lit: Set<string> | null;
  onOpenSector: (sector: string) => void;
  onOpenPage: (sector: string, page: string) => void;
  /** Where the map is coming back from: the camera eases out of it. */
  enterFrom: { sector: string; page?: string } | null;
}

const MORPH_MS = 720;
const MORPH_STAGGER = 0.3;
const CAMERA_MS = 430;
const ZOOMED_ALPHA = 0.3;
const SECTOR_ZOOM = 2.3;
const PAGE_ZOOM = 4.5;
const TOOLTIP_W = 300;
const BAND_LABEL_MIN = 14;
const WIDE_QUERY = "(min-width: 760px)";

const reducedMotion = () =>
  typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const isWide = () => typeof window.matchMedia !== "function" || window.matchMedia(WIDE_QUERY).matches;
const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

function insetsFor(wide: boolean, grouping: Grouping): RingInsets {
  return wide
    ? { left: 260, top: 76, bottom: 10, labelWidth: grouping === "course" ? 138 : 104 }
    : { left: 0, top: 96, bottom: 150, labelWidth: 84 };
}

/** Shortest way round from one angle to another. */
function towards(from: number, to: number, t: number): number {
  let d = (to - from) % (Math.PI * 2);
  if (d > Math.PI) d -= Math.PI * 2;
  if (d < -Math.PI) d += Math.PI * 2;
  return from + d * t;
}

function spikeFrame(ring: Ring, g: RingGeometry, degree: Map<string, number>): SpikeFrame {
  const n = ring.spikes.length;
  const frame: SpikeFrame = {
    angle: new Float64Array(n),
    tip: new Float64Array(n),
    color: new Array<string>(n),
    state: new Uint8Array(n),
  };
  const colors = ring.sectors.map((s) => resolveColor(s.color));
  ring.spikes.forEach((s, i) => {
    frame.angle[i] = s.angle;
    frame.tip[i] = bandRadius(g, bandOf(degree.get(s.id) ?? 0));
    frame.color[i] = colors[s.sector];
  });
  return frame;
}

interface Cursor {
  sector: number;
  /** A spike's ring index, or null when the whole sector is selected. */
  spike: number | null;
}

export function Atlas({
  sectors,
  grouping,
  info,
  degree,
  totalLinks,
  termCount,
  matches,
  lit,
  onOpenSector,
  onOpenPage,
  enterFrom,
}: Props) {
  const stageRef = useRef<HTMLDivElement>(null);
  const baseRef = useRef<HTMLCanvasElement>(null);
  const hotRef = useRef<HTMLCanvasElement>(null);
  const tipRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0, wide: true });
  const [moving, setMoving] = useState(false);
  const [zooming, setZooming] = useState(enterFrom != null && !reducedMotion());
  const [cursor, setCursor] = useState<Cursor | null>(null);
  const [hoverSector, setHoverSector] = useState<number | null>(null);

  const ring = useMemo(() => layoutRing(sectors), [sectors]);
  const insets = useMemo(() => insetsFor(size.wide, grouping), [size.wide, grouping]);
  const g = useMemo(() => ringGeometry(size.w, size.h, insets), [size, insets]);
  const labels = useMemo(() => layoutLabels(ring, g), [ring, g]);
  const matchedTotal = useMemo(() => {
    const on = lit ?? matches;
    return on ? ring.spikes.filter((s) => on.has(s.id)).length : null;
  }, [lit, matches, ring]);
  const cursorSpike = cursor?.spike != null ? (ring.spikes[cursor.spike] ?? null) : null;

  // What the imperative drawing reads. Written in a layout effect, read from handlers and rAF.
  const draw = useRef({
    ring,
    g,
    spikes: null as SpikeFrame | null,
    palette: null as Palette | null,
    cam: null as Camera | null,
    alpha: 1,
    structure: true,
    hover: null as Spike | null,
    hoverSector: null as number | null,
    cursor: null as Spike | null,
    cursorSector: null as number | null,
    dpr: 1,
    dimSectors: null as Set<number> | null,
    anyActive: false,
    raf: 0,
    pendingMove: null as { x: number; y: number } | null,
    moveRaf: 0,
    rectLeft: 0,
    rectTop: 0,
  });

  const paintBase = useCallback((freshPalette: boolean) => {
    const d = draw.current;
    const ctx = baseRef.current?.getContext("2d");
    if (!ctx || !d.spikes) return;
    if (freshPalette || !d.palette) d.palette = readPalette();
    const started = performance.now();
    const frame: RingFrame = {
      g: d.g,
      ring: d.ring,
      spikes: d.spikes,
      palette: d.palette,
      cam: d.cam ?? homeCamera(d.g),
      dpr: d.dpr,
      showStructure: d.structure,
      dimSectors: d.dimSectors,
      alpha: d.alpha,
      anyActive: d.anyActive,
    };
    drawRing(ctx, frame);
    (window as unknown as { __atlasDrawTimes?: number[] }).__atlasDrawTimes?.push(performance.now() - started);
  }, []);

  const paintHot = useCallback(() => {
    const d = draw.current;
    const ctx = hotRef.current?.getContext("2d");
    if (!ctx || !d.spikes) return;
    if (!d.palette) d.palette = readPalette();
    if (d.cam || d.raf) {
      clear(ctx, d.g, d.dpr);
      return;
    }
    const frame: HotFrame = {
      g: d.g,
      ring: d.ring,
      spikes: d.spikes,
      palette: d.palette,
      dpr: d.dpr,
      hover: d.hover,
      cursor: d.cursor,
      sector: d.hoverSector ?? d.cursorSector ?? d.hover?.sector ?? null,
    };
    drawHot(ctx, frame);
  }, []);

  // --- Size ---------------------------------------------------------------------------
  useLayoutEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;
    const measure = () => {
      const r = stage.getBoundingClientRect();
      draw.current.rectLeft = r.left;
      draw.current.rectTop = r.top;
      const next = { w: Math.round(r.width) || 900, h: Math.round(r.height) || 640, wide: isWide() };
      setSize((prev) => (prev.w === next.w && prev.h === next.h && prev.wide === next.wide ? prev : next));
    };
    measure();
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(measure);
    ro.observe(stage);
    return () => ro.disconnect();
  }, []);

  useLayoutEffect(() => {
    const dpr = window.devicePixelRatio || 1;
    draw.current.dpr = dpr;
    for (const canvas of [baseRef.current, hotRef.current]) {
      if (!canvas) continue;
      canvas.width = Math.round(size.w * dpr);
      canvas.height = Math.round(size.h * dpr);
    }
  }, [size]);

  // --- Spikes: new ring (with a morph when the grouping changed), filter, search ---------
  const lastRing = useRef<{ grouping: Grouping; spikes: SpikeFrame; ids: string[] } | null>(null);
  const morph = useRef<{ target: SpikeFrame; frame: SpikeFrame } | null>(null);
  const stopAnim = useCallback(() => {
    cancelAnimationFrame(draw.current.raf);
    draw.current.raf = 0;
  }, []);

  useLayoutEffect(() => {
    const d = draw.current;
    d.ring = ring;
    d.g = g;
    const target = spikeFrame(ring, g, degree);
    const before = lastRing.current;
    lastRing.current = { grouping, spikes: target, ids: ring.spikes.map((s) => s.id) };

    const states = target.state;
    let active = false;
    const hasSector = new Set<number>();
    ring.spikes.forEach((s, i) => {
      const inLit = lit?.has(s.id);
      const inMatch = !matches || matches.has(s.id);
      const on = lit ? !!inLit : inMatch;
      states[i] = !on ? SPIKE_DIM : inLit ? SPIKE_LIT : SPIKE_NORMAL;
      if (on) hasSector.add(s.sector);
      if (!on) active = true;
    });
    d.anyActive = active;
    d.dimSectors = active ? new Set(ring.arcs.map((a) => a.sector).filter((x) => !hasSector.has(x))) : null;

    if (!before || before.grouping === grouping || reducedMotion()) {
      if (d.raf && moving) {
        const m = morph.current;
        const sameRing =
          before?.grouping === grouping &&
          before.ids.length === ring.spikes.length &&
          ring.spikes.every((s, i) => s.id === before.ids[i]);
        if (m && sameRing) {
          // A filter or search during the morph: it lands on the new states.
          m.target = target;
          m.frame.tip = target.tip;
          m.frame.state = states;
          return;
        }
        stopAnim(); // the ring changed under the morph, so its frames no longer line up
      }
      d.structure = true;
      d.spikes = target;
      setMoving(false);
      paintBase(true);
      paintHot();
      return;
    }

    // Morph: each spike travels from where it was to its new place, a little staggered round the
    // ring, and changes colour halfway so each frame still batches by colour.
    const fromIndex = new Map(before.ids.map((id, i) => [id, i]));
    const n = ring.spikes.length;
    const fromAngle = new Float64Array(n);
    const fromColor = new Array<string>(n);
    ring.spikes.forEach((s, i) => {
      const j = fromIndex.get(s.id);
      fromAngle[i] = j == null ? s.angle : before.spikes.angle[j];
      fromColor[i] = j == null ? target.color[i] : before.spikes.color[j];
    });
    const frame: SpikeFrame = {
      angle: fromAngle.slice(),
      tip: target.tip,
      color: fromColor.slice(),
      state: states,
    };
    const m = { target, frame };
    morph.current = m;
    d.spikes = frame;
    d.structure = false;
    d.hover = null;
    setMoving(true);
    stopAnim();
    const startedAt = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - startedAt) / MORPH_MS);
      for (let i = 0; i < n; i++) {
        const delay = (i / n) * MORPH_STAGGER;
        const local = Math.max(0, Math.min(1, (t - delay) / (1 - MORPH_STAGGER)));
        frame.angle[i] = towards(fromAngle[i], m.target.angle[i], easeInOut(local));
        frame.color[i] = local < 0.5 ? fromColor[i] : m.target.color[i];
      }
      paintBase(false);
      if (t < 1) {
        d.raf = requestAnimationFrame(tick);
      } else {
        d.raf = 0;
        d.spikes = m.target;
        d.structure = true;
        paintBase(true);
        paintHot();
        setMoving(false);
      }
    };
    d.raf = requestAnimationFrame(tick);
    // `moving` only guards re-entry above; it must not restart this effect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ring, g, degree, grouping, matches, lit, paintBase, paintHot, stopAnim]);

  // A theme switch: repaint with the new colours. Sector colours are resolved in spikeFrame, so a
  // sector on a CSS variable picks its colour up on the next ring; arcs resolve on every paint.
  useEffect(() => {
    const repaint = () => {
      const d = draw.current;
      if (d.spikes && !d.raf) d.spikes = spikeFrameWithStates(d.spikes, d.ring);
      paintBase(true);
      paintHot();
    };
    const observer = typeof MutationObserver === "undefined" ? null : new MutationObserver(repaint);
    observer?.observe(document.documentElement, { attributes: true, attributeFilter: ["class", "style", "data-theme"] });
    const scheme = typeof window.matchMedia === "function" ? window.matchMedia("(prefers-color-scheme: light)") : null;
    scheme?.addEventListener?.("change", repaint);
    return () => {
      observer?.disconnect();
      scheme?.removeEventListener?.("change", repaint);
    };
  }, [paintBase, paintHot]);

  useEffect(
    () => () => {
      cancelAnimationFrame(draw.current.raf);
      cancelAnimationFrame(draw.current.moveRaf);
    },
    [],
  );

  // --- Keyboard / pointer state into the hot layer ---------------------------------------
  useLayoutEffect(() => {
    const d = draw.current;
    d.cursor = cursorSpike;
    d.cursorSector = cursor?.sector ?? null;
    d.hoverSector = hoverSector;
    paintHot();
  }, [cursorSpike, cursor, hoverSector, paintHot]);

  // --- Camera: into a sector or spike, then the route changes; back out on return ---------
  const cameraTarget = useCallback((sector: number, spike: Spike | null): Camera => {
    const d = draw.current;
    if (spike) {
      const tip = polar(d.g, spike.angle, d.g.outer);
      return { x: tip.x, y: tip.y, k: PAGE_ZOOM };
    }
    const arc = d.ring.arcs[sector];
    const at = polar(d.g, arc.mid, (d.g.inner + d.g.outer) / 2);
    return { x: at.x, y: at.y, k: SECTOR_ZOOM };
  }, []);

  const runCamera = useCallback(
    (from: Camera, to: Camera, alphaFrom: number, alphaTo: number, done: () => void) => {
      const d = draw.current;
      stopAnim();
      d.structure = false;
      clear(hotRef.current?.getContext("2d") ?? (null as never), d.g, d.dpr);
      const startedAt = performance.now();
      const tick = (now: number) => {
        const t = Math.min(1, (now - startedAt) / CAMERA_MS);
        const e = easeInOut(t);
        d.cam = {
          x: from.x + (to.x - from.x) * e,
          y: from.y + (to.y - from.y) * e,
          k: from.k * (to.k / from.k) ** e,
        };
        d.alpha = alphaFrom + (alphaTo - alphaFrom) * e;
        paintBase(false);
        if (t < 1) {
          d.raf = requestAnimationFrame(tick);
        } else {
          d.raf = 0;
          done();
        }
      };
      d.raf = requestAnimationFrame(tick);
    },
    [paintBase, stopAnim],
  );

  const zoomInto = useCallback(
    (sector: number, spike: Spike | null) => {
      const s = ring.sectors[sector];
      if (!s) return;
      const open = () => (spike ? onOpenPage(s.id, spike.id) : onOpenSector(s.id));
      if (reducedMotion() || !hotRef.current?.getContext("2d")) {
        open();
        return;
      }
      setZooming(true);
      setHoverSector(null);
      hideTip(tipRef.current);
      runCamera(homeCamera(draw.current.g), cameraTarget(sector, spike), 1, ZOOMED_ALPHA, open);
    },
    [ring, onOpenPage, onOpenSector, runCamera, cameraTarget],
  );

  // On arrival from a focused view, once the ring has its real size.
  const entered = useRef(false);
  useEffect(() => {
    if (entered.current || !size.w || !draw.current.spikes) return;
    entered.current = true;
    if (!enterFrom || reducedMotion() || !hotRef.current?.getContext("2d")) {
      setZooming(false);
      return;
    }
    const sector = ring.sectors.findIndex((s) => s.id === enterFrom.sector);
    if (sector < 0) {
      setZooming(false);
      return;
    }
    const spike = enterFrom.page ? (ring.spikes.find((s) => s.id === enterFrom.page) ?? null) : null;
    const d = draw.current;
    runCamera(cameraTarget(sector, spike), homeCamera(d.g), ZOOMED_ALPHA, 1, () => {
      d.cam = null;
      d.alpha = 1;
      d.structure = true;
      paintBase(false);
      paintHot();
      setZooming(false);
    });
  }, [size, enterFrom, ring, runCamera, cameraTarget, paintBase, paintHot]);

  // --- Pointer -------------------------------------------------------------------------
  const applyHover = useCallback(() => {
    const d = draw.current;
    d.moveRaf = 0;
    const at = d.pendingMove;
    if (!at || d.raf || d.cam) return;
    const hit = hitTest(d.ring, d.g, at.x, at.y);
    const spike = hit?.kind === "spike" ? hit.spike : null;
    const sector = hit?.kind === "sector" ? hit.sector : null;
    const tip = tipRef.current;
    if (spike !== d.hover || sector !== d.hoverSector) {
      d.hover = spike;
      d.hoverSector = sector;
      paintHot();
      if (tip) {
        if (spike) fillTip(tip, info.get(spike.id), d.ring.sectors[spike.sector], degree.get(spike.id) ?? 0);
        else if (sector != null) fillSectorTip(tip, d.ring.sectors[sector]);
        else hideTip(tip);
      }
      if (hotRef.current) hotRef.current.style.cursor = spike || sector != null ? "pointer" : "default";
    }
    if (tip && (spike || sector != null)) moveTip(tip, at.x, at.y, d.g);
  }, [info, degree, paintHot]);

  const onPointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (e.pointerType === "touch") return;
      const d = draw.current;
      d.pendingMove = { x: e.clientX - d.rectLeft, y: e.clientY - d.rectTop };
      if (!d.moveRaf) d.moveRaf = requestAnimationFrame(applyHover);
    },
    [applyHover],
  );

  const onPointerLeave = useCallback(() => {
    const d = draw.current;
    d.pendingMove = null;
    d.hover = null;
    d.hoverSector = null;
    paintHot();
    hideTip(tipRef.current);
  }, [paintHot]);

  const pointerKind = useRef<string>("mouse");
  const onPointerDown = useCallback((e: React.PointerEvent) => {
    pointerKind.current = e.pointerType;
    const stage = stageRef.current?.getBoundingClientRect();
    if (stage) {
      draw.current.rectLeft = stage.left;
      draw.current.rectTop = stage.top;
    }
  }, []);

  const onClick = useCallback(
    (e: React.MouseEvent) => {
      const d = draw.current;
      if (d.raf || d.cam) return;
      const hit = hitTest(d.ring, d.g, e.clientX - d.rectLeft, e.clientY - d.rectTop);
      if (!hit) {
        setCursor(null);
        return;
      }
      const sector = hit.kind === "spike" ? hit.spike.sector : hit.sector;
      const spike = hit.kind === "spike" ? hit.spike : null;
      // A fingertip covers dozens of spikes, so a tap selects and the card opens it.
      if (pointerKind.current === "touch") {
        setCursor({ sector, spike: spike?.index ?? null });
        return;
      }
      zoomInto(sector, spike);
    },
    [zoomInto],
  );

  // --- Keyboard ------------------------------------------------------------------------
  const stepSpike = useCallback(
    (by: number) => {
      const count = ring.spikes.length;
      if (!count) return;
      setCursor((c) => {
        const at = c?.spike ?? (c ? ring.sectors.slice(0, c.sector).reduce((n, s) => n + s.pageIds.length, 0) - (by > 0 ? 1 : 0) : by > 0 ? -1 : 0);
        const next = (at + by + count) % count;
        return { sector: ring.spikes[next].sector, spike: next };
      });
    },
    [ring],
  );

  const stepSector = useCallback(
    (by: number) => {
      const count = ring.sectors.length;
      if (!count) return;
      setCursor((c) => ({ sector: c ? (c.sector + by + count) % count : by > 0 ? 0 : count - 1, spike: null }));
    },
    [ring],
  );

  const onKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const keys: Record<string, () => void> = {
        ArrowRight: () => stepSpike(1),
        ArrowLeft: () => stepSpike(-1),
        ArrowDown: () => stepSector(1),
        ArrowUp: () => stepSector(-1),
        PageDown: () => stepSector(1),
        PageUp: () => stepSector(-1),
        Home: () => setCursor(ring.spikes.length ? { sector: 0, spike: 0 } : null),
        End: () => {
          const last = ring.spikes[ring.spikes.length - 1];
          if (last) setCursor({ sector: last.sector, spike: last.index });
        },
        Enter: () => {
          if (cursor) zoomInto(cursor.sector, cursorSpike);
        },
      };
      if (e.key === "Escape" && cursor) {
        e.preventDefault();
        setCursor(null);
        return;
      }
      const action = keys[e.key];
      if (!action) return;
      e.preventDefault();
      action();
    },
    [stepSpike, stepSector, ring, cursor, cursorSpike, zoomInto],
  );

  // A ring from another grouping or wiki state: an index would point at another page.
  useEffect(() => setCursor(null), [ring]);

  // --- What's selected, in words --------------------------------------------------------
  const selSector = cursor ? ring.sectors[cursor.sector] : null;
  const selInfo = cursorSpike ? info.get(cursorSpike.id) : null;
  const announcement = !selSector
    ? ""
    : cursorSpike
      ? `${selInfo?.title ?? cursorSpike.id}, ${selSector.label}, ${degree.get(cursorSpike.id) ?? 0} links`
      : `${selSector.label}, ${selSector.pageIds.length} pages`;
  const pageTotal = ring.spikes.length;
  const titleOf = useCallback((id: string) => info.get(id)?.title ?? id, [info]);

  const cardSize = g.inner * 1.72;
  const cardStyle = g.cardInside
    ? { left: g.cx - cardSize / 2, top: g.cy - cardSize / 2, width: cardSize, height: cardSize }
    : undefined;

  return (
    <div ref={stageRef} className={`atlas${moving || zooming ? " is-moving" : ""}`}>
      <canvas ref={baseRef} className="atlas-canvas" aria-hidden="true" />
      <canvas
        ref={hotRef}
        className="atlas-canvas atlas-canvas--hot"
        tabIndex={0}
        role="application"
        aria-label={`Atlas of ${pageTotal} wiki pages in ${ring.sectors.length} sectors, one spike per page; a longer spike means more links. Left and right arrows step through pages, up and down through sectors, Enter opens. Everything here is also under "Browse as a list".`}
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
        onPointerDown={onPointerDown}
        onClick={onClick}
        onKeyDown={onKeyDown}
      />

      <svg className="atlas-svg" width={size.w} height={size.h} aria-hidden={false} role="group" aria-label="Sectors">
        <g className="atlas-bands" aria-hidden="true">
          {BANDS.map((b, i) => {
            const r = bandRadius(g, i);
            // A small ring has no room for all five: keep the two ends of the scale.
            const tight = bandRadius(g, 1) - bandRadius(g, 0) < BAND_LABEL_MIN;
            if (tight && i !== 0 && i !== BANDS.length - 1) return null;
            return (
              <text key={b.label} x={g.cx} y={g.cy - r + 4} textAnchor="middle" className="atlas-band">
                {b.label}
              </text>
            );
          })}
        </g>
        {labels.map((l) => {
          const s = ring.sectors[l.sector];
          const dir = l.anchor === "start" ? 1 : -1;
          return (
            <g key={s.id}>
              <path
                className="atlas-leader"
                d={`M${l.from.x},${l.from.y} L${l.x - dir * 4},${l.y - 4}`}
                style={{ stroke: s.color }}
              />
              <a
                href={`#${mapPath({ level: "sector", grouping, sector: s.id, cap: DEFAULT_CAP })}`}
                className="atlas-label"
                onClick={(e) => {
                  e.preventDefault();
                  zoomInto(l.sector, null);
                }}
                onPointerEnter={() => setHoverSector(l.sector)}
                onPointerLeave={() => setHoverSector(null)}
                onFocus={() => setHoverSector(l.sector)}
                onBlur={() => setHoverSector(null)}
              >
                <title>
                  {`${s.label}: ${s.pageIds.length} pages${grouping === "course" && s.id !== BEYOND_SECTOR ? " with this as their main course" : ""}`}
                </title>
                <text x={l.x} y={l.y} textAnchor={l.anchor}>
                  {l.text} <tspan className="atlas-label-count">{l.count}</tspan>
                </text>
              </a>
            </g>
          );
        })}
      </svg>

      <div className={`atlas-card${g.cardInside ? "" : " atlas-card--below"}`} style={cardStyle}>
        {selSector ? (
          <>
            <div className="atlas-card-sector">
              <span className="cur-dot" style={{ background: selSector.color }} aria-hidden="true" />
              {selSector.label}
            </div>
            {cursorSpike ? (
              <>
                <div className="atlas-card-title">{selInfo?.title ?? cursorSpike.id}</div>
                <div className="atlas-card-summary">{selInfo?.summary}</div>
                <div className="atlas-card-note">{degree.get(cursorSpike.id) ?? 0} links</div>
              </>
            ) : (
              <>
                <div className="atlas-card-title">{selSector.pageIds.length} pages</div>
                <div className="atlas-card-summary">
                  Best linked: {selSector.pageIds.slice(0, 3).map(titleOf).join(", ")}
                </div>
              </>
            )}
            <div className="atlas-card-actions">
              <button type="button" className="pill-btn" aria-label="Previous" onClick={() => (cursorSpike ? stepSpike(-1) : stepSector(-1))}>
                ‹
              </button>
              <button type="button" className="pill-btn" aria-label="Next" onClick={() => (cursorSpike ? stepSpike(1) : stepSector(1))}>
                ›
              </button>
              <button
                type="button"
                className="pill-btn pill-btn--accent"
                onClick={() => zoomInto(cursor!.sector, cursorSpike)}
              >
                Open
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="atlas-card-total">
              {matchedTotal != null ? `${matchedTotal} of ${pageTotal}` : pageTotal.toLocaleString("en-US")}
            </div>
            <div className="atlas-card-note">{matchedTotal != null ? "pages match" : "wiki pages"}</div>
            <div className="atlas-card-note">
              {totalLinks.toLocaleString("en-US")} links
              {termCount > 0 && ` · ${termCount} glossary terms`}
            </div>
            <div className="atlas-card-legend">Spike length: links to and from a page</div>
          </>
        )}
      </div>

      <div ref={tipRef} className="atlas-tip" style={{ width: TOOLTIP_W }} hidden aria-hidden="true" />
      <div className="sr-only" aria-live="polite">
        {announcement}
      </div>
      <AtlasList sectors={ring.sectors} grouping={grouping} titleOf={titleOf} matches={lit ?? matches} />
    </div>
  );
}

/** Same spikes with colours resolved again: a sector on a CSS variable follows the theme. */
function spikeFrameWithStates(frame: SpikeFrame, ring: Ring): SpikeFrame {
  const colors = ring.sectors.map((s) => resolveColor(s.color));
  ring.spikes.forEach((s, i) => {
    frame.color[i] = colors[s.sector];
  });
  return frame;
}

function hideTip(tip: HTMLElement | null): void {
  if (tip) tip.hidden = true;
}

function tipLine(cls: string, text: string): HTMLDivElement {
  const div = document.createElement("div");
  div.className = cls;
  div.textContent = text;
  return div;
}

function fillTip(tip: HTMLElement, page: AtlasPageInfo | undefined, sector: AtlasSector, links: number): void {
  tip.replaceChildren(
    tipLine("atlas-tip-title", page?.title ?? ""),
    tipLine("atlas-tip-summary", page?.summary ?? ""),
    tipLine("atlas-tip-meta", `${sector.label} · ${links} ${links === 1 ? "link" : "links"}`),
  );
  tip.hidden = false;
}

function fillSectorTip(tip: HTMLElement, sector: AtlasSector): void {
  tip.replaceChildren(
    tipLine("atlas-tip-title", sector.label),
    tipLine("atlas-tip-meta", `${sector.pageIds.length} pages · click to open the best linked`),
  );
  tip.hidden = false;
}

/** Beside the pointer, on the side with room. Uses a transform, so it doesn't trigger layout. */
function moveTip(tip: HTMLElement, x: number, y: number, g: RingGeometry): void {
  const left = x + 16 + TOOLTIP_W > g.width ? x - TOOLTIP_W - 16 : x + 16;
  const top = y > g.height - 150 ? y - 130 : y + 14;
  tip.style.transform = `translate(${Math.max(4, left)}px, ${Math.max(4, top)}px)`;
}
