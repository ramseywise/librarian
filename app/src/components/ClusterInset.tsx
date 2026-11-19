import { useMemo } from "react";
import "./clusterInset.css";
import { layoutRing, polar, type AtlasSector } from "../utils/atlas";

interface Props {
  sectors: AtlasSector[];
  /** Pages on the canvas. */
  pageIds: string[];
  /** The page the level is about, marked on the ring. */
  anchorId: string | null;
  onOpenSector: (sector: string) => void;
  onOpenAtlas: () => void;
  /** Pages drawn as points behind the cards: within two links, and three or four away. */
  around?: { near: number; far: number; beyond?: number };
}

/** The drawing's own units; CSS sets how large it is shown. */
const SIZE = 132;
const CENTRE = { cx: SIZE / 2, cy: SIZE / 2 };
const ARC_R = 58;
const TICK_OUT = 51;
const TICK_IN = 30;
/** Sectors the list names; the ring shows the rest. */
const LISTED = 5;

function arcPath(start: number, end: number): string {
  const a = polar(CENTRE, start, ARC_R);
  const b = polar(CENTRE, end, ARC_R);
  return `M${a.x.toFixed(1)} ${a.y.toFixed(1)}A${ARC_R} ${ARC_R} 0 ${end - start > Math.PI ? 1 : 0} 1 ${b.x.toFixed(1)} ${b.y.toFixed(1)}`;
}

/**
 * The atlas in small, beside a focused level: the ring's sectors with the ones this view reaches
 * lit, a tick for each page on the canvas, and those sectors listed by how many of its pages they
 * hold. It answers "where in the wiki am I, and what does this page touch".
 */
export function ClusterInset({ sectors, pageIds, anchorId, onOpenSector, onOpenAtlas, around }: Props) {
  const ring = useMemo(() => layoutRing(sectors), [sectors]);
  const spikeOf = useMemo(() => new Map(ring.spikes.map((s) => [s.id, s])), [ring]);
  const shown = useMemo(() => pageIds.flatMap((id) => spikeOf.get(id) ?? []), [pageIds, spikeOf]);
  const counts = useMemo(() => {
    const out = new Map<number, number>();
    for (const s of shown) out.set(s.sector, (out.get(s.sector) ?? 0) + 1);
    return out;
  }, [shown]);
  if (shown.length === 0) return null;

  const touched = [...counts].sort(([a, x], [b, y]) => y - x || a - b);
  const anchor = anchorId ? spikeOf.get(anchorId) : undefined;
  const dot = anchor && polar(CENTRE, anchor.angle, TICK_OUT);

  return (
    <section className="cluster-inset" aria-label="Clusters in view">
      <button type="button" className="cluster-inset-ring" onClick={onOpenAtlas} title="Back to the atlas">
        <svg viewBox={`0 0 ${SIZE} ${SIZE}`} aria-hidden="true">
          {ring.arcs.map((arc) => (
            <path
              key={arc.sector}
              d={arcPath(arc.start, arc.end)}
              className={counts.has(arc.sector) ? "cluster-inset-arc cluster-inset-arc--lit" : "cluster-inset-arc"}
              style={{ stroke: ring.sectors[arc.sector].color }}
            />
          ))}
          {shown.map((s) => {
            const from = polar(CENTRE, s.angle, TICK_IN);
            const to = polar(CENTRE, s.angle, TICK_OUT);
            return (
              <line
                key={s.id}
                x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                className="cluster-inset-tick"
                style={{ stroke: ring.sectors[s.sector].color }}
              />
            );
          })}
          {dot && <circle cx={dot.x} cy={dot.y} r={3.5} className="cluster-inset-anchor" />}
        </svg>
      </button>
      <div className="cluster-inset-list">
        <div className="panel-label">Clusters in view</div>
        {touched.slice(0, LISTED).map(([sector, n]) => {
          const s = ring.sectors[sector];
          return (
            <button key={s.id} type="button" className="cluster-inset-row" onClick={() => onOpenSector(s.id)} title={`Open ${s.label}`}>
              <span className="cluster-inset-swatch" style={{ background: s.color }} />
              <span className="cluster-inset-label">{s.label}</span>
              <span className="cluster-inset-count">{n}</span>
            </button>
          );
        })}
        {touched.length > LISTED && <div className="detail-more">+{touched.length - LISTED} more</div>}
        {around && around.near + around.far > 0 && (
          <div className="cluster-inset-around">
            <span className="cluster-inset-point cluster-inset-point--near" /> {around.near} within 2 links
            <span className="cluster-inset-point" /> {around.far} within 4
          </div>
        )}
        {!!around?.beyond && (
          <div className="cluster-inset-around">
            <span className="cluster-inset-point" /> {around.beyond} further out
          </div>
        )}
      </div>
    </section>
  );
}
