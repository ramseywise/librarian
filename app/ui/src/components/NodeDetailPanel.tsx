import type { WikiNodeData } from "../types";

const TAG_COLORS: Record<string, string> = {
  langgraph: "#4CAF50", rag: "#2196F3", adk: "#FF9800", mcp: "#9C27B0",
  memory: "#00BCD4", voice: "#F44336", eval: "#FFEB3B", infra: "#607D8B",
  llm: "#E91E63", "deep-agents": "#3F51B5", "context-management": "#009688",
};

interface Props {
  nodeId: string;
  data: WikiNodeData;
  highlighted: boolean;
  lastQuery: string;
  onClose: () => void;
}

export function NodeDetailPanel({ data, highlighted, lastQuery, onClose }: Props) {
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <span style={{ fontWeight: 600, color: "#e0e0e0", fontSize: 13, flex: 1, marginRight: 8 }}>
          {data.title}
        </span>
        <button onClick={onClose} style={closeBtnStyle}>✕</button>
      </div>

      {highlighted && lastQuery && (
        <div style={{ padding: "6px 14px 0" }}>
          <span style={badgeStyle}>Referenced while answering: "{lastQuery}"</span>
        </div>
      )}

      {data.summary && (
        <div style={{ padding: "10px 14px", fontSize: 12, color: "#aaa", lineHeight: 1.6 }}>
          {data.summary}
        </div>
      )}

      <div style={{ padding: "0 14px 10px", display: "flex", flexWrap: "wrap", gap: 4 }}>
        {(data.domain as string[]).map((tag) => (
          <span
            key={tag}
            style={{
              background: (TAG_COLORS[tag] ?? "#607D8B") + "22",
              border: `1px solid ${TAG_COLORS[tag] ?? "#607D8B"}`,
              color: TAG_COLORS[tag] ?? "#607D8B",
              borderRadius: 10,
              padding: "2px 8px",
              fontSize: 10,
            }}
          >
            {tag}
          </span>
        ))}
        <span
          style={{
            background: "#2a2a2a",
            border: "1px solid #444",
            color: "#666",
            borderRadius: 10,
            padding: "2px 8px",
            fontSize: 10,
          }}
        >
          {data.typeTag}
        </span>
      </div>

      {data.updated && (
        <div style={{ padding: "0 14px 10px", fontSize: 10, color: "#444" }}>
          updated {data.updated}
        </div>
      )}
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  position: "absolute",
  bottom: 80,
  right: 12,
  zIndex: 20,
  background: "#1c1c1c",
  border: "1px solid #333",
  borderRadius: 8,
  minWidth: 260,
  maxWidth: 320,
  boxShadow: "0 4px 24px rgba(0,0,0,0.5)",
};

const headerStyle: React.CSSProperties = {
  padding: "10px 14px",
  borderBottom: "1px solid #222",
  display: "flex",
  alignItems: "flex-start",
};

const closeBtnStyle: React.CSSProperties = {
  background: "none",
  border: "none",
  color: "#555",
  cursor: "pointer",
  fontSize: 14,
  padding: "0 2px",
  flexShrink: 0,
};

const badgeStyle: React.CSSProperties = {
  display: "inline-block",
  background: "#2196F322",
  border: "1px solid #2196F3",
  color: "#2196F3",
  borderRadius: 4,
  padding: "3px 8px",
  fontSize: 10,
  lineHeight: 1.4,
};
