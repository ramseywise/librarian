const DOMAIN_TAGS = [
  "rag", "langgraph", "adk", "infra", "patterns",
  "eval", "deep-agents", "memory", "mcp", "meta", "projects",
];

const TAG_COLORS: Record<string, string> = {
  rag: "#2196F3", langgraph: "#4CAF50", adk: "#FF9800", infra: "#607D8B",
  patterns: "#E91E63", eval: "#FFEB3B", "deep-agents": "#3F51B5",
  memory: "#00BCD4", mcp: "#9C27B0", meta: "#795548", projects: "#009688",
};

interface Props {
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
  onBrief?: (domain: string) => void;
}

export function TagFilterPanel({ activeTags, onChange, onBrief }: Props) {
  function toggle(tag: string) {
    const next = new Set(activeTags);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    onChange(next);
  }

  const allActive = activeTags.size === 0;

  return (
    <div style={panelStyle}>
      <div style={labelStyle}>Filter by Domain</div>
      <button
        style={{ ...chipStyle, background: allActive ? "#333" : "transparent", color: allActive ? "#e0e0e0" : "#555", border: "1px solid #444" }}
        onClick={() => onChange(new Set())}
      >
        All
      </button>
      {DOMAIN_TAGS.map((tag) => {
        const active = activeTags.has(tag);
        const color = TAG_COLORS[tag] ?? "#607D8B";
        return (
          <button
            key={tag}
            onClick={() => toggle(tag)}
            style={{
              ...chipStyle,
              background: active ? color + "22" : "transparent",
              border: `1px solid ${active ? color : "#333"}`,
              color: active ? color : "#555",
              display: "flex",
              alignItems: "center",
              gap: 4,
              padding: "3px 6px 3px 8px",
            }}
          >
            {tag}
            {onBrief && (
              <span
                onClick={(e) => { e.stopPropagation(); onBrief(tag); }}
                title={`Brief me on ${tag}`}
                style={{
                  fontSize: 9,
                  opacity: 0.5,
                  padding: "1px 3px",
                  borderRadius: 3,
                  background: color + "33",
                }}
              >
                ↗
              </span>
            )}
          </button>
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
