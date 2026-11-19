import { MiniMap } from "@xyflow/react";
import { EdgeTogglePanel } from "./EdgeTogglePanel";
import { LayoutSwitcher } from "./LayoutSwitcher";
import type { WikiFlowNode } from "./WikiNode";
import type { EdgeVisibility, LayoutMode } from "../types";

interface Props {
  edgeVis: EdgeVisibility;
  onEdgeVis: (v: EdgeVisibility) => void;
  onLoadSemantic: () => void;
  loadingSemantic: boolean;
  layout: LayoutMode;
  onLayout: (mode: LayoutMode) => void;
  loadingUmap: boolean;
  umapFailed: boolean;
  miniMapColor: (n: WikiFlowNode) => string;
  /** False under the chat, where the connections are listed inline instead. */
  withEdges?: boolean;
}

/**
 * The map's controls: connections, arrangement and the minimap. They act on the page canvas, so the
 * atlas has none. Rendered outside <ReactFlow> but inside its provider, so the minimap reads the same
 * store.
 */
export function MapControls({
  edgeVis, onEdgeVis, onLoadSemantic, loadingSemantic, layout, onLayout, loadingUmap, umapFailed, miniMapColor,
  withEdges = true,
}: Props) {
  return (
    <>
      {withEdges && (
        <EdgeTogglePanel
          visibility={edgeVis}
          onChange={onEdgeVis}
          onLoadSemantic={onLoadSemantic}
          loadingSemanticEdges={loadingSemantic}
        />
      )}
      <LayoutSwitcher
        current={layout}
        onChange={onLayout}
        loadingUmap={loadingUmap}
        umapUnavailable={layout === "umap-semantic" && umapFailed}
      />
      {/* The theme's colours are passed in because its CSS variables are scoped to the canvas. */}
      <div className="panel-label panel-label--spaced">Minimap</div>
      <div className="side-minimap">
        <MiniMap
          nodeColor={miniMapColor}
          className="graph-minimap"
          bgColor="var(--surface)"
          maskColor="var(--minimap-mask)"
          maskStrokeColor="var(--border-pressed)"
          style={{ width: 240, height: 150 }}
          pannable
          zoomable
          ariaLabel="Minimap"
        />
      </div>
    </>
  );
}
