import { useCallback, useEffect, useRef, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
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
}

export function WikiGraph({ highlightedPages, onNodeSelect }: WikiGraphProps) {
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
    wikilink: true,
    semantic: false,
    "tag-shared": false,
  });
  const [layout, setLayout] = useState<LayoutMode>("dagre");
  const [activeTags, setActiveTags] = useState<Set<string>>(new Set());
  const [loadingUmap, setLoadingUmap] = useState(false);
  const [loadingSemantic, setLoadingSemantic] = useState(false);
  const [umapPositions, setUmapPositions] = useState<Record<string, { x: number; y: number }> | null>(null);

  // Refs so layout effect can read current dimming state without being a dep
  const activeTagsRef = useRef(activeTags);
  const highlightedPagesRef = useRef(highlightedPages);
  activeTagsRef.current = activeTags;
  highlightedPagesRef.current = highlightedPages;

  const applyDimming = useCallback((newNodes: WikiFlowNode[]): WikiFlowNode[] => {
    const hp = highlightedPagesRef.current;
    const at = activeTagsRef.current;
    return newNodes.map((n) => ({
      ...n,
      data: {
        ...n.data,
        dimmed:
          hp && hp.size > 0
            ? !hp.has(n.id)
            : at.size > 0 && !n.data.domain.some((t: string) => at.has(t)),
      },
    }));
  }, []);

  // Recompute layout whenever base nodes or layout mode changes
  useEffect(() => {
    if (!baseNodes.length) return;

    async function applyLayout() {
      const visibleEdges = wikilinkEdges;
      if (layout === "dagre") {
        const laid = applyDagreLayout(baseNodes as Node[], visibleEdges as Edge[]);
        setNodes(applyDimming(laid as WikiFlowNode[]));
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
      }
    }

    applyLayout();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baseNodes, layout]);

  // Recompute visible edges whenever toggles or edge sets change
  useEffect(() => {
    const active: Edge<WikiEdgeData>[] = [];
    if (edgeVis.wikilink) active.push(...wikilinkEdges);
    if (edgeVis.semantic) active.push(...semanticEdges);
    if (edgeVis["tag-shared"]) active.push(...tagSharedEdges);

    const styled = active.map((e) => ({
      ...e,
      style: EDGE_STYLES[e.data?.edgeType ?? "wikilink"],
      animated: e.data?.edgeType === "semantic",
    }));
    setEdges(styled);
  }, [edgeVis, wikilinkEdges, semanticEdges, tagSharedEdges, setEdges]);

  // Re-apply dimming when filter/highlight state changes
  useEffect(() => {
    setNodes((prev) => (prev.length ? applyDimming(prev) : prev));
  }, [activeTags, highlightedPages, applyDimming]);

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
      onNodeSelect?.({ id: node.id, data: node.data as WikiNodeData });
    },
    [onNodeSelect]
  );

  const handlePaneClick = useCallback(() => {
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  const miniMapColor = useCallback((n: Node) => {
    const domain = (n.data as WikiFlowNode["data"]).domain[0] ?? "";
    const colors: Record<string, string> = {
      langgraph: "#4CAF50", rag: "#2196F3", adk: "#FF9800", mcp: "#9C27B0",
      memory: "#00BCD4", infra: "#607D8B", llm: "#E91E63",
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

      <TagFilterPanel activeTags={activeTags} onChange={setActiveTags} />

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
