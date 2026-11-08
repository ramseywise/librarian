import type { EdgeVisibility } from "../types";

interface Props {
  visibility: EdgeVisibility;
  onChange: (v: EdgeVisibility) => void;
  onLoadSemantic: () => void;
  loadingSemanticEdges: boolean;
}

const EDGE_META: { key: keyof EdgeVisibility; label: string; color: string; description: string }[] = [
  { key: "wikilink", label: "Wikilinks", color: "var(--edge-wikilink-label)", description: "Explicit [[...]] references" },
  { key: "semantic", label: "Semantic", color: "var(--edge-semantic)", description: "Cosine similarity ≥ 0.65 (MiniLM)" },
  { key: "module", label: "Same module", color: "var(--edge-module)", description: "Pages taught in the same curriculum module, each joined to the module's best-linked page here" },
  { key: "tag-shared", label: "Shared tag", color: "var(--edge-tag)", description: "Pages sharing a domain tag (cross-domain structural links). Shown around emphasised pages only: projects in overview, the filter, the clicked node or chat results." },
  { key: "terms", label: "Glossary terms", color: "var(--concept)", description: "Glossary terms on these pages, joined to the pages that mention them" },
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
    <div className="graph-edge-panel" role="group" aria-label="Layers">
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
