import type { WikiNodeData } from "../types";

const DOMAIN_COLORS: Record<string, string> = {
  langgraph: "#4CAF50", rag: "#2196F3", adk: "#FF9800", mcp: "#9C27B0",
  memory: "#00BCD4", voice: "#F44336", eval: "#FFEB3B", infra: "#607D8B",
  llm: "#E91E63", "deep-agents": "#3F51B5", "context-management": "#009688",
};

const TYPE_LABELS: Record<string, string> = {
  concept: "Concept", pattern: "Pattern", decision: "Decision",
  project: "Project", comparison: "Comparison", reference: "Reference",
};

interface Props {
  nodeId: string;
  data: WikiNodeData;
  highlighted: boolean;
  lastQuery: string;
  onClose: () => void;
}

export function NodeDetailPanel({ data, highlighted, lastQuery, onClose }: Props) {
  const primaryDomain = (data.domain as string[])[0] ?? "infra";
  const color = DOMAIN_COLORS[primaryDomain] ?? "#607D8B";
  const fileName = data.path ? String(data.path).split("/").pop() : null;

  return (
    <div style={panelStyle}>
      {/* Colour accent bar */}
      <div style={{ height: 3, background: color, borderRadius: "8px 8px 0 0" }} />

      {/* Header */}
      <div style={headerStyle}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 10, color, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 6 }}>
            {(data.domain as string[]).join(" · ")}
            <span style={{ marginLeft: 8, color: "#555", fontWeight: 400, textTransform: "none", letterSpacing: 0 }}>
              {TYPE_LABELS[data.typeTag] ?? data.typeTag}
            </span>
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, color: "#f0f0f0", lineHeight: 1.2 }}>
            {data.title}
          </div>
        </div>
        <button onClick={onClose} style={closeBtnStyle} aria-label="Close">✕</button>
      </div>

      {/* Highlighted badge */}
      {highlighted && lastQuery && (
        <div style={{ padding: "0 20px 12px" }}>
          <span style={{ ...badgeStyle, borderColor: color, color, background: color + "18" }}>
            Referenced while answering: "{lastQuery}"
          </span>
        </div>
      )}

      {/* Summary */}
      {data.summary && (
        <div style={summaryStyle}>
          {data.summary}
        </div>
      )}

      {/* Tags */}
      <div style={{ padding: "0 20px 16px", display: "flex", flexWrap: "wrap", gap: 6 }}>
        {(data.tags as string[]).map((tag) => {
          const tagColor = DOMAIN_COLORS[tag] ?? "#444";
          return (
            <span key={tag} style={{
              background: tagColor + "22",
              border: `1px solid ${tagColor}`,
              color: tagColor,
              borderRadius: 12,
              padding: "3px 10px",
              fontSize: 11,
            }}>
              {tag}
            </span>
          );
        })}
      </div>

      {/* Footer meta */}
      <div style={footerStyle}>
        {fileName && (
          <span style={{ color: "#444", fontFamily: "monospace", fontSize: 11 }}>
            {fileName}
          </span>
        )}
        {data.updated && (
          <span style={{ color: "#444", fontSize: 11 }}>
            updated {data.updated}
          </span>
        )}
      </div>
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  position: "absolute",
  bottom: 20,
  left: "50%",
  transform: "translateX(-50%)",
  zIndex: 20,
  background: "#161616",
  border: "1px solid #2a2a2a",
  borderRadius: 8,
  width: "min(560px, 48vw)",
  maxHeight: "42vh",
  boxShadow: "0 8px 40px rgba(0,0,0,0.7)",
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
};

const headerStyle: React.CSSProperties = {
  padding: "18px 20px 14px",
  display: "flex",
  alignItems: "flex-start",
  gap: 12,
};

const summaryStyle: React.CSSProperties = {
  padding: "0 20px 16px",
  fontSize: 14,
  color: "#bbb",
  lineHeight: 1.65,
  flex: 1,
  overflowY: "auto",
};

const footerStyle: React.CSSProperties = {
  padding: "10px 20px",
  borderTop: "1px solid #222",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  flexShrink: 0,
};

const closeBtnStyle: React.CSSProperties = {
  background: "none",
  border: "none",
  color: "#555",
  cursor: "pointer",
  fontSize: 16,
  padding: 4,
  flexShrink: 0,
  lineHeight: 1,
};

const badgeStyle: React.CSSProperties = {
  display: "inline-block",
  border: "1px solid",
  borderRadius: 4,
  padding: "4px 10px",
  fontSize: 11,
  lineHeight: 1.4,
};
