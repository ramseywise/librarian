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
import { applyDagreLayout, declutter, placeMissingNodes, type XY } from "../utils/layout";
import {
  applyView,
  degreeOf,
  expandBridges,
  filterPrimaryIds,
  neighbours,
  renderIds as computeRenderIds,
  sampleIds,
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
    wikilink: true,
    semantic: false,
    "tag-shared": true,
  });
  const [layout, setLayout] = useState<LayoutMode>("umap-semantic");
  // Sample-first: render a seed and grow it by clicking; "All" renders every page.
  const [showAll, setShowAll] = useState(false);
  /** Pages revealed by clicks since the last reset; they stay rendered (sample mode). */
  const [revealed, setRevealed] = useState<Set<string>>(() => new Set());
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

  // Neighbourhoods expand over wikilinks plus semantic edges once loaded — never over
  // tag-shared edges, whose near-cliques pulled most of the graph into every click.
  const linkEdges = useMemo(() => [...wikilinkEdges, ...semanticEdges], [wikilinkEdges, semanticEdges]);
  const degree = useMemo(() => degreeOf(wikilinkEdges), [wikilinkEdges]);
  const sample = useMemo(() => sampleIds(baseNodes, degree), [baseNodes, degree]);

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
    return primary ? expandBridges(primary, linkEdges) : null;
  }, [baseNodes, activeTags, linkEdges]);

  // Semantic layout keeps its positions under a filter (fitView zooms to the subgraph);
  // Hierarchy re-runs dagre on the subgraph so it reads as its own tree.
  const positions = useMemo(() => {
    if (!baseLayout || !filterIds || layout !== "dagre") return baseLayout;
    const sub = baseNodes.filter((n) => filterIds.has(n.id));
    // Wikilinks first so they win the one-parent-per-node choice in applyDagreLayout.
    const subEdges = linkEdges.filter((e) => filterIds.has(e.source) && filterIds.has(e.target));
    return { ...baseLayout, ...positionsOf(applyDagreLayout(sub, subEdges)) };
  }, [baseLayout, filterIds, layout, baseNodes, linkEdges]);

  // A new filter is a new view: drop the click focus so its neighbourhood doesn't linger
  // beside (and dim) the filter subgraph.
  useEffect(() => {
    setFocusNodeId(null);
  }, [activeTags]);

  // --- View: what is rendered, dimming / highlight, and the rendered edges ---------------
  const focusIds = useMemo(
    () => (focusNodeId ? new Set([focusNodeId, ...neighbours(focusNodeId, linkEdges, degree)]) : null),
    [focusNodeId, linkEdges, degree],
  );

  const view = useMemo<ViewState>(
    () => ({
      chatHighlight: highlightedPages,
      focusId: focusNodeId,
      focusIds,
      filterIds,
      activeTags,
    }),
    [highlightedPages, focusNodeId, focusIds, filterIds, activeTags],
  );

  const rendered = useMemo(
    () => computeRenderIds(showAll, sample, revealed, view),
    [showAll, sample, revealed, view],
  );

  // UMAP positions overlap where pages are similar; spread just the rendered cards.
  // Dagre output never overlaps, so a dagre-laid-out filter subgraph is left alone.
  const placed = useMemo(() => {
    if (!positions || layout !== "umap-semantic") return positions;
    return { ...positions, ...declutter(positions, rendered ?? baseNodes.map((n) => n.id)) };
  }, [positions, layout, rendered, baseNodes]);

  const viewNodes = useMemo(() => {
    if (!placed) return NO_NODES;
    const laidOut = baseNodes
      .filter((n) => !rendered || rendered.has(n.id))
      .map((n) => ({ ...n, position: placed[n.id] ?? n.position }));
    return applyView(laidOut, view);
  }, [placed, baseNodes, rendered, view]);

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
  // A new `positions` object means a relayout: take the new positions and refit. A new
  // filter (or switching Sample/All) also refits, even when positions are unchanged. A new
  // `placed` (declutter re-ran because the rendered set changed) takes the new positions
  // without a refit, so revealed cards don't land on top of stale ones. Otherwise only
  // view flags changed: keep where the user dragged nodes to.
  const [nodes, setNodes, onNodesChange] = useNodesState<WikiFlowNode>([]);
  const lastPositions = useRef<Record<string, XY> | null>(null);
  const lastPlaced = useRef<Record<string, XY> | null>(null);
  const lastFrame = useRef<{ filterIds: Set<string> | null; showAll: boolean } | null>(null);
  const pendingFit = useRef(false);

  useEffect(() => {
    const relayout = lastPositions.current !== positions;
    lastPositions.current = positions;
    const reframe =
      lastFrame.current?.filterIds !== filterIds || lastFrame.current?.showAll !== showAll;
    lastFrame.current = { filterIds, showAll };
    if ((relayout || reframe) && positions) pendingFit.current = true;
    const moved = relayout || reframe || lastPlaced.current !== placed;
    lastPlaced.current = placed;
    setNodes((prev) => {
      const prevById = new Map(prev.map((n) => [n.id, n]));
      return viewNodes.map((n) => {
        const p = prevById.get(n.id);
        if (!p) return n;
        return {
          ...n,
          position: moved ? n.position : p.position,
          measured: p.measured,
          selected: p.selected,
        };
      });
    });
  }, [viewNodes, positions, placed, filterIds, showAll, setNodes]);

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
  // The page may be outside the sample: focusing it puts it (and its neighbours) into
  // the rendered set, and the fit waits until React Flow actually holds the node.
  const appliedFocus = useRef<string | null>(null);
  const pendingFocusFit = useRef<string | null>(null);
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
    setFocusNodeId(focusPage);
    pendingFocusFit.current = focusPage;
    onNodeSelect?.({ id: node.id, data: node.data });
    onFocusApplied?.();
  }, [focusPage, hasRenderedNodes, baseNodes, onNodeSelect, onFocusApplied]);

  useEffect(() => {
    const id = pendingFocusFit.current;
    if (!id || !nodes.some((n) => n.id === id)) return;
    pendingFocusFit.current = null;
    requestAnimationFrame(() => {
      void fitView({ nodes: [{ id }], padding: 2, maxZoom: 1.2, duration: 400 });
    });
  }, [nodes, fitView]);

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

  // Clicking a node focuses it and, in sample mode, keeps its neighbours on the canvas
  // so the graph can be walked outward click by click. Clicking it again unfocuses.
  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: WikiFlowNode) => {
      setFocusNodeId((prev) => (prev === node.id ? null : node.id));
      setRevealed((prev) => {
        const next = new Set(prev);
        next.add(node.id);
        for (const id of neighbours(node.id, linkEdges, degree)) next.add(id);
        return next.size === prev.size ? prev : next;
      });
      onNodeSelect?.({ id: node.id, data: node.data as WikiNodeData });
    },
    [onNodeSelect, linkEdges, degree],
  );

  const handleResetSample = useCallback(() => {
    setRevealed(new Set());
    setFocusNodeId(null);
    onNodeSelect?.(null);
  }, [onNodeSelect]);

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
      {/* Connection status, and how much of the wiki is on the canvas */}
      <div className={`graph-status ${connected ? "graph-status--live" : "graph-status--offline"}`}>
        {connected ? "● live" : "○ connecting…"}
        {hasNodes && (
          <span className="graph-status-count">
            {" "}· {nodes.length} of {baseNodes.length} pages
          </span>
        )}
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
          <button
            onClick={() => setShowAll(false)}
            aria-pressed={!showAll}
            className="seg-btn"
            title="Projects and each domain's best-linked pages; click a node to reveal its links"
          >
            Sample
          </button>
          <button
            onClick={() => setShowAll(true)}
            aria-pressed={showAll}
            className="seg-btn"
            title="Render every page (slower)"
          >
            All
          </button>
          {!showAll && revealed.size > 0 && (
            <button onClick={handleResetSample} className="seg-btn" title="Back to the default sample">
              Reset
            </button>
          )}
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
        onlyRenderVisibleElements
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
