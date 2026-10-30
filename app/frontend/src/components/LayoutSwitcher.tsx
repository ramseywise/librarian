import type { LayoutMode } from "../types";

interface Props {
  current: LayoutMode;
  onChange: (mode: LayoutMode) => void;
  loadingUmap: boolean;
  /** The server could not compute UMAP; the graph is showing the hierarchy layout instead. */
  umapUnavailable?: boolean;
}

const MODES: { key: LayoutMode; label: string; hint: string }[] = [
  { key: "dagre", label: "Hierarchy", hint: "Top-down by link structure" },
  { key: "umap-semantic", label: "Semantic", hint: "Spatial position encodes meaning (UMAP)" },
];

export function LayoutSwitcher({ current, onChange, loadingUmap, umapUnavailable }: Props) {
  return (
    <div className="float-panel graph-layout-panel">
      <div className="panel-label panel-label--spaced">Layout</div>
      <div className="btn-row">
        {MODES.map(({ key, label, hint }) => (
          <button
            key={key}
            type="button"
            title={key === "umap-semantic" && umapUnavailable ? "UMAP unavailable on the server — showing Hierarchy" : hint}
            aria-pressed={current === key}
            onClick={() => onChange(key)}
            className="toggle-btn"
          >
            {label}
            {key === "umap-semantic" && loadingUmap && " …"}
            {key === "umap-semantic" && umapUnavailable && " (unavailable)"}
          </button>
        ))}
      </div>
    </div>
  );
}
