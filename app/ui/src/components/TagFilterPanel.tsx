const DOMAIN_TAGS = [
  "langgraph", "rag", "adk", "mcp", "memory", "voice",
  "eval", "infra", "llm", "deep-agents", "context-management",
];

const TAG_COLORS: Record<string, string> = {
  langgraph: "#4CAF50", rag: "#2196F3", adk: "#FF9800", mcp: "#9C27B0",
  memory: "#00BCD4", voice: "#F44336", eval: "#FFEB3B", infra: "#607D8B",
  llm: "#E91E63", "deep-agents": "#3F51B5", "context-management": "#009688",
};

interface Props {
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
}

export function TagFilterPanel({ activeTags, onChange }: Props) {
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
            }}
          >
            {tag}
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
