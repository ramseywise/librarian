import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import "./filter.css";
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
  /** Under the chat: the connection types, listed inline after the filters rather than in the Map popover. */
  connections?: ReactNode;
  /** A brief on the sector in the crumbs; no button without it. */
  onBriefSector?: () => void;
  /** Anything else for the end of the bar: the All nodes button. */
  extra?: ReactNode;
  /** Under the chat: no Back, breadcrumb or count, and the filters and connections listed inline. */
  controlsOnly?: boolean;
}

/**
 * A button and the panel it opens over it (the bar sits at the bottom of the screen). Escape or a click outside closes it; Escape closes only
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
      // Only catches an Escape bubbling up from the Map button and its popover; not a control itself.
      role="presentation"
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
 * The map's bar: the Domain / Wiki switch, search and the Filters popover on every level; on a
 * focused level also the breadcrumb, Back, how much of the level is shown, and a Map popover for
 * connections, arrangement and the minimap (the atlas draws no lines, so none there). Under the
 * chat the bar is `controlsOnly`: the switch, then search and the Map popover, then the filters and
 * the connections inline, broadest first, with no Back or breadcrumb.
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
  connections,
  onBriefSector,
  extra,
  controlsOnly,
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
    <div className="map-browse">
      <span className="panel-label">Browse by</span>
      <div className="seg" role="group" aria-label="Browse by">
        {(["domain", "wiki"] as const).map((g) => (
          <button key={g} type="button" className="seg-btn" aria-pressed={grouping === g} onClick={() => onGrouping(g)}>
            {g === "domain" ? "Domain" : "Wiki"}
          </button>
        ))}
      </div>
    </div>
  );
  const more = (
    <>
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
    </>
  );
  const controls = (
    <>
      {filters && <Popover label={activeCount ? `Filters (${activeCount})` : "Filters"}>{filters}</Popover>}
      {map && <Popover label="Map">{map}</Popover>}
      {extra}
    </>
  );
  if (controlsOnly) {
    return (
      <div className="map-bar map-bar--docked">
        {switcher}
        <div className="map-dock-row">
          {search}
          {map && <Popover label="Layout">{map}</Popover>}
          {extra}
          {more}
        </div>
        <div className="map-dock-scroll">
          {filters && (
            <section aria-label="Filters" className="map-dock-filters">
              {filters}
            </section>
          )}
          {connections && (
            <details className="side-section" open>
              <summary className="panel-label">Connect by</summary>
              <div className="side-section-body">{connections}</div>
            </details>
          )}
        </div>
      </div>
    );
  }
  if (atlas) {
    return (
      <div className="map-bar map-bar--atlas">
        {switcher}
        {search}
        {controls}
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
      {more}
      {refocus && (
        <button type="button" className="pill-btn map-refocus" onClick={refocus.onClick} title={refocus.title}>
          Focus here
        </button>
      )}
      {search}
      {controls}
    </div>
  );
}
