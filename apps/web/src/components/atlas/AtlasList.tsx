import { useState } from "react";
import type { AtlasSector } from "../../utils/atlas";
import { DEFAULT_CAP, mapPath, PAGE_CAP, type Grouping } from "../../utils/mapRoute";

interface Props {
  sectors: AtlasSector[];
  grouping: Grouping;
  titleOf: (id: string) => string;
  matches: Set<string> | null;
}

function SectorRows({ sector, grouping, titleOf, matches }: { sector: AtlasSector } & Omit<Props, "sectors">) {
  const [open, setOpen] = useState(false);
  const ids = matches ? sector.pageIds.filter((id) => matches.has(id)) : sector.pageIds;
  return (
    <details className="atlas-list-sector" onToggle={(e) => setOpen(e.currentTarget.open)}>
      <summary>
        {sector.label} <span className="cur-count">{ids.length}</span>
      </summary>
      {open && (
        <ul>
          <li>
            <a href={`#${mapPath({ level: "sector", grouping, sector: sector.id, cap: DEFAULT_CAP })}`}>Open this sector</a>
          </li>
          {ids.map((id) => (
            <li key={id}>
              <a href={`#${mapPath({ level: "page", grouping, sector: sector.id, page: id, cap: PAGE_CAP })}`}>
                {titleOf(id)}
              </a>
            </li>
          ))}
        </ul>
      )}
    </details>
  );
}

/** The whole atlas as plain links: what the ring shows, reachable without the canvas. */
export function AtlasList({ sectors, grouping, titleOf, matches }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <details className="atlas-list" onToggle={(e) => setOpen(e.currentTarget.open)}>
      <summary>Browse as a list</summary>
      {open && (
        <div className="atlas-list-body">
          {sectors.map((s) => (
            <SectorRows key={s.id} sector={s} grouping={grouping} titleOf={titleOf} matches={matches} />
          ))}
        </div>
      )}
    </details>
  );
}
