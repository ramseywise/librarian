import { mapPath, parentOf, type MapView } from "../utils/mapRoute";

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
}

/**
 * Where you are on the map and the way back: breadcrumb, Back, how much of the level is shown.
 * None on the atlas, the top level; the Domain / Course switch and search are in the sidebar.
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
}: Props) {
  if (view.level === "atlas") return null;

  const grouping = view.level === "all" ? "domain" : view.grouping;
  const parent = parentOf(view);
  const sectorPath = view.level === "page" ? mapPath(parentOf(view)!) : null;
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
            <span aria-hidden="true">/</span>
            <span aria-current="page" className="map-crumb-page" title={pageTitle}>
              {pageTitle}
            </span>
          </>
        ) : (
          <span aria-current="page">{sectorLabel ?? view.sector}</span>
        )}
      </nav>
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
    </div>
  );
}
