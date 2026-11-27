import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import "../filter.css";
import {
  bandRadius,
  BANDS,
  hitTest,
  layoutLabels,
  layoutRing,
  polar,
  ringGeometry,
  type AtlasSector,
  type Spike,
} from "../../utils/atlas";
import { fieldHit, layoutField, type FieldLink } from "../../utils/atlasField";
import type { Grouping } from "../../utils/mapRoute";
import type { RelatedPages } from "../NodeDetailPanel";
import { AtlasPageDetail } from "./AtlasPageDetail";
import {
  clear,
  drawHot,
  drawRing,
  homeCamera,
  readPalette,
  SPIKE_DIM,
  SPIKE_FAINT,
  SPIKE_LIT,
  SPIKE_NORMAL,
  type Camera,
  type HotFrame,
  type Palette,
  type RingFrame,
  type SpikeFrame,
} from "./atlasCanvas";
import { insetsFor, spikeFrame, spikeFrameWithStates, towards } from "./atlasFrames";
import { gapText, sectorSummary, type AtlasPageInfo } from "./atlasText";
import { fillSectorTip, fillTip, hideTip, moveTip, TOOLTIP_W } from "./atlasTip";

export type { AtlasPageInfo } from "./atlasText";

interface Props {
  sectors: AtlasSector[];
  grouping: Grouping;
  info: Map<string, AtlasPageInfo>;
  degree: Map<string, number>;
  totalLinks: number;
  /** Pages the filter selects (others dim); null without a filter. */
  matches: Set<string> | null;
  /** Pages lit by search or chat; null when nothing is. */
  lit: Set<string> | null;
  /** Pages some lesson links; the rest draw faint as course gaps. Null until the curriculum arrives. */
  taught: Set<string> | null;
  /** Where the map is coming back from: the camera eases out of it. */
  enterFrom: { sector: string; page?: string } | null;
  /**
   * The side column's Reading slot. Given one, the page or sector under the pointer (or the
   * keyboard cursor) is read there in full, and the hole keeps only a few large words.
   */
  reading?: HTMLElement | null;
  /** Wikilinks between pages: they place the inner field's dots and are drawn on selecting one. */
  links?: FieldLink[];
  /** A page's links grouped by kind of link; without it the card lists them in one group. */
  related?: (pageId: string) => RelatedPages[];
  /** A tag on the card toggles its filter; `activeTags` are the ones on. */
  onTagClick?: (tag: string) => void;
  activeTags?: Set<string>;
  /** A page's most similar pages by embedding, best first. Without it the card lists none. */
  similar?: (pageId: string) => SimilarPage[];
}

export interface SimilarPage {
  id: string;
  title: string;
  score: number;
}

const NO_LINKS: FieldLink[] = [];
/** How many of a page's neighbours the card and column list by name. */
const NEIGHBOUR_LIST = 12;
/** The link groups the card shows, and how many pages each lists before "+n more". */
const CARD_GROUPS = ["Builds on", "Leads to", "Examples", "Related", "Disagrees with", "Superseded by", "Replaces"];
const CARD_GROUP_CAP = 3;
/** How many similar pages the card lists and the map draws. */
const SIMILAR_CAP = 3;

const MORPH_MS = 720;
const MORPH_STAGGER = 0.3;
const CAMERA_MS = 430;
const ZOOMED_ALPHA = 0.3;
const SECTOR_ZOOM = 2.3;
const PAGE_ZOOM = 4.5;
const BAND_LABEL_MIN = 14;
const WIDE_QUERY = "(min-width: 760px)";
const MAX_VIEW_ZOOM = 5;
const DRAG_SLOP = 4;
/** Backing pixels per canvas when re-rendering for a zoom: past this a bigger bitmap costs more than it shows. */
const MAX_CANVAS_PX = 16e6;
const SHARPEN_MS = 150;

const reducedMotion = () =>
  typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const isWide = () => typeof window.matchMedia !== "function" || window.matchMedia(WIDE_QUERY).matches;
const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);

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
  matches,
  lit,
  taught,
  enterFrom,
  reading = null,
  links = NO_LINKS,
  related,
  onTagClick,
  activeTags,
  similar,
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
  // Which lines the selected page shows, on the map and in its card.
  const [lines, setLines] = useState({ wiki: true, similar: true });
  // The last thing pointed at. It stays when the pointer leaves, so it can still be read in the column.
  const [peek, setPeek] = useState<Cursor | null>(null);
  const peekRef = useRef<Cursor | null>(null);
  peekRef.current = peek;

  const ring = useMemo(() => layoutRing(sectors), [sectors]);
  const field = useMemo(() => layoutField(ring, degree, links), [ring, degree, links]);
  const titles = useMemo(() => ring.spikes.map((s) => info.get(s.id)?.title ?? s.id), [ring, info]);
  const insets = useMemo(() => insetsFor(size.wide, grouping), [size.wide, grouping]);
  const g = useMemo(() => ringGeometry(size.w, size.h, insets), [size, insets]);
  const labels = useMemo(() => layoutLabels(ring, g), [ring, g]);
  const matchedTotal = useMemo(() => {
    const on = lit ?? matches;
    return on ? ring.spikes.filter((s) => on.has(s.id)).length : null;
  }, [lit, matches, ring]);
  const cursorSpike = cursor?.spike != null ? (ring.spikes[cursor.spike] ?? null) : null;
  const spikeIndex = useMemo(() => new Map(ring.spikes.map((sp) => [sp.id, sp.index])), [ring]);
  /** A page's similar pages that are on the ring, best first, or none with the switch off. */
  const similarOf = useCallback(
    (id: string): SimilarPage[] =>
      lines.similar && similar ? similar(id).filter((p) => p.id !== id && spikeIndex.has(p.id)).slice(0, SIMILAR_CAP) : [],
    [lines.similar, similar, spikeIndex],
  );
  /** Per sector, how many of its pages no lesson links yet; null until the curriculum is in. */
  const gaps = useMemo(
    () => (taught ? new Map(ring.sectors.map((s) => [s.id, s.pageIds.filter((id) => !taught.has(id)).length])) : null),
    [ring, taught],
  );

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
    field: null as ReturnType<typeof layoutField> | null,
    titles: [] as string[],
    viewK: 1,
    wikiLines: true,
    similar: [] as number[],
  });

  // Free zoom and pan: a CSS transform on the layer holding the canvases, labels and card. The
  // ring is still drawn in its own coordinates, so hit tests map the pointer back through it.
  const worldRef = useRef<HTMLDivElement>(null);
  const view = useRef({ k: 1, x: 0, y: 0 });
  const [viewK, setViewK] = useState(1);
  const viewZoomed = viewK > 1;
  const dragRef = useRef<{ x: number; y: number; vx: number; vy: number; moved: boolean } | null>(null);
  const suppressClick = useRef(false);

  const applyView = useCallback(() => {
    const v = view.current;
    const { width, height } = draw.current.g;
    v.k = Math.min(MAX_VIEW_ZOOM, Math.max(1, v.k));
    v.x = Math.min(0, Math.max(width * (1 - v.k), v.x));
    v.y = Math.min(0, Math.max(height * (1 - v.k), v.y));
    if (worldRef.current) worldRef.current.style.transform = `translate(${v.x}px, ${v.y}px) scale(${v.k})`;
    setViewK(v.k);
  }, []);

  /** Zoom by `factor` about a point in stage coordinates (the centre by default). */
  const zoomView = useCallback(
    (factor: number, at?: { x: number; y: number }) => {
      const v = view.current;
      const { width, height } = draw.current.g;
      const px = at?.x ?? width / 2;
      const py = at?.y ?? height / 2;
      const k = Math.min(MAX_VIEW_ZOOM, Math.max(1, v.k * factor));
      v.x = px - ((px - v.x) * k) / v.k;
      v.y = py - ((py - v.y) * k) / v.k;
      v.k = k;
      applyView();
    },
    [applyView],
  );

  const resetView = useCallback(() => {
    view.current = { k: 1, x: 0, y: 0 };
    applyView();
  }, [applyView]);

  const toRing = (x: number, y: number) => {
    const v = view.current;
    return { x: (x - v.x) / v.k, y: (y - v.y) / v.k };
  };

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
      field: d.field,
      viewK: d.viewK,
      titles: d.titles,
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
      field: d.field,
      viewK: d.viewK,
      titles: d.titles,
      wikiLines: d.wikiLines,
      similar: d.similar,
    };
    drawHot(ctx, frame);
  }, []);

  // Once a zoom settles, redraw at the zoomed resolution so the scaled bitmap stays sharp, and
  // with the labels the zoom has made room for.
  useEffect(() => {
    const timer = setTimeout(() => {
      const d = draw.current;
      const base = window.devicePixelRatio || 1;
      const { width, height } = d.g;
      const dpr = Math.max(base, Math.min(base * viewK, Math.sqrt(MAX_CANVAS_PX / Math.max(1, width * height))));
      const sameDpr = Math.abs(dpr - d.dpr) < 0.01;
      if (sameDpr && d.viewK === viewK) return;
      d.viewK = viewK;
      if (!sameDpr) {
        d.dpr = dpr;
        for (const canvas of [baseRef.current, hotRef.current]) {
          if (!canvas) continue;
          canvas.width = Math.round(width * dpr);
          canvas.height = Math.round(height * dpr);
        }
      }
      paintBase(false);
      paintHot();
    }, SHARPEN_MS);
    return () => clearTimeout(timer);
  }, [viewK, paintBase, paintHot]);

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

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;
    const onWheel = (e: WheelEvent) => {
      const d = draw.current;
      if (d.raf || d.cam) return;
      e.preventDefault();
      const r = stage.getBoundingClientRect();
      zoomView(Math.exp(-e.deltaY * 0.0015), { x: e.clientX - r.left, y: e.clientY - r.top });
    };
    stage.addEventListener("wheel", onWheel, { passive: false });
    return () => stage.removeEventListener("wheel", onWheel);
  }, [zoomView]);

  // A new size is a new ring geometry: start from the whole ring again.
  useEffect(() => resetView(), [size, resetView]);

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
    d.field = field;
    d.titles = titles;
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
      states[i] = !on ? SPIKE_DIM : inLit ? SPIKE_LIT : taught && !taught.has(s.id) ? SPIKE_FAINT : SPIKE_NORMAL;
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
  }, [ring, g, degree, field, titles, grouping, matches, lit, taught, paintBase, paintHot, stopAnim]);

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
    d.wikiLines = lines.wiki;
    d.similar = cursorSpike ? similarOf(cursorSpike.id).map((p) => spikeIndex.get(p.id)!) : [];
    paintHot();
  }, [cursorSpike, cursor, hoverSector, lines.wiki, similarOf, spikeIndex, paintHot]);

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
  /** The rim first (spikes, arcs), then the field of dots inside it. */
  const hitAt = (x: number, y: number) => {
    const d = draw.current;
    const hit = hitTest(d.ring, d.g, x, y);
    if (hit || !d.field || !d.structure) return hit;
    if (Math.hypot(x - d.g.cx, y - d.g.cy) >= d.g.inner - 8) return null;
    const i = fieldHit(d.field, d.g, x, y, 4 / view.current.k);
    const spike = i == null ? null : d.ring.spikes[i];
    return spike ? { kind: "spike" as const, spike } : null;
  };

  const applyHover = useCallback(() => {
    const d = draw.current;
    d.moveRaf = 0;
    const at = d.pendingMove;
    if (!at || d.raf || d.cam) return;
    const p = toRing(at.x, at.y);
    const hit = hitAt(p.x, p.y);
    const spike = hit?.kind === "spike" ? hit.spike : null;
    const sector = hit?.kind === "sector" ? hit.sector : null;
    const tip = tipRef.current;
    if (spike !== d.hover || sector !== d.hoverSector) {
      d.hover = spike;
      d.hoverSector = sector;
      paintHot();
      if (spike) setPeek({ sector: spike.sector, spike: spike.index });
      else if (sector != null) setPeek({ sector, spike: null });
      if (tip) {
        if (spike) {
          const untaught = taught != null && !taught.has(spike.id);
          fillTip(tip, info.get(spike.id), d.ring.sectors[spike.sector], degree.get(spike.id) ?? 0, untaught);
        } else if (sector != null) {
          const s = d.ring.sectors[sector];
          fillSectorTip(tip, s, gaps?.get(s.id) ?? null);
        }
        else hideTip(tip);
      }
      if (hotRef.current) hotRef.current.style.cursor = spike || sector != null ? "pointer" : "default";
    }
    if (tip && (spike || sector != null)) moveTip(tip, at.x, at.y, d.g);
  }, [info, degree, taught, gaps, paintHot]);

  const onPointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (e.pointerType === "touch") return;
      const d = draw.current;
      const drag = dragRef.current;
      if (drag && e.buttons & 1) {
        const dx = e.clientX - drag.x;
        const dy = e.clientY - drag.y;
        if (!drag.moved && Math.hypot(dx, dy) < DRAG_SLOP) return;
        if (!drag.moved) {
          drag.moved = true;
          d.hover = null;
          d.hoverSector = null;
          paintHot();
          hideTip(tipRef.current);
        }
        view.current.x = drag.vx + dx;
        view.current.y = drag.vy + dy;
        applyView();
        return;
      }
      d.pendingMove = { x: e.clientX - d.rectLeft, y: e.clientY - d.rectTop };
      if (!d.moveRaf) d.moveRaf = requestAnimationFrame(applyHover);
    },
    [applyHover, applyView, paintHot],
  );

  const onPointerLeave = useCallback(() => {
    const d = draw.current;
    d.pendingMove = null;
    d.hover = null;
    d.hoverSector = null;
    paintHot();
    hideTip(tipRef.current);
  }, [paintHot]);

  const onPointerDown = useCallback((e: React.PointerEvent) => {
    const stage = stageRef.current?.getBoundingClientRect();
    if (stage) {
      draw.current.rectLeft = stage.left;
      draw.current.rectTop = stage.top;
    }
    // Dragging pans once zoomed; a press that doesn't move is still a click.
    dragRef.current =
      e.button === 0 && e.pointerType !== "touch" && view.current.k > 1
        ? { x: e.clientX, y: e.clientY, vx: view.current.x, vy: view.current.y, moved: false }
        : null;
  }, []);

  const onPointerUp = useCallback(() => {
    suppressClick.current = dragRef.current?.moved ?? false;
    dragRef.current = null;
  }, []);

  const onClick = useCallback(
    (e: React.MouseEvent) => {
      const d = draw.current;
      if (suppressClick.current) {
        suppressClick.current = false;
        return;
      }
      if (d.raf || d.cam) return;
      const p = toRing(e.clientX - d.rectLeft, e.clientY - d.rectTop);
      const hit = hitAt(p.x, p.y);
      if (!hit) {
        setCursor(null);
        return;
      }
      const sector = hit.kind === "spike" ? hit.spike.sector : hit.sector;
      const spike = hit.kind === "spike" ? hit.spike : null;
      // A click selects a page (lighting its links) or a sector; the card reads it. Nothing
      // here leaves the atlas: the card's links move the selection instead.
      setCursor({ sector, spike: spike ? spike.index : null });
    },
    [],
  );

  // --- Keyboard ------------------------------------------------------------------------
  const stepSpike = useCallback(
    (by: number) => {
      const count = ring.spikes.length;
      if (!count) return;
      setCursor((sel) => {
        const c = sel ?? peekRef.current;
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
      setCursor((sel) => {
        const c = sel ?? peekRef.current;
        return { sector: c ? (c.sector + by + count) % count : by > 0 ? 0 : count - 1, spike: null };
      });
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
    [stepSpike, stepSector, ring, cursor],
  );

  // A ring from another grouping or wiki state: an index would point at another page.
  useEffect(() => {
    setCursor(null);
    setPeek(null);
  }, [ring]);

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

  // With a Reading slot, the column shows the selection, or failing that the last thing pointed at.
  const readCursor = cursor ?? peek;
  const readSector = readCursor ? ring.sectors[readCursor.sector] : null;
  const readSpike = readCursor?.spike != null ? (ring.spikes[readCursor.spike] ?? null) : null;
  const readInfo = readSpike ? info.get(readSpike.id) : null;
  const spikeById = useMemo(() => new Map(ring.spikes.map((sp) => [sp.id, sp])), [ring]);
  const selectPage = useCallback(
    (id: string) => {
      const sp = spikeById.get(id);
      if (sp) setCursor({ sector: sp.sector, spike: sp.index });
    },
    [spikeById],
  );
  const colorOf = useCallback(
    (id: string) => {
      const sp = spikeById.get(id);
      return sp ? ring.sectors[sp.sector].color : "var(--text-ghost)";
    },
    [spikeById, ring],
  );

  /** A page's links, grouped by kind when the caller knows the kinds, else one best-linked group. */
  const groupsOf = (spike: Spike): RelatedPages[] => {
    if (!lines.wiki) return [];
    if (related) {
      return related(spike.id)
        .filter((g) => CARD_GROUPS.includes(g.label))
        .map((g) => {
          const pages = g.pages.filter((p) => spikeById.has(p.id));
          return { ...g, pages: pages.slice(0, CARD_GROUP_CAP), more: g.more + Math.max(0, pages.length - CARD_GROUP_CAP) };
        })
        .filter((g) => g.pages.length > 0);
    }
    const near = [...(field.neighbours[spike.index] ?? [])].sort(
      (a, b) => (degree.get(ring.spikes[b].id) ?? 0) - (degree.get(ring.spikes[a].id) ?? 0),
    );
    if (!near.length) return [];
    return [
      {
        label: "Linked pages",
        pages: near.slice(0, NEIGHBOUR_LIST).map((j) => ({ id: ring.spikes[j].id, title: titleOf(ring.spikes[j].id) })),
        more: Math.max(0, near.length - NEIGHBOUR_LIST),
      },
    ];
  };

  const pageDetail = (spike: Spike) => (
    <AtlasPageDetail
      key={spike.id}
      pageId={spike.id}
      related={groupsOf(spike)}
      similar={similarOf(spike.id)}
      page={info.get(spike.id)}
      tags={info.get(spike.id)?.tags ?? []}
      activeTags={activeTags}
      onSelect={selectPage}
      onTagClick={onTagClick}
      colorOf={colorOf}
    />
  );

  /** A sector's best-linked pages, as buttons that select them. */
  const bestLinked = (sector: AtlasSector, n: number) => (
    <>
      <div className="panel-label reading-sub">Best linked</div>
      <ul className="reading-list">
        {sector.pageIds.slice(0, n).map((id) => (
          <li key={id}>
            <button type="button" className="reading-link" onClick={() => selectPage(id)}>
              {titleOf(id)}
            </button>
          </li>
        ))}
      </ul>
    </>
  );

  const actions = (sel: Cursor, spike: Spike | null) => (
    <div className="atlas-card-actions">
      <button type="button" className="pill-btn" aria-label="Previous" onClick={() => (spike ? stepSpike(-1) : stepSector(-1))}>
        ‹
      </button>
      <button type="button" className="pill-btn" aria-label="Next" onClick={() => (spike ? stepSpike(1) : stepSector(1))}>
        ›
      </button>
      {spike && (
        <button type="button" className="pill-btn" onClick={() => setCursor({ sector: sel.sector, spike: null })}>
          {ring.sectors[sel.sector]?.label ?? "Sector"}
        </button>
      )}
      {cursor && (
        <button type="button" className="pill-btn" onClick={() => setCursor(null)}>
          Clear
        </button>
      )}
    </div>
  );

  const legend = (
    <>
      <div className="atlas-card-legend">Dot size and spike length: links to and from a page</div>
      {taught && <div className="atlas-card-legend">Faint: no lesson links the page yet</div>}
    </>
  );

  const totals = (
    <>
      <div className="atlas-card-total">
        {matchedTotal != null ? `${matchedTotal} of ${pageTotal}` : pageTotal.toLocaleString("en-US")}
      </div>
      <div className="atlas-card-note">{matchedTotal != null ? "pages match" : "wiki pages"}</div>
      <div className="atlas-card-note">{totalLinks.toLocaleString("en-US")} links</div>
    </>
  );

  // The same selection in full, for the Reading slot.
  const readingBody = (
    <div className="reading-atlas">
      {readSector && readCursor ? (
        <>
          <div className="reading-kicker">
            <span className="cur-dot" style={{ background: readSector.color }} aria-hidden="true" />
            {readSector.label}
          </div>
          {readSpike ? (
            <>
              <h2 className="reading-title">{readInfo?.title ?? readSpike.id}</h2>
              {readInfo?.summary && <p className="reading-summary">{readInfo.summary}</p>}
              <div className="reading-meta">
                {degree.get(readSpike.id) ?? 0} links
                {taught && !taught.has(readSpike.id) && " · not yet in a lesson"}
              </div>
              {pageDetail(readSpike)}
            </>
          ) : (
            <>
              <h2 className="reading-title">{readSector.pageIds.length} pages</h2>
              {gaps?.get(readSector.id) ? <div className="reading-meta">{gapText(gaps.get(readSector.id)!)}</div> : null}
              {bestLinked(readSector, 8)}
            </>
          )}
          {actions(readCursor, readSpike)}
        </>
      ) : (
        <>
          <p className="reading-empty">
            Point at a page or a sector to read about it here. Click one to keep it here, then follow its links from page to page.
          </p>
          {legend}
        </>
      )}
    </div>
  );

  return (
    <div ref={stageRef} className={`atlas${moving || zooming ? " is-moving" : ""}${viewZoomed ? " is-zoomed" : ""}`}>
      <div ref={worldRef} className="atlas-world">
      <canvas ref={baseRef} className="atlas-canvas" aria-hidden="true" />
      <canvas
        ref={hotRef}
        className="atlas-canvas atlas-canvas--hot"
        tabIndex={0}
        // A canvas has no native semantics; "application" hands arrow keys to the page (labelled below).
        // eslint-disable-next-line jsx-a11y/no-interactive-element-to-noninteractive-role
        role="application"
        aria-label={`Atlas of ${pageTotal} wiki pages in ${ring.sectors.length} sectors, one dot and one spike per page; a bigger dot or longer spike means more links. Left and right arrows step through pages, up and down through sectors, Escape clears. Everything here is also under "Browse as a list".`}
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
        onPointerDown={onPointerDown}
        onPointerUp={onPointerUp}
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
              <g
                role="button"
                tabIndex={0}
                className="atlas-label"
                onClick={() => setCursor({ sector: l.sector, spike: null })}
                onKeyDown={(e) => {
                  if (e.key !== "Enter" && e.key !== " ") return;
                  e.preventDefault();
                  setCursor({ sector: l.sector, spike: null });
                }}
                onPointerEnter={() => setHoverSector(l.sector)}
                onPointerLeave={() => setHoverSector(null)}
                onFocus={() => setHoverSector(l.sector)}
                onBlur={() => setHoverSector(null)}
              >
                <title>{sectorSummary(s, gaps?.get(s.id) ?? null)}</title>
                <text x={l.x} y={l.y} textAnchor={l.anchor}>
                  {l.text} <tspan className="atlas-label-count">{l.count}</tspan>
                </text>
              </g>
            </g>
          );
        })}
      </svg>

      </div>
      {reading && createPortal(readingBody, reading)}

      {/* The corner beside the ring: the totals, and without a Reading slot the selection's card. */}
      <div className="atlas-corner">
      {!reading && selSector && cursor && (
        <div className="atlas-card atlas-card--dock">
          <div className="atlas-card-sector">
            <span className="cur-dot" style={{ background: selSector.color }} aria-hidden="true" />
            {selSector.label}
          </div>
          {cursorSpike ? (
            <>
              <div className="atlas-card-title">{selInfo?.title ?? cursorSpike.id}</div>
              {selInfo?.summary && <div className="atlas-card-summary">{selInfo.summary}</div>}
              <div className="atlas-card-note">
                {degree.get(cursorSpike.id) ?? 0} links
                {taught && !taught.has(cursorSpike.id) && " · not yet in a lesson"}
              </div>
              <div className="atlas-card-links">{pageDetail(cursorSpike)}</div>
            </>
          ) : (
            <>
              <div className="atlas-card-title">{selSector.pageIds.length} pages</div>
              {gaps?.get(selSector.id) ? <div className="atlas-card-note">{gapText(gaps.get(selSector.id)!)}</div> : null}
              <div className="atlas-card-links">{bestLinked(selSector, 6)}</div>
            </>
          )}
          {actions(cursor, cursorSpike)}
        </div>
      )}
      <div className="atlas-totals">
        {totals}
        {!reading && !cursor && legend}
      </div>
      </div>

      <div className="atlas-lines" role="group" aria-label="Lines to show from the selected page">
        <button
          type="button"
          className="pill-btn"
          aria-pressed={lines.wiki}
          title="Wikilinks: pages this one links or is linked from"
          onClick={() => setLines((l) => ({ ...l, wiki: !l.wiki }))}
        >
          — wiki links
        </button>
        {similar && (
          <button
            type="button"
            className="pill-btn"
            aria-pressed={lines.similar}
            title="Pages whose text is closest to this one's, linked or not"
            onClick={() => setLines((l) => ({ ...l, similar: !l.similar }))}
          >
            ┄ similar
          </button>
        )}
      </div>

      <div className="atlas-zoom" role="group" aria-label="Zoom the atlas">
        <button type="button" className="pill-btn" aria-label="Zoom in" onClick={() => zoomView(1.5)}>
          +
        </button>
        <button type="button" className="pill-btn" aria-label="Zoom out" disabled={!viewZoomed} onClick={() => zoomView(1 / 1.5)}>
          −
        </button>
        <button type="button" className="pill-btn" disabled={!viewZoomed} onClick={resetView}>
          Reset
        </button>
      </div>

      <div ref={tipRef} className="atlas-tip" style={{ width: TOOLTIP_W }} hidden aria-hidden="true" />
      <div className="sr-only" aria-live="polite">
        {announcement}
      </div>
    </div>
  );
}
