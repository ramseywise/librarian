import { domainColor } from "../theme/domains";

interface Props {
  /** Domain list from the graph payload (disk-derived on the server; no `private`). */
  domains: string[];
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
  onBrief?: (domain: string) => void;
}

export function TagFilterPanel({ domains, activeTags, onChange, onBrief }: Props) {
  function toggle(tag: string) {
    const next = new Set(activeTags);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    onChange(next);
  }

  const allActive = activeTags.size === 0;

  return (
    <div className="float-panel graph-filter-panel" role="group" aria-label="Filter by domain">
      <div className="panel-label">Filter by Domain</div>
      <button
        type="button"
        aria-pressed={allActive}
        className="chip chip--all"
        onClick={() => onChange(new Set())}
      >
        All
      </button>
      {domains.filter((d) => d !== "private").map((tag) => {
        const active = activeTags.has(tag);
        const color = domainColor(tag);
        return (
          <div
            key={tag}
            role="group"
            aria-label={tag}
            className="chip-group"
            style={{
              background: active ? color + "22" : "transparent",
              border: `1px solid ${active ? color : "var(--border-strong)"}`,
            }}
          >
            <button
              type="button"
              aria-pressed={active}
              onClick={() => toggle(tag)}
              className={`chip-part${onBrief ? " chip-part--with-brief" : ""}`}
              style={{ color: active ? color : "var(--text-ghost)" }}
            >
              {tag}
            </button>
            {onBrief && (
              <button
                type="button"
                aria-label={`Brief me on ${tag}`}
                title={`Brief me on ${tag}`}
                onClick={() => onBrief(tag)}
                className="chip-part chip-brief"
                style={{ color: active ? color : "var(--text-muted)", background: color + "33" }}
              >
                ↗
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
