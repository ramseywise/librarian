import { useId, useRef, useState } from "react";
import type { SearchResult } from "../utils/glossary";

interface Props {
  value: string;
  onChange: (query: string) => void;
  result: SearchResult | null;
  /** A page was chosen from the results. */
  onOpenPage: (pageId: string) => void;
}

/** The map's search box. Matches light up on the map as you type; picking a result opens it. */
export function MapSearch({ value, onChange, result, onOpenPage }: Props) {
  const [active, setActive] = useState(-1);
  const [open, setOpen] = useState(false);
  const listId = useId();
  const blurTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const hits = result?.hits ?? [];
  const showList = open && !!result;

  function choose(index: number) {
    const page = hits[index]?.page;
    if (!page) return;
    setOpen(false);
    onOpenPage(page);
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Escape") {
      // One press, one thing: this clears the search and doesn't also leave the level.
      e.preventDefault();
      e.stopPropagation();
      e.nativeEvent.stopImmediatePropagation();
      onChange("");
      setOpen(false);
      setActive(-1);
    } else if (e.key === "ArrowDown" && hits.length) {
      e.preventDefault();
      setOpen(true);
      setActive((a) => (a + 1) % hits.length);
    } else if (e.key === "ArrowUp" && hits.length) {
      e.preventDefault();
      setActive((a) => (a <= 0 ? hits.length - 1 : a - 1));
    } else if (e.key === "Enter" && hits.length) {
      e.preventDefault();
      choose(Math.max(active, 0));
    }
  }

  return (
    <div className="map-search">
      <input
        className="map-search-input"
        data-view-search
        type="search"
        placeholder="Search pages, terms"
        aria-label="Search the map"
        role="combobox"
        aria-expanded={showList}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={showList && active >= 0 ? `${listId}-${active}` : undefined}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
          setActive(-1);
        }}
        onFocus={() => {
          clearTimeout(blurTimer.current);
          setOpen(true);
        }}
        // Later than a click on a result, which would otherwise lose its target.
        onBlur={() => {
          blurTimer.current = setTimeout(() => setOpen(false), 120);
        }}
        onKeyDown={onKeyDown}
      />
      <ul id={listId} role="listbox" aria-label="Search results" className="map-search-list" hidden={!showList}>
        {hits.length === 0 && showList && <li className="map-search-none">No matches</li>}
        {hits.map((hit, i) => (
          <li
            key={`${hit.kind}:${hit.id}`}
            id={`${listId}-${i}`}
            role="option"
            aria-selected={i === active}
            className={`map-search-hit${i === active ? " is-active" : ""}`}
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => choose(i)}
          >
            <span className="map-search-label">
              {hit.kind === "term" && <span className="map-search-kind">term</span>}
              {hit.label}
            </span>
            <span className="map-search-detail">{hit.detail}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
