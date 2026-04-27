import type { EdgeVisibility } from "../types";

interface Props {
  visibility: EdgeVisibility;
  onChange: (v: EdgeVisibility) => void;
  onLoadSemantic: () => void;
  loadingSemanticEdges: boolean;
}

const EDGE_META: { key: keyof EdgeVisibility; label: string; color: string; description: string }[] = [
  { key: "wikilink", label: "Wikilinks", color: "#aaa", description: "Explicit [[...]] references" },
  { key: "semantic", label: "Semantic", color: "#4a90d9", description: "Cosine similarity ≥ 0.65 (MiniLM)" },
  { key: "tag-shared", label: "Tag-shared", color: "#e8943a", description: "Pages sharing a domain tag (cross-domain structural links)" },
];

export function EdgeTogglePanel({ visibility, onChange, onLoadSemantic, loadingSemanticEdges }: Props) {
  function toggle(key: keyof EdgeVisibility) {
    const next = { ...visibility, [key]: !visibility[key] };
    if (key === "semantic" && next.semantic) {
      onLoadSemantic();
    }
    onChange(next);
  }

  return (
    <div style={panelStyle}>
      <div style={labelStyle}>Edge Types</div>
      {EDGE_META.map(({ key, label, color, description }) => (
        <label key={key} style={rowStyle} title={description}>
          <input
            type="checkbox"
            checked={visibility[key]}
            onChange={() => toggle(key)}
            style={{ accentColor: color }}
          />
          <span style={{ color, fontSize: 12, marginLeft: 6 }}>
            {label}
            {key === "semantic" && loadingSemanticEdges && " …"}
          </span>
        </label>
      ))}
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  position: "absolute",
  top: 12,
  left: 12,
  zIndex: 10,
  background: "#1c1c1c",
  border: "1px solid #333",
  borderRadius: 8,
  padding: "10px 14px",
  display: "flex",
  flexDirection: "column",
  gap: 8,
};

const labelStyle: React.CSSProperties = {
  fontSize: 10,
  color: "#666",
  fontWeight: 700,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  marginBottom: 2,
};

const rowStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  cursor: "pointer",
};
