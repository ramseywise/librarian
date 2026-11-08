import type { EdgeVisibility } from "../types";

interface Props {
  visibility: EdgeVisibility;
  onChange: (v: EdgeVisibility) => void;
  onLoadSemantic: () => void;
  loadingSemanticEdges: boolean;
}

/** Each kind of line between pages: a plain label, a short hint shown beside it, and the full story on hover. */
const EDGE_META: { key: keyof EdgeVisibility; label: string; hint: string; color: string; description: string }[] = [
  { key: "wikilink", label: "Wikilinks", hint: "one page links to the other", color: "var(--edge-wikilink-label)", description: "Explicit [[...]] references in the page text" },
  { key: "semantic", label: "Similar meaning", hint: "by embedding", color: "var(--edge-semantic)", description: "Cosine similarity ≥ 0.65 between the pages' MiniLM embeddings" },
  { key: "module", label: "Same module", hint: "taught together", color: "var(--edge-module)", description: "Pages taught in the same curriculum module, each joined to the module's best-linked page here" },
  { key: "tag-shared", label: "Shared tag", hint: "same domain tag", color: "var(--edge-tag)", description: "Pages sharing a domain tag. Shown around emphasised pages only: the filter, the clicked node or chat results." },
  { key: "terms", label: "Glossary terms", hint: "term → pages that use it", color: "var(--concept)", description: "Glossary terms on these pages, joined to the pages that mention them" },
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
    <div className="graph-edge-panel" role="group" aria-label="Connections">
      {EDGE_META.map(({ key, label, hint, color, description }) => (
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
          <span className="edge-hint">{hint}</span>
        </label>
      ))}
    </div>
  );
}
