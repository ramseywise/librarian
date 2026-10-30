import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Edge, Node } from "@xyflow/react";
import type { GraphPayload, WikiEdgeData, WikiNodeData } from "../types";
import { tagSharedEdges as computeTagSharedEdges } from "../utils/tagEdges";
import type { XY } from "../utils/layout";

const RECONNECT_MS = 2000;

/** WebSocket URL on the page's own origin; Vite proxies `/ws` to the API (ws: true). */
export function wsUrl(loc: Pick<Location, "protocol" | "host">): string {
  const proto = loc.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${loc.host}/ws`;
}

/** Domain list from nodes' primary directory, sorted, excluding `private`. */
export function deriveDomains(nodes: Pick<Node<WikiNodeData>, "data">[]): string[] {
  const set = new Set<string>();
  for (const n of nodes) {
    const d = n.data.domain[0];
    if (d && d !== "private") set.add(d);
  }
  return [...set].sort();
}

/**
 * Parse a `graph_update` WebSocket message into a GraphPayload. Works with both the
 * new server shape (`{nodes, edges, domains}`, wikilink edges only) and the old one
 * (no `domains`, tag-shared edges inline): edges are always narrowed to wikilinks and
 * tag-shared edges are recomputed client-side. Returns null for anything else.
 */
export function parseGraphMessage(raw: string): GraphPayload | null {
  let msg: unknown;
  try {
    msg = JSON.parse(raw);
  } catch {
    return null;
  }
  if (!msg || typeof msg !== "object") return null;
  const { type, data } = msg as { type?: unknown; data?: unknown };
  if (type !== "graph_update" || !data || typeof data !== "object") return null;
  const { nodes, edges, domains } = data as Partial<GraphPayload>;
  if (!Array.isArray(nodes) || !Array.isArray(edges)) return null;
  return {
    nodes,
    edges: edges.filter((e) => e.data?.edgeType === "wikilink"),
    domains: Array.isArray(domains) ? domains.filter((d) => d !== "private") : deriveDomains(nodes),
  };
}

const EMPTY: GraphPayload = { nodes: [], edges: [], domains: [] };

export function useWikiData() {
  const [graph, setGraph] = useState<GraphPayload>(EMPTY);
  const [semanticEdges, setSemanticEdges] = useState<Edge<WikiEdgeData>[]>([]);
  const [umapPositions, setUmapPositions] = useState<Record<string, XY> | null>(null);
  const [connected, setConnected] = useState(false);
  const umapRequest = useRef<Promise<Record<string, XY> | null> | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let disposed = false;

    function connect() {
      const sock = new WebSocket(wsUrl(window.location));
      ws = sock;
      sock.onopen = () => setConnected(true);
      sock.onclose = () => {
        setConnected(false);
        if (!disposed) timer = setTimeout(connect, RECONNECT_MS);
      };
      sock.onmessage = (e) => {
        const payload = typeof e.data === "string" ? parseGraphMessage(e.data) : null;
        if (payload) setGraph(payload);
      };
    }
    connect();

    return () => {
      disposed = true;
      clearTimeout(timer);
      if (ws) {
        ws.onclose = null;
        ws.onmessage = null;
        ws.onopen = null;
        ws.close();
      }
    };
  }, []);

  // ~42k edges on the current wiki; recomputed only when a new payload arrives.
  const tagSharedEdges = useMemo(
    () => computeTagSharedEdges(graph.nodes, graph.domains),
    [graph.nodes, graph.domains],
  );

  const fetchSemanticEdges = useCallback(async (threshold = 0.65) => {
    const res = await fetch(`/api/edges/semantic?threshold=${threshold}`);
    if (!res.ok) throw new Error(`semantic edges: HTTP ${res.status}`);
    setSemanticEdges((await res.json()) as Edge<WikiEdgeData>[]);
  }, []);

  /** Fetch the UMAP projection once; concurrent and later calls share the result. */
  const loadUmapPositions = useCallback(() => {
    if (!umapRequest.current) {
      umapRequest.current = fetch("/api/layout/umap", { method: "POST" })
        .then((res) => (res.ok ? (res.json() as Promise<Record<string, XY>>) : null))
        .catch(() => null)
        .then((pos) => {
          if (pos) setUmapPositions(pos);
          else umapRequest.current = null; // allow a retry
          return pos;
        });
    }
    return umapRequest.current;
  }, []);

  return {
    baseNodes: graph.nodes as Node<WikiNodeData>[],
    wikilinkEdges: graph.edges,
    domains: graph.domains,
    tagSharedEdges,
    semanticEdges,
    fetchSemanticEdges,
    umapPositions,
    loadUmapPositions,
    connected,
  };
}
