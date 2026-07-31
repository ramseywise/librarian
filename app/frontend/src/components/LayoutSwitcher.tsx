import type { LayoutMode } from "../types";

interface Props {
  current: LayoutMode;
  onChange: (mode: LayoutMode) => void;
  loadingUmap: boolean;
}

const MODES: { key: LayoutMode; label: string; hint: string }[] = [
  { key: "dagre", label: "Hierarchy", hint: "Top-down by link structure" },
  { key: "umap-semantic", label: "Semantic", hint: "Spatial position encodes meaning (UMAP)" },
];

export function LayoutSwitcher({ current, onChange, loadingUmap }: Props) {
  return (
    <div style={panelStyle}>
      <div style={labelStyle}>Layout</div>
      <div style={{ display: "flex", gap: 6 }}>
        {MODES.map(({ key, label, hint }) => (
          <button
            key={key}
            title={hint}
            onClick={() => onChange(key)}
            style={{
              ...btnStyle,
              background: current === key ? "#2a2a2a" : "transparent",
              border: `1px solid ${current === key ? "#555" : "#333"}`,
              color: current === key ? "#e0e0e0" : "#666",
            }}
          >
            {label}
            {key === "umap-semantic" && loadingUmap && " …"}
          </button>
        ))}
      </div>
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  position: "absolute",
  top: 12,
  right: 12,
  zIndex: 10,
  background: "#1c1c1c",
  border: "1px solid #333",
  borderRadius: 8,
  padding: "10px 14px",
};

const labelStyle: React.CSSProperties = {
  fontSize: 10,
  color: "#666",
  fontWeight: 700,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  marginBottom: 8,
};

const btnStyle: React.CSSProperties = {
  padding: "4px 10px",
  borderRadius: 5,
  fontSize: 12,
  cursor: "pointer",
};
