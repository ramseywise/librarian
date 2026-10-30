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
  { key: "tag-shared", label: "Tag-shared", color: "#e8943a", description: "Pages sharing a domain tag (cross-domain structural links). Shown around emphasised pages only: projects in overview, the filter, the clicked node or chat results." },
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
    <div className="float-panel graph-edge-panel">
      <div className="panel-label">Edge Types</div>
      {EDGE_META.map(({ key, label, color, description }) => (
        <label key={key} className="edge-row" title={description}>
          <input
            type="checkbox"
            checked={visibility[key]}
            onChange={() => toggle(key)}
            style={{ accentColor: color }}
          />
          <span className="edge-label" style={{ color }}>
            {label}
            {key === "semantic" && loadingSemanticEdges && " …"}
          </span>
        </label>
      ))}
    </div>
  );
}
