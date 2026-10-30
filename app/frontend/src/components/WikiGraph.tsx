import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { WikiNode, type WikiFlowNode } from "./WikiNode";
import { EdgeTogglePanel } from "./EdgeTogglePanel";
import { LayoutSwitcher } from "./LayoutSwitcher";
import { TagFilterPanel } from "./TagFilterPanel";
import { useWikiData } from "../hooks/useWikiData";
import { applyDagreLayout, placeMissingNodes, type XY } from "../utils/layout";
import {
  applyView,
  expandOneHop,
  filterPrimaryIds,
  focusNeighbourhood,
  visibleEdges,
  type ViewState,
} from "../utils/graphView";
import { domainColor } from "../theme/domains";
import type { EdgeVisibility, LayoutMode, SelectedNode, WikiNodeData } from "../types";

const NODE_TYPES = { wikiNode: WikiNode };
const NO_NODES: WikiFlowNode[] = [];

interface WikiGraphProps {
  highlightedPages?: Set<string>;
  /** Wiki page to pan/zoom to — set when arriving from a course lesson's concept link. */
  focusPage?: string | null;
  onNodeSelect?: (node: SelectedNode | null) => void;
  /** Called once `focusPage` has been applied (node found, view fitted, node selected). */
  onFocusApplied?: () => void;
  onBrief?: (domain: string) => void;
  activeTags: Set<string>;
  onActiveTagsChange: (tags: Set<string>) => void;
}

function positionsOf(nodes: Node[]): Record<string, XY> {
  return Object.fromEntries(nodes.map((n) => [n.id, n.position]));
}

function WikiGraphInner({
  highlightedPages,
  focusPage,
  onNodeSelect,
  onFocusApplied,
  onBrief,
  activeTags,
  onActiveTagsChange,
}: WikiGraphProps) {
  const {
    baseNodes,
    wikilinkEdges,
    domains,
    tagSharedEdges,
    semanticEdges,
    fetchSemanticEdges,
    umapPositions,
    umapFailed,
    loadUmapPositions,
    connected,
  } = useWikiData();

  const [edgeVis, setEdgeVis] = useState<EdgeVisibility>({
    wikilink: false,
    semantic: false,
    "tag-shared": true,
  });
  const [layout, setLayout] = useState<LayoutMode>("umap-semantic");
  const [overviewMode, setOverviewMode] = useState(true);
  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);
  const [loadingSemantic, setLoadingSemantic] = useState(false);
  // Narrow screens only: the control panels collapse behind one menu button.
  const [menuOpen, setMenuOpen] = useState(false);
  const menuBtnRef = useRef<HTMLButtonElement>(null);
  const { fitView } = useReactFlow();

  const hasNodes = baseNodes.length > 0;
  const loadingUmap = layout === "umap-semantic" && hasNodes && !umapPositions && !umapFailed;

  // UMAP positions are fetched once, on first use; the hook caches them.
  useEffect(() => {
    if (layout === "umap-semantic" && hasNodes) void loadUmapPositions();
  }, [layout, hasNodes, loadUmapPositions]);

  const structuralEdges = useMemo(
    () => [...wikilinkEdges, ...tagSharedEdges],
    [wikilinkEdges, tagSharedEdges],
  );

  // --- Layout: base positions (UMAP or dagre), then the filter subgraph on top ----------
  const baseLayout = useMemo<Record<string, XY> | null>(() => {
    if (!hasNodes) return null;
    if (layout === "umap-semantic") {
      if (umapPositions) return placeMissingNodes(baseNodes, umapPositions, wikilinkEdges);
      if (!umapFailed) return null; // still loading: render nothing rather than a pile at (0,0)
      // UMAP unavailable on the server: fall back to the hierarchy layout.
    }
    return positionsOf(applyDagreLayout(baseNodes, wikilinkEdges));
  }, [hasNodes, layout, umapPositions, umapFailed, baseNodes, wikilinkEdges]);

  const filterIds = useMemo(() => {
    const primary = filterPrimaryIds(baseNodes, activeTags);
    return primary ? expandOneHop(primary, structuralEdges) : null;
  }, [baseNodes, activeTags, structuralEdges]);

  const positions = useMemo(() => {
    if (!baseLayout || !filterIds) return baseLayout;
    const sub = baseNodes.filter((n) => filterIds.has(n.id));
    // All three edge types shape the subgraph; wikilinks first so they win the
    // one-parent-per-node choice in applyDagreLayout.
    const subEdges = [...wikilinkEdges, ...semanticEdges, ...tagSharedEdges].filter(
      (e) => filterIds.has(e.source) && filterIds.has(e.target),
    );
    return { ...baseLayout, ...positionsOf(applyDagreLayout(sub, subEdges)) };
  }, [baseLayout, filterIds, baseNodes, wikilinkEdges, semanticEdges, tagSharedEdges]);

  // --- View: dimming / highlight / hidden, and the rendered edges -----------------------
  const focusIds = useMemo(
    () => focusNeighbourhood(focusNodeId, structuralEdges, semanticEdges),
    [focusNodeId, structuralEdges, semanticEdges],
  );

  const view = useMemo<ViewState>(
    () => ({
      chatHighlight: highlightedPages,
      focusId: focusNodeId,
      focusIds,
      filterIds,
      activeTags,
      overview: overviewMode,
    }),
    [highlightedPages, focusNodeId, focusIds, filterIds, activeTags, overviewMode],
  );

  const viewNodes = useMemo(() => {
    if (!positions) return NO_NODES;
    const laidOut = baseNodes.map((n) => ({ ...n, position: positions[n.id] ?? n.position }));
    return applyView(laidOut, view);
  }, [positions, baseNodes, view]);

  const edges = useMemo(
    () =>
      visibleEdges(
        { wikilink: wikilinkEdges, semantic: semanticEdges, tagShared: tagSharedEdges },
        edgeVis,
        viewNodes,
        view,
      ),
    [wikilinkEdges, semanticEdges, tagSharedEdges, edgeVis, viewNodes, view],
  );

  // --- Sync derived nodes into React Flow state (keeps node dragging working) -----------
  // A new `positions` object means a relayout: take the new positions and refit.
  // Otherwise only view flags changed: keep where the user dragged nodes to.
  const [nodes, setNodes, onNodesChange] = useNodesState<WikiFlowNode>([]);
  const lastPositions = useRef<Record<string, XY> | null>(null);
  const pendingFit = useRef(false);

  useEffect(() => {
    const relayout = lastPositions.current !== positions;
    lastPositions.current = positions;
    if (relayout && positions) pendingFit.current = true;
    setNodes((prev) => {
      const prevById = new Map(prev.map((n) => [n.id, n]));
      return viewNodes.map((n) => {
        const p = prevById.get(n.id);
        if (!p) return n;
        return {
          ...n,
          position: relayout ? n.position : p.position,
          measured: p.measured,
          selected: p.selected,
        };
      });
    });
  }, [viewNodes, positions, setNodes]);

  useEffect(() => {
    if (!pendingFit.current || !nodes.length) return;
    pendingFit.current = false;
    const ids = filterIds;
    requestAnimationFrame(() => {
      if (ids) {
        void fitView({ nodes: [...ids].map((id) => ({ id })), padding: 0.3, duration: 400 });
      } else {
        void fitView({ padding: 0.15, duration: 300 });
      }
    });
  }, [nodes, filterIds, fitView]);

  // --- focusPage (arriving from a lesson): fit to it, open its panel, report back -------
  // Declared after the layout fit so its fitView is queued last and wins on first load.
  const appliedFocus = useRef<string | null>(null);
  const hasRenderedNodes = nodes.length > 0;
  useEffect(() => {
    if (!focusPage) {
      appliedFocus.current = null;
      return;
    }
    if (appliedFocus.current === focusPage || !hasRenderedNodes) return;
    const node = baseNodes.find((n) => n.id === focusPage);
    appliedFocus.current = focusPage;
    if (!node) {
      // Unknown or private page (graph loaded, id absent): drop the request rather than
      // leave it pending, so it can't fire later on an unrelated graph update.
      onFocusApplied?.();
      return;
    }
    requestAnimationFrame(() => {
      void fitView({ nodes: [{ id: focusPage }], padding: 2, maxZoom: 1.2, duration: 400 });
    });
    onNodeSelect?.({ id: node.id, data: node.data });
    onFocusApplied?.();
  }, [focusPage, hasRenderedNodes, baseNodes, fitView, onNodeSelect, onFocusApplied]);

  // --- Handlers ------------------------------------------------------------------------
  const handleLoadSemantic = useCallback(async () => {
    setLoadingSemantic(true);
    try {
      await fetchSemanticEdges(0.65);
    } catch {
      // Toggle stays on with no edges; the next toggle retries.
    } finally {
      setLoadingSemantic(false);
    }
  }, [fetchSemanticEdges]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: WikiFlowNode) => {
      setFocusNodeId((prev) => (prev === node.id ? null : node.id));
      onNodeSelect?.({ id: node.id, data: node.data as WikiNodeData });
    },
    [onNodeSelect],
  );

  const handlePaneClick = useCallback(() => {
    setFocusNodeId(null);
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      e.preventDefault();
      setMenuOpen(false);
      menuBtnRef.current?.focus();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  const miniMapColor = useCallback((n: WikiFlowNode) => domainColor(n.data.domain[0]), []);

  return (
    <div className="graph-root">
      {/* Connection status */}
      <div className={`graph-status ${connected ? "graph-status--live" : "graph-status--offline"}`}>
        {connected ? "● live" : "○ connecting…"}
      </div>

      {/* Narrow screens: one button in place of the four control panels. */}
      <button
        ref={menuBtnRef}
        type="button"
        className="graph-menu-btn"
        aria-label="Graph controls"
        aria-expanded={menuOpen}
        aria-controls="graph-controls"
        onClick={() => setMenuOpen((o) => !o)}
      >
        ☰ Controls
      </button>

      <div id="graph-controls" className={`graph-controls${menuOpen ? " is-open" : ""}`}>
        <EdgeTogglePanel
          visibility={edgeVis}
          onChange={setEdgeVis}
          onLoadSemantic={handleLoadSemantic}
          loadingSemanticEdges={loadingSemantic}
        />

        <LayoutSwitcher
          current={layout}
          onChange={setLayout}
          loadingUmap={loadingUmap}
          umapUnavailable={layout === "umap-semantic" && umapFailed}
        />

        {/* Depth toggle — top-right */}
        <div className="graph-depth seg">
          <button onClick={() => setOverviewMode(true)} aria-pressed={overviewMode} className="seg-btn">
            Projects
          </button>
          <button onClick={() => setOverviewMode(false)} aria-pressed={!overviewMode} className="seg-btn">
            All
          </button>
        </div>

        <TagFilterPanel
          domains={domains}
          activeTags={activeTags}
          onChange={onActiveTagsChange}
          onBrief={onBrief}
        />
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        nodeTypes={NODE_TYPES}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.1}
        maxZoom={3}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} color="#222" gap={20} />
        <Controls className="graph-flow-controls" />
        <MiniMap nodeColor={miniMapColor} className="graph-minimap" />
      </ReactFlow>
    </div>
  );
}

export function WikiGraph(props: WikiGraphProps) {
  return (
    <ReactFlowProvider>
      <WikiGraphInner {...props} />
    </ReactFlowProvider>
  );
}
