import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { mapPath, parentOf, type Grouping, type MapView } from "../utils/mapRoute";

interface Props {
  view: MapView;
  sectorLabel?: string;
  pageTitle?: string;
  /** Focused views: pages from the level on the canvas, of how many it could hold. */
  shown?: number;
  total?: number;
  hops?: number;
  revealedExtra: number;
  onResetRevealed: () => void;
  /** The next cap, when there is more to show. */
  nextCap: number | null;
  onExpand: () => void;
  /** Label of the page a click has focused, offered as the next level. */
  refocus: { title: string; onClick: () => void } | null;
  /** The Domain / Wiki switch: the map's arrangement. */
  onGrouping: (g: Grouping) => void;
  /** The map's search box. */
  search?: ReactNode;
  /** The filters list, and how many are active (shown on the button). */
  filters?: ReactNode;
  activeCount?: number;
  /** How a focused map is drawn: connections, arrangement, minimap. Absent on the atlas, which draws no lines. */
  map?: ReactNode;
  /** A brief on the sector in the crumbs; no button without it. */
  onBriefSector?: () => void;
}

/**
 * A button and the panel it opens under it. Escape or a click outside closes it; Escape closes only
 * the popover, not the level behind it.
 */
function Popover({ label, children }: { label: string; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const wrap = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const panelId = useId();
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (!wrap.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [open]);
  return (
    <div
      className="map-pop"
      ref={wrap}
      onKeyDown={(e) => {
        if (e.key !== "Escape" || !open) return;
        e.preventDefault();
        setOpen(false);
        button.current?.focus();
      }}
    >
      <button
        ref={button}
        type="button"
        className="pill-btn map-pop-btn"
        aria-expanded={open}
        aria-controls={open ? panelId : undefined}
        onClick={() => setOpen((o) => !o)}
      >
        {label}
      </button>
      {open && (
        <div id={panelId} className="map-pop-panel" role="group" aria-label={label.replace(/ \(\d+\)$/, "")}>
          {children}
        </div>
      )}
    </div>
  );
}

/**
 * The map's one bar: the Domain / Wiki switch, search and the Filters popover on every level; on a
 * focused level also the breadcrumb, Back, how much of the level is shown, and a Map popover for
 * connections, arrangement and the minimap (the atlas draws no lines, so none there).
 */
export function MapBar({
  view,
  sectorLabel,
  pageTitle,
  shown,
  total,
  hops,
  revealedExtra,
  onResetRevealed,
  nextCap,
  onExpand,
  refocus,
  onGrouping,
  search,
  filters,
  activeCount = 0,
  map,
  onBriefSector,
}: Props) {
  const grouping = view.level === "all" ? "domain" : view.grouping;
  const parent = parentOf(view);
  const sectorPath = view.level === "page" ? mapPath(parentOf(view)!) : null;
  const atlas = view.level === "atlas";
  const brief = onBriefSector && (
    <button
      type="button"
      className="map-brief"
      aria-label={`Brief me on ${sectorLabel ?? (view.level === "sector" || view.level === "page" ? view.sector : "")}`}
      onClick={onBriefSector}
    >
      Brief me ↗
    </button>
  );
  const switcher = (
    <div className="seg" role="group" aria-label="Browse by">
      {(["domain", "wiki"] as const).map((g) => (
        <button key={g} type="button" className="seg-btn" aria-pressed={grouping === g} onClick={() => onGrouping(g)}>
          {g === "domain" ? "Domain" : "Wiki"}
        </button>
      ))}
    </div>
  );
  const tools = (
    <>
      {search}
      {filters && <Popover label={activeCount ? `Filters (${activeCount})` : "Filters"}>{filters}</Popover>}
      {map && <Popover label="Map">{map}</Popover>}
    </>
  );
  if (atlas) {
    return (
      <div className="map-bar map-bar--atlas">
        {switcher}
        {tools}
      </div>
    );
  }
  return (
    <div className="map-bar map-bar--focused">
      <a className="pill-btn map-back" href={`#${parent ? mapPath(parent) : "/"}`}>
        ‹ Back
      </a>
      <nav className="map-crumbs" aria-label="Map level">
        <a href={`#${mapPath({ level: "atlas", grouping })}`}>Atlas</a>
        <span aria-hidden="true">/</span>
        {view.level === "all" ? (
          <span aria-current="page">All nodes</span>
        ) : sectorPath ? (
          <>
            <a href={`#${sectorPath}`}>{sectorLabel ?? view.sector}</a>
            {brief}
            <span aria-hidden="true">/</span>
            <span aria-current="page" className="map-crumb-page" title={pageTitle}>
              {pageTitle}
            </span>
          </>
        ) : (
          <>
            <span aria-current="page">{sectorLabel ?? view.sector}</span>
            {brief}
          </>
        )}
      </nav>
      {switcher}
      {total != null && (
        <span className="map-count">
          showing {shown} of {total}
          {view.level === "page" && hops != null && hops > 0 ? ` · ${hops} ${hops === 1 ? "hop" : "hops"}` : ""}
        </span>
      )}
      {nextCap != null && (
        <button type="button" className="pill-btn" onClick={onExpand}>
          Show {nextCap}
        </button>
      )}
      {revealedExtra > 0 && (
        <button type="button" className="pill-btn" onClick={onResetRevealed} title="Drop the pages your clicks revealed">
          Reset +{revealedExtra}
        </button>
      )}
      {refocus && (
        <button type="button" className="pill-btn map-refocus" onClick={refocus.onClick} title={refocus.title}>
          Focus here
        </button>
      )}
      {tools}
    </div>
  );
}
