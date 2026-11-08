import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Edge, Node } from "@xyflow/react";
import type { GraphPayload, WikiEdgeData, WikiNodeData } from "../types";
import { tagSharedEdges as computeTagSharedEdges } from "../utils/tagEdges";
import { RELEASE_EVENT, apiFetch, wsProtocols } from "../utils/api";
import type { XY } from "../utils/layout";

const RECONNECT_MS = 2000;
/** On the atlas, how long after its first paint the full graph is fetched anyway. */
const LIVE_DELAY_MS = 1500;

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

/** GET /api/graph/atlas: the pages without summaries, wikilinks as index pairs. */
export interface AtlasPayload {
  nodes: { id: string; title: string; domain: string; typeTag: string; tags: string[] }[];
  links: ([number, number] | [number, number, string])[];
  domains: string[];
}

/** The atlas payload as a GraphPayload, with empty summaries until the full graph arrives. */
export function fromAtlas(a: AtlasPayload): GraphPayload {
  const nodes = a.nodes.map((n) => ({
    id: n.id,
    type: "wikiNode",
    position: { x: 0, y: 0 },
    data: {
      title: n.title,
      tags: n.tags,
      domain: [n.domain],
      typeTag: n.typeTag,
      summary: "",
      updated: "",
      path: `${n.domain}/${n.id}.md`,
      dimmed: false,
    },
  })) as Node<WikiNodeData>[];
  const edges = a.links.flatMap(([s, t, relationship]) => {
    const source = nodes[s]?.id;
    const target = nodes[t]?.id;
    if (!source || !target) return [];
    const data: WikiEdgeData = relationship ? { edgeType: "wikilink", relationship } : { edgeType: "wikilink" };
    return [{ id: `wl:${source}->${target}`, source, target, data }];
  });
  return { nodes, edges, domains: a.domains.filter((d) => d !== "private") };
}

const EMPTY: GraphPayload = { nodes: [], edges: [], domains: [] };
const NO_EDGES: Edge<WikiEdgeData>[] = [];

/**
 * `tagShared`: derive the tag-shared edges. Costly, so the map asks only when they're shown.
 * `live`: open the socket (the full graph, then its updates) now. Until then the map runs on the
 * atlas payload, about a tenth of the size, and the socket opens shortly after it lands anyway.
 */
export function useWikiData({ tagShared = true, live = true }: { tagShared?: boolean; live?: boolean } = {}) {
  const [graph, setGraph] = useState<GraphPayload>(EMPTY);
  /** The full graph has arrived over the socket; the atlas payload no longer applies. */
  const [full, setFull] = useState(false);
  const fullRef = useRef(false);
  const [atlasDone, setAtlasDone] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  const wantLive = live || timedOut;
  const [semanticEdges, setSemanticEdges] = useState<Edge<WikiEdgeData>[]>([]);
  const [umapPositions, setUmapPositions] = useState<Record<string, XY> | null>(null);
  /** Last UMAP request failed (e.g. the server answers 503 when umap-learn is missing). */
  const [umapFailed, setUmapFailed] = useState(false);
  const [connected, setConnected] = useState(false);
  const umapRequest = useRef<Promise<Record<string, XY> | null> | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch("/api/graph/atlas")
      .then((res) => (res.ok ? (res.json() as Promise<AtlasPayload>) : null))
      .catch(() => null)
      .then((atlas) => {
        if (cancelled) return;
        if (atlas && Array.isArray(atlas.nodes) && !fullRef.current) setGraph(fromAtlas(atlas));
        setAtlasDone(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // A failed atlas request (an older server) goes straight to the socket.
  useEffect(() => {
    if (!atlasDone || wantLive) return;
    const timer = setTimeout(() => setTimedOut(true), graph.nodes.length ? LIVE_DELAY_MS : 0);
    return () => clearTimeout(timer);
  }, [atlasDone, wantLive, graph.nodes.length]);

  useEffect(() => {
    if (!wantLive) return;
    let ws: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let disposed = false;

    function connect() {
      const sock = new WebSocket(wsUrl(window.location), wsProtocols());
      ws = sock;
      sock.onopen = () => setConnected(true);
      sock.onclose = () => {
        setConnected(false);
        if (!disposed) timer = setTimeout(connect, RECONNECT_MS);
      };
      sock.onmessage = (e) => {
        const payload = typeof e.data === "string" ? parseGraphMessage(e.data) : null;
        if (payload) {
          fullRef.current = true;
          setFull(true);
          setGraph(payload);
        }
      };
    }
    connect();

    // A new content release: drop the socket; its reconnect receives the new graph.
    const onRelease = () => ws?.close();
    window.addEventListener(RELEASE_EVENT, onRelease);

    return () => {
      disposed = true;
      window.removeEventListener(RELEASE_EVENT, onRelease);
      clearTimeout(timer);
      if (ws) {
        ws.onclose = null;
        ws.onmessage = null;
        ws.onopen = null;
        ws.close();
      }
    };
  }, [wantLive]);

  // ~42k edges on the current wiki; recomputed only when a new payload arrives.
  const tagSharedEdges = useMemo(
    () => (tagShared ? computeTagSharedEdges(graph.nodes, graph.domains) : NO_EDGES),
    [tagShared, graph.nodes, graph.domains],
  );

  const fetchSemanticEdges = useCallback(async (threshold = 0.65) => {
    const res = await apiFetch(`/api/edges/semantic?threshold=${threshold}`);
    if (!res.ok) throw new Error(`semantic edges: HTTP ${res.status}`);
    setSemanticEdges((await res.json()) as Edge<WikiEdgeData>[]);
  }, []);

  /** Fetch the UMAP projection once; concurrent and later calls share the result. */
  const loadUmapPositions = useCallback(() => {
    if (!umapRequest.current) {
      setUmapFailed(false);
      umapRequest.current = apiFetch("/api/layout/umap", { method: "POST" })
        .then((res) => (res.ok ? (res.json() as Promise<Record<string, XY>>) : null))
        .catch(() => null)
        .then((pos) => {
          if (pos) {
            setUmapPositions(pos);
          } else {
            setUmapFailed(true);
            umapRequest.current = null; // a later layout switch retries
          }
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
    umapFailed,
    loadUmapPositions,
    connected,
    full,
  };
}
