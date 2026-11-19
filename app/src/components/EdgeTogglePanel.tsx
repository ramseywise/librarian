import type { EdgeVisibility } from "../types";
import "./filter.css";

interface Props {
  visibility: EdgeVisibility;
  onChange: (v: EdgeVisibility) => void;
  onLoadSemantic: () => void;
  loadingSemanticEdges: boolean;
}

interface ChipProps extends Props {
  /** Why the chips do nothing here (the atlas draws no lines); shown beside them, and they are disabled. */
  inactive?: string;
}

/** Each kind of line between pages: a plain label, a short hint shown beside it, and the full story on hover. */
const EDGE_META: { key: keyof EdgeVisibility; label: string; hint: string; color: string; description: string }[] = [
  { key: "wikilink", label: "Wikilinks", hint: "one page links to the other", color: "var(--edge-wikilink-label)", description: "Explicit [[...]] references in the page text. Typed See Also links count most when ranking a page's level." },
  { key: "semantic", label: "Similar meaning", hint: "by embedding", color: "var(--edge-semantic)", description: "Each page's 5 nearest pages by MiniLM embedding (cosine ≥ 0.45). Also ranks the pages a page's level pulls in." },
  { key: "module", label: "Same module", hint: "taught together", color: "var(--edge-module)", description: "Pages taught in the same curriculum module, each joined to the module's best-linked page here. Also ranks the pages a page's level pulls in." },
  { key: "course-order", label: "Course order", hint: "taught next", color: "var(--edge-course)", description: "Within a module, each page joined to the next one its notes teach, earlier → later. Also ranks the pages a page's level pulls in." },
  { key: "term", label: "Shared term", hint: "same glossary term", color: "var(--edge-term)", description: "Pages mentioning the same glossary term; terms on more than 80 pages are skipped. Also ranks the pages a page's level pulls in." },
  { key: "tag-shared", label: "Shared tag", hint: "same domain tag", color: "var(--edge-tag)", description: "Pages sharing a domain tag. Shown around emphasised pages only: the filter, the clicked node or chat results." },
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

/** The dock's three connection chips, each one or more edge kinds: what joins two pages, in a word. */
const CONNECT_CHIPS: { label: string; keys: (keyof EdgeVisibility)[]; color: string; description: string }[] = [
  { label: "Links", keys: ["wikilink"], color: "var(--edge-wikilink-label)", description: "One page links to the other ([[...]]); typed See Also links count most when ranking a page's level." },
  { label: "Similar", keys: ["semantic", "term"], color: "var(--edge-semantic)", description: "Similar meaning by embedding, and the same glossary term (terms on more than 80 pages skipped)." },
];

/** Under the chat: links against similarity as two chips, pinned under the filters on every level. */
export function ConnectChips({ visibility, onChange, onLoadSemantic, loadingSemanticEdges, inactive }: ChipProps) {
  return (
    <div className="connect-chips" role="group" aria-label="Connect by">
      <span className="panel-label">Connect by</span>
      {CONNECT_CHIPS.map(({ label, keys, color, description }) => {
        // On when any of its kinds is: one press then switches them all the same way.
        const on = keys.some((k) => visibility[k]);
        return (
          <button
            key={label}
            type="button"
            className="chip connect-chip"
            aria-pressed={on}
            disabled={!!inactive}
            title={description}
            style={on ? { color, borderColor: color } : undefined}
            onClick={() => {
              const next = { ...visibility };
              for (const k of keys) next[k] = !on;
              if (!on && keys.includes("semantic")) onLoadSemantic();
              onChange(next);
            }}
          >
            {label}
            {keys.includes("semantic") && loadingSemanticEdges && " …"}
          </button>
        );
      })}
      {inactive && <span className="connect-note">{inactive}</span>}
    </div>
  );
}
