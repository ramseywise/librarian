import { memo, useMemo, useState } from "react";
import "./graph.css";
import { ViewportPortal } from "@xyflow/react";
import { FIELD_HOPS, LABEL_SIZE, NEAR_HOPS, type Field, type FieldDot } from "../utils/hopField";

interface Props {
  field: Field;
  titleOf: (id: string) => string;
  onOpenPage: (id: string) => void;
  /** The sector the view has moved in on, if any: its points are drawn larger. */
  focus: string | null;
  /** A sector's arc or label was picked. */
  onPickSector: (sector: string) => void;
}

/** How a point is drawn: its page has a card, or is this near, or no link reaches it. */
const kindOf = (d: FieldDot) =>
  d.card ? "card" : d.hop === undefined || d.hop > FIELD_HOPS ? "rest" : d.hop <= NEAR_HOPS ? "near" : `h${d.hop}`;
const away = (d: FieldDot) =>
  d.card ? "on the map" : d.hop === undefined ? "no link from here" : `${d.hop} links away`;

/**
 * The wiki behind a page's level (see `layoutField`): every page a point in a circle round the
 * cards, sector by sector, bigger and brighter the nearer its page is to the open one. Drawn in
 * the viewport, so it pans and zooms with the cards; CSS puts the portal under them. A point opens
 * its page's level; a sector's arc or label moves the view in on that part of the circle, where
 * its points are drawn larger. Under the pointer a point's links back to the cards are drawn.
 *
 * Points are placed by a CSS transform and kept in a fixed order, so from one page's level to the
 * next each is the same element: the circle stays and its points grow and light for the new page.
 */
export const HopField = memo(function HopField({ field, titleOf, onOpenPage, focus, onPickSector }: Props) {
  const [hover, setHover] = useState<string | null>(null);
  const byId = useMemo(() => new Map(field.dots.map((d) => [d.id, d])), [field.dots]);

  const marks = useMemo(() => {
    const color = (sector: number) => field.sectors[sector].color;
    const focused = (sector: number) => field.sectors[sector].id === focus;
    return (
      <>
        {field.arcs.map((a) => (
          <path
            key={field.sectors[a.sector].id}
            d={a.d}
            data-sector={field.sectors[a.sector].id}
            className={`hop-arc${a.lit ? " hop-arc--lit" : ""}${focused(a.sector) ? " hop-arc--focus" : ""}`}
            style={{ stroke: color(a.sector) }}
          >
            <title>{field.sectors[a.sector].label}</title>
          </path>
        ))}
        {field.dots.map((d) => {
          // A card to its own point, and a page in reach to the page it is reached through.
          const tied = (d.card || (d.hop !== undefined && d.hop <= FIELD_HOPS)) && d.from;
          return tied && (
            <line
              key={d.id}
              x1={d.from!.x} y1={d.from!.y} x2={d.x} y2={d.y}
              className={d.card ? "hop-line hop-line--card" : d.hop! <= NEAR_HOPS ? "hop-line" : `hop-line hop-line--h${d.hop}`}
              style={{ stroke: color(d.sector) }}
            />
          );
        })}
        {field.dots.map((d) => (
          <circle
            key={d.id}
            data-id={d.id}
            r={5}
            className={`hop-dot hop-dot--${kindOf(d)}${focused(d.sector) ? " hop-dot--focus" : ""}`}
            style={{ fill: color(d.sector), transform: `translate(${d.x}px, ${d.y}px)` }}
          >
            <title>{`${titleOf(d.id)} · ${away(d)} · ${field.sectors[d.sector].label}`}</title>
          </circle>
        ))}
        {field.labels.map((l) => (
          <text
            key={l.sector}
            data-sector={field.sectors[l.sector].id}
            className="hop-label"
            fontSize={LABEL_SIZE}
            textAnchor={l.anchor}
            x={l.x}
            y={l.y}
            style={{ fill: color(l.sector) }}
          >
            {l.text}
            <title>{focused(l.sector) ? "Back to the whole circle" : `Zoom in on ${field.sectors[l.sector].label}`}</title>
          </text>
        ))}
      </>
    );
  }, [field, titleOf, focus]);

  // From the point under the pointer back, link by link, to the card its chain starts at.
  const chain = useMemo(() => {
    const start = hover ? byId.get(hover) : undefined;
    if (!start) return null;
    const points: string[] = [];
    const seen = new Set<string>();
    let at: FieldDot | undefined = start;
    while (at && !seen.has(at.id)) {
      seen.add(at.id);
      points.push(`${at.x},${at.y}`);
      const next: FieldDot | undefined = at.card ? undefined : byId.get(at.via);
      if ((!next || next.card) && at.from) points.push(`${at.from.x},${at.from.y}`);
      at = next?.card ? undefined : next;
    }
    return points.length > 1 ? { points: points.join(" "), color: field.sectors[start.sector].color } : null;
  }, [hover, byId, field.sectors]);

  const attr = (target: EventTarget, name: string) => (target as Element).getAttribute?.(name) ?? null;
  return (
    <ViewportPortal>
      <svg
        className="hop-field"
        width={1}
        height={1}
        aria-hidden="true"
        onClick={(e) => {
          const id = attr(e.target, "data-id");
          const sector = attr(e.target, "data-sector");
          if (id) onOpenPage(id);
          else if (sector) onPickSector(sector);
        }}
        onMouseOver={(e) => setHover(attr(e.target, "data-id"))}
        onMouseLeave={() => setHover(null)}
      >
        {marks}
        {chain && <polyline className="hop-chain" points={chain.points} style={{ stroke: chain.color }} />}
      </svg>
    </ViewportPortal>
  );
});
