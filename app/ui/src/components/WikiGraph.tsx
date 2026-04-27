import { useCallback, useEffect, useRef, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { WikiNode, type WikiFlowNode } from "./WikiNode";
import { EdgeTogglePanel } from "./EdgeTogglePanel";
import { LayoutSwitcher } from "./LayoutSwitcher";
import { TagFilterPanel } from "./TagFilterPanel";
import { useWikiData } from "../hooks/useWikiData";
import { applyDagreLayout, applyUmapLayout } from "../utils/layout";
import type { EdgeVisibility, LayoutMode, SelectedNode, WikiEdgeData, WikiNodeData } from "../types";

const NODE_TYPES = { wikiNode: WikiNode };

const EDGE_STYLES: Record<string, React.CSSProperties> = {
  wikilink: { stroke: "#666", strokeWidth: 1 },
  semantic: { stroke: "#4a90d9", strokeWidth: 1, strokeDasharray: "4 3" },
  "tag-shared": { stroke: "#e8943a", strokeWidth: 1, strokeDasharray: "2 4" },
};

interface WikiGraphProps {
  highlightedPages?: Set<string>;
  onNodeSelect?: (node: SelectedNode | null) => void;
  onBrief?: (domain: string) => void;
  activeTags: Set<string>;
  onActiveTagsChange: (tags: Set<string>) => void;
}

function AutoFit({ version }: { version: number }) {
  const { fitView } = useReactFlow();
  useEffect(() => {
    if (version > 0) requestAnimationFrame(() => fitView({ padding: 0.15 }));
  }, [version, fitView]);
  return null;
}

function WikiGraphInner({ highlightedPages, onNodeSelect, onBrief, activeTags, onActiveTagsChange }: WikiGraphProps) {
  const {
    baseNodes,
    wikilinkEdges,
    tagSharedEdges,
    semanticEdges,
    fetchSemanticEdges,
    fetchUmapPositions,
    connected,
  } = useWikiData();

  const [nodes, setNodes, onNodesChange] = useNodesState<WikiFlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge<WikiEdgeData>>([]);

  const [edgeVis, setEdgeVis] = useState<EdgeVisibility>({
    wikilink: false,
    semantic: false,
    "tag-shared": true,
  });
  const [layout, setLayout] = useState<LayoutMode>("umap-semantic");
  const [overviewMode, setOverviewMode] = useState(true);
  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);
  const [loadingUmap, setLoadingUmap] = useState(false);
  const [loadingSemantic, setLoadingSemantic] = useState(false);
  const [umapPositions, setUmapPositions] = useState<Record<string, { x: number; y: number }> | null>(null);
  const [fitVersion, setFitVersion] = useState(0);

  // Refs so effects can read current state without stale closures
  const activeTagsRef = useRef(activeTags);
  const highlightedPagesRef = useRef(highlightedPages);
  const overviewModeRef = useRef(overviewMode);
  const focusNodeIdRef = useRef(focusNodeId);
  const focusNeighborIdsRef = useRef<Set<string> | null>(null);
  const filterMatchingIdsRef = useRef<Set<string> | null>(null);
  activeTagsRef.current = activeTags;
  highlightedPagesRef.current = highlightedPages;
  overviewModeRef.current = overviewMode;
  focusNodeIdRef.current = focusNodeId;

  const { fitView } = useReactFlow();

  // Compute neighbor IDs for focused node — uses all edge types regardless of toggles,
  // 2-hop via structural edges (wikilink + tag-shared) + 1-hop semantic for richer context
  useEffect(() => {
    if (!focusNodeId) {
      focusNeighborIdsRef.current = null;
      return;
    }
    const neighbors = new Set<string>([focusNodeId]);
    const structural = [...wikilinkEdges, ...tagSharedEdges];
    const firstHop = new Set<string>();
    for (const e of structural) {
      if (e.source === focusNodeId) { neighbors.add(e.target); firstHop.add(e.target); }
      if (e.target === focusNodeId) { neighbors.add(e.source); firstHop.add(e.source); }
    }
    for (const e of structural) {
      if (firstHop.has(e.source)) neighbors.add(e.target);
      if (firstHop.has(e.target)) neighbors.add(e.source);
    }
    for (const e of semanticEdges) {
      if (e.source === focusNodeId) neighbors.add(e.target);
      if (e.target === focusNodeId) neighbors.add(e.source);
    }
    focusNeighborIdsRef.current = neighbors;
  }, [focusNodeId, wikilinkEdges, tagSharedEdges, semanticEdges]);

  const applyDimming = useCallback((newNodes: WikiFlowNode[]): WikiFlowNode[] => {
    const hp = highlightedPagesRef.current;
    const at = activeTagsRef.current;
    const ov = overviewModeRef.current;
    const fn = focusNeighborIdsRef.current;
    const hasChatHighlights = hp != null && hp.size > 0;
    const hasFocus = fn != null;
    const hasTagFilter = at.size > 0;
    return newNodes.map((n) => {
      const inChatHighlight = hasChatHighlights && hp!.has(n.id);
      const inFocus = hasFocus && fn!.has(n.id);
      const inTagFilter = hasTagFilter && (n.data.domain.some((t: string) => at.has(t)) || at.has(n.data.typeTag));
      // Use expanded filter set (primary + neighbors) for visibility; domain match for highlight
      const fm = filterMatchingIdsRef.current;
      const inFilterExpanded = fm ? fm.has(n.id) : false;
      const hidden = hasChatHighlights ? false : fm ? !inFilterExpanded : false;
      return {
        ...n,
        hidden,
        data: {
          ...n.data,
          highlighted: hasChatHighlights ? inChatHighlight : hasFocus ? inFocus && !hidden : inTagFilter,
          dimmed: hasChatHighlights
            ? !inChatHighlight
            : hasFocus && !hidden
            ? !inFocus
            : ov && !hasTagFilter
            ? n.data.typeTag !== "project"
            : false,
        },
      };
    });
  }, []);

  // Recompute layout whenever base nodes or layout mode changes
  useEffect(() => {
    if (!baseNodes.length) return;

    async function applyLayout() {
      try {
        const visibleEdges = wikilinkEdges;
        if (layout === "dagre") {
          const laid = applyDagreLayout(baseNodes as Node[], visibleEdges as Edge[]);
          setNodes(applyDimming(laid as WikiFlowNode[]));
          setFitVersion((v) => v + 1);
        } else if (layout === "umap-semantic") {
          setLoadingUmap(true);
          const positions = umapPositions ?? await (async () => {
            const pos = await fetchUmapPositions();
            setUmapPositions(pos);
            return pos;
          })();
          setLoadingUmap(false);
          const laid = applyUmapLayout(baseNodes as Node[], positions);
          setNodes(applyDimming(laid as WikiFlowNode[]));
          setFitVersion((v) => v + 1);
        }
      } catch {
        setLoadingUmap(false);
      }
    }

    applyLayout();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baseNodes, layout]);

  // Recompute visible edges + apply chip/focus filtering
  useEffect(() => {
    const hp = highlightedPages;
    const fn = focusNodeId;
    const at = activeTags;
    const fm = filterMatchingIdsRef.current;

    // In filter mode, always show all 3 edge types within the subgraph
    const active: Edge<WikiEdgeData>[] = at.size > 0
      ? [...wikilinkEdges, ...semanticEdges, ...tagSharedEdges]
      : [
          ...(edgeVis.wikilink ? wikilinkEdges : []),
          ...(edgeVis.semantic ? semanticEdges : []),
          ...(edgeVis["tag-shared"] ? tagSharedEdges : []),
        ];

    const filteredNodeIds = fm;

    const styled = active.map((e) => ({
      ...e,
      style: EDGE_STYLES[e.data?.edgeType ?? "wikilink"],
      animated: e.data?.edgeType === "semantic",
      hidden: hp && hp.size > 0
        ? !hp.has(e.source) && !hp.has(e.target)
        : fn
        ? e.source !== fn && e.target !== fn
        : filteredNodeIds
        ? !filteredNodeIds.has(e.source) && !filteredNodeIds.has(e.target)
        : false,
    }));
    setEdges(styled);
  }, [edgeVis, wikilinkEdges, semanticEdges, tagSharedEdges, highlightedPages, activeTags, focusNodeId, baseNodes, setEdges]);

  // Re-apply dimming when highlight/focus/overview state changes (not activeTags — handled by filter layout)
  useEffect(() => {
    setNodes((prev) => (prev.length ? applyDimming(prev) : prev));
  }, [focusNodeId, highlightedPages, overviewMode, applyDimming]);

  // Filter layout: Dagre subgraph when chips active, restore full layout when cleared
  useEffect(() => {
    if (!baseNodes.length) return;
    const at = activeTags;

    if (at.size === 0) {
      filterMatchingIdsRef.current = null;
      if (layout === "umap-semantic" && umapPositions) {
        const laid = applyUmapLayout(baseNodes as Node[], umapPositions);
        setNodes(applyDimming(laid as WikiFlowNode[]));
      } else if (layout === "dagre") {
        const laid = applyDagreLayout(baseNodes as Node[], wikilinkEdges as Edge[]);
        setNodes(applyDimming(laid as WikiFlowNode[]));
      } else {
        setNodes((prev) => applyDimming(prev));
      }
      requestAnimationFrame(() => fitView({ padding: 0.15, duration: 300 }));
      return;
    }

    // Primary nodes: domain OR type tag match
    const primaryIds = new Set(
      baseNodes
        .filter(n => {
          const d = n.data as WikiNodeData;
          return d.domain.some((t: string) => at.has(t)) || at.has(d.typeTag);
        })
        .map(n => n.id as string)
    );
    // Expand to 1-hop neighbors via wikilinks + tag-shared for richer context
    const matchingIds = new Set(primaryIds);
    for (const e of [...wikilinkEdges, ...tagSharedEdges]) {
      if (primaryIds.has(e.source)) matchingIds.add(e.target);
      if (primaryIds.has(e.target)) matchingIds.add(e.source);
    }
    filterMatchingIdsRef.current = matchingIds;

    const matchingBaseNodes = baseNodes.filter(n => matchingIds.has(n.id as string)) as Node[];
    // Always use all 3 edge types within the subgraph for full context
    const subEdges = ([...wikilinkEdges, ...semanticEdges, ...tagSharedEdges] as Edge[])
      .filter(e => matchingIds.has(e.source) && matchingIds.has(e.target));

    const laidOut = applyDagreLayout(matchingBaseNodes, subEdges);
    const newPositions = Object.fromEntries(laidOut.map(n => [n.id, n.position]));

    setNodes((prev) =>
      applyDimming(
        prev.map(n => ({
          ...n,
          position: matchingIds.has(n.id) ? (newPositions[n.id] ?? n.position) : n.position,
        })) as WikiFlowNode[]
      )
    );
    requestAnimationFrame(() =>
      fitView({ nodes: Array.from(matchingIds).map(id => ({ id })), padding: 0.3, duration: 400 })
    );
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTags, baseNodes, layout, umapPositions, edgeVis, wikilinkEdges, semanticEdges, tagSharedEdges]);

  const handleLoadSemantic = useCallback(async () => {
    setLoadingSemantic(true);
    await fetchSemanticEdges(0.65);
    setLoadingSemantic(false);
  }, [fetchSemanticEdges]);

  const handleLayoutChange = useCallback(
    async (mode: LayoutMode) => {
      setLayout(mode);
      if (mode === "umap-semantic" && !umapPositions) {
        setLoadingUmap(true);
        const pos = await fetchUmapPositions();
        setUmapPositions(pos);
        setLoadingUmap(false);
      }
    },
    [umapPositions, fetchUmapPositions]
  );

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setFocusNodeId((prev) => (prev === node.id ? null : node.id));
      onNodeSelect?.({ id: node.id, data: node.data as WikiNodeData });
    },
    [onNodeSelect]
  );

  const handlePaneClick = useCallback(() => {
    setFocusNodeId(null);
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  const miniMapColor = useCallback((n: Node) => {
    const domain = (n.data as WikiFlowNode["data"]).domain[0] ?? "";
    const colors: Record<string, string> = {
      rag: "#2196F3", langgraph: "#4CAF50", adk: "#FF9800", infra: "#607D8B",
      patterns: "#E91E63", eval: "#FFEB3B", "deep-agents": "#3F51B5",
      memory: "#00BCD4", mcp: "#9C27B0", meta: "#795548", projects: "#009688",
    };
    return colors[domain] ?? "#555";
  }, []);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      {/* Connection status */}
      <div style={{
        position: "absolute", top: 12, left: "50%", transform: "translateX(-50%)",
        zIndex: 10, fontSize: 11, color: connected ? "#4CAF50" : "#F44336",
        background: "#1c1c1c", padding: "3px 10px", borderRadius: 12, border: "1px solid #333",
      }}>
        {connected ? "● live" : "○ connecting…"}
      </div>

      <EdgeTogglePanel
        visibility={edgeVis}
        onChange={setEdgeVis}
        onLoadSemantic={handleLoadSemantic}
        loadingSemanticEdges={loadingSemantic}
      />

      <LayoutSwitcher current={layout} onChange={handleLayoutChange} loadingUmap={loadingUmap} />

      {/* Depth toggle — top-right */}
      <div style={depthToggleStyle}>
        <button
          onClick={() => setOverviewMode(true)}
          style={{ ...depthBtnStyle, ...(overviewMode ? depthBtnActiveStyle : {}) }}
        >
          Projects
        </button>
        <button
          onClick={() => setOverviewMode(false)}
          style={{ ...depthBtnStyle, ...(!overviewMode ? depthBtnActiveStyle : {}) }}
        >
          All
        </button>
      </div>

      <TagFilterPanel activeTags={activeTags} onChange={onActiveTagsChange} onBrief={onBrief} />

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={NODE_TYPES}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.1}
        maxZoom={3}
        proOptions={{ hideAttribution: true }}
      >
        <AutoFit version={fitVersion} />
        <Background variant={BackgroundVariant.Dots} color="#222" gap={20} />
        <Controls style={{ background: "#1c1c1c", border: "1px solid #333" }} />
        <MiniMap
          nodeColor={miniMapColor}
          style={{ background: "#111", border: "1px solid #333" }}
        />
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

const depthToggleStyle: React.CSSProperties = {
  position: "absolute",
  top: 90,
  right: 12,
  zIndex: 10,
  display: "flex",
  background: "#1c1c1c",
  border: "1px solid #333",
  borderRadius: 8,
  overflow: "hidden",
};

const depthBtnStyle: React.CSSProperties = {
  padding: "5px 14px",
  fontSize: 11,
  cursor: "pointer",
  background: "transparent",
  border: "none",
  color: "#555",
};

const depthBtnActiveStyle: React.CSSProperties = {
  background: "#2a2a2a",
  color: "#e0e0e0",
};
