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
    <div style={panelStyle} role="group" aria-label="Filter by domain">
      <div style={labelStyle}>Filter by Domain</div>
      <button
        type="button"
        aria-pressed={allActive}
        style={{ ...chipStyle, background: allActive ? "#333" : "transparent", color: allActive ? "#e0e0e0" : "#555", border: "1px solid #444" }}
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
            style={{
              ...chipGroupStyle,
              background: active ? color + "22" : "transparent",
              border: `1px solid ${active ? color : "#333"}`,
            }}
          >
            <button
              type="button"
              aria-pressed={active}
              onClick={() => toggle(tag)}
              style={{ ...chipPartStyle, color: active ? color : "#555", padding: onBrief ? "3px 4px 3px 8px" : "3px 8px" }}
            >
              {tag}
            </button>
            {onBrief && (
              <button
                type="button"
                aria-label={`Brief me on ${tag}`}
                title={`Brief me on ${tag}`}
                onClick={() => onBrief(tag)}
                style={{ ...chipPartStyle, ...briefStyle, color: active ? color : "#777", background: color + "33" }}
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

const panelStyle: React.CSSProperties = {
  position: "absolute",
  bottom: 12,
  left: 12,
  zIndex: 10,
  background: "#1c1c1c",
  border: "1px solid #333",
  borderRadius: 8,
  padding: "10px 14px",
  display: "flex",
  flexWrap: "wrap",
  gap: 6,
  maxWidth: 340,
};

const labelStyle: React.CSSProperties = {
  width: "100%",
  fontSize: 10,
  color: "#666",
  fontWeight: 700,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  marginBottom: 2,
};

const chipStyle: React.CSSProperties = {
  padding: "3px 8px",
  borderRadius: 12,
  fontSize: 11,
  cursor: "pointer",
};

const chipGroupStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  borderRadius: 12,
  overflow: "hidden",
};

const chipPartStyle: React.CSSProperties = {
  background: "transparent",
  border: "none",
  fontSize: 11,
  fontFamily: "inherit",
  cursor: "pointer",
};

const briefStyle: React.CSSProperties = {
  fontSize: 9,
  padding: "2px 6px",
  margin: "0 3px 0 0",
  borderRadius: 3,
};
