import { useEffect, useState, useCallback, useRef } from "react";
import type { Node, Edge } from "@xyflow/react";
import type { WikiNodeData, WikiEdgeData } from "../types";

const WS_URL = "ws://localhost:8000/ws";

export function useWikiData() {
  const [baseNodes, setBaseNodes] = useState<Node<WikiNodeData>[]>([]);
  const [wikilinkEdges, setWikilinkEdges] = useState<Edge<WikiEdgeData>[]>([]);
  const [tagSharedEdges, setTagSharedEdges] = useState<Edge<WikiEdgeData>[]>([]);
  const [semanticEdges, setSemanticEdges] = useState<Edge<WikiEdgeData>[]>([]);
  const [umapPositions, setUmapPositions] = useState<Record<string, { x: number; y: number }> | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    function connect() {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        setTimeout(connect, 2000);
      };
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data as string) as {
          type: string;
          data: { nodes: Node<WikiNodeData>[]; edges: Edge<WikiEdgeData>[] };
        };
        if (msg.type === "graph_update") {
          const { nodes, edges } = msg.data;
          setBaseNodes(nodes);
          setWikilinkEdges(edges.filter((e) => e.data?.edgeType === "wikilink"));
          setTagSharedEdges(edges.filter((e) => e.data?.edgeType === "tag-shared"));
        }
      };
    }
    connect();
    return () => wsRef.current?.close();
  }, []);

  const fetchSemanticEdges = useCallback(async (threshold = 0.65) => {
    const res = await fetch(`/api/edges/semantic?threshold=${threshold}`);
    const data = (await res.json()) as Edge<WikiEdgeData>[];
    setSemanticEdges(data);
  }, []);

  const fetchUmapPositions = useCallback(async () => {
    const res = await fetch("/api/layout/umap", { method: "POST" });
    const data = (await res.json()) as Record<string, { x: number; y: number }>;
    setUmapPositions(data);
    return data;
  }, []);

  return {
    baseNodes,
    wikilinkEdges,
    tagSharedEdges,
    semanticEdges,
    fetchSemanticEdges,
    umapPositions,
    fetchUmapPositions,
    connected,
  };
}
