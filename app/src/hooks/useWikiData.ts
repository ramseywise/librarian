import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Edge, Node } from "@xyflow/react";
import type { GraphPayload, WikiEdgeData, WikiNodeData } from "../types";
import {
  atlasPayloadSchema,
  graphSocketMessageSchema,
  semanticEdgesSchema,
  umapPositionsSchema,
  type AtlasPayload,
} from "../schemas/graph";
import { tagSharedEdges as computeTagSharedEdges } from "../utils/tagEdges";
import { RELEASE_EVENT, apiFetch, parseJson, wsProtocols } from "../utils/api";
import type { XY } from "../utils/layout";
import { errorText } from "./resource";

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
 * Parse a WebSocket message into a GraphPayload. The socket carries one message type,
 * `graph_update`, validated as a strict discriminated union: a message that is not JSON, names
 * another `type` or has the wrong shape yields null, and `onInvalid` hears why. Works with both
 * the new server shape (`{nodes, edges, domains}`, wikilink edges only) and the old one (no
 * `domains`, tag-shared edges inline): edges are always narrowed to wikilinks and tag-shared
 * edges are recomputed client-side.
 */
export function parseGraphMessage(raw: string, onInvalid?: (reason: string) => void): GraphPayload | null {
  let msg: unknown;
  try {
    msg = JSON.parse(raw);
  } catch {
    onInvalid?.("the message was not JSON");
    return null;
  }
  const parsed = graphSocketMessageSchema.safeParse(msg);
  if (!parsed.success) {
    onInvalid?.(parsed.error.issues[0]?.message ?? "unexpected message");
    return null;
  }
  const { nodes, edges, domains, areas } = parsed.data.data;
  return {
    nodes,
    edges: edges.filter((e) => e.data?.edgeType === "wikilink"),
    domains: domains ? domains.filter((d) => d !== "private") : deriveDomains(nodes),
    areas: areas ?? [],
  };
}

/** GET /api/graph/atlas: the pages without summaries, wikilinks as index pairs. */
export type { AtlasPayload };

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
  return { nodes, edges, domains: a.domains.filter((d) => d !== "private"), areas: a.areas ?? [] };
}

const EMPTY: GraphPayload = { nodes: [], edges: [], domains: [], areas: [] };
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
  const [atlasError, setAtlasError] = useState<string | null>(null);
  /** The socket closed, or sent something unreadable, before the full graph arrived. */
  const [socketError, setSocketError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
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
    setAtlasError(null);
    void apiFetch("/api/graph/atlas")
      .then((res) => (res.ok ? parseJson(res, atlasPayloadSchema) : Promise.reject(new Error(`HTTP ${res.status}`))))
      .then(
        (atlas) => atlas,
        (e: unknown) => {
          if (!cancelled) setAtlasError(errorText(e));
          return null;
        },
      )
      .then((atlas) => {
        if (cancelled) return;
        if (atlas && !fullRef.current) setGraph(fromAtlas(atlas));
        setAtlasDone(true);
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

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
        if (!fullRef.current) setSocketError("the live connection closed before the map arrived");
        if (!disposed) timer = setTimeout(connect, RECONNECT_MS);
      };
      sock.onmessage = (e) => {
        const payload =
          typeof e.data === "string"
            ? parseGraphMessage(e.data, (why) => {
                if (!fullRef.current) setSocketError(`unreadable map update (${why})`);
              })
            : null;
        if (payload) {
          fullRef.current = true;
          setFull(true);
          setSocketError(null);
          setAtlasError(null);
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
  }, [wantLive, attempt]);

  // ~42k edges on the current wiki; recomputed only when a new payload arrives.
  const tagSharedEdges = useMemo(
    () => (tagShared ? computeTagSharedEdges(graph.nodes, graph.domains) : NO_EDGES),
    [tagShared, graph.nodes, graph.domains],
  );

  const fetchSemanticEdges = useCallback(async (threshold = 0.65) => {
    const res = await apiFetch(`/api/edges/semantic?threshold=${threshold}`);
    if (!res.ok) throw new Error(`semantic edges: HTTP ${res.status}`);
    setSemanticEdges(await parseJson(res, semanticEdgesSchema));
  }, []);

  /** Fetch the UMAP projection once; concurrent and later calls share the result. */
  const loadUmapPositions = useCallback(() => {
    if (!umapRequest.current) {
      setUmapFailed(false);
      umapRequest.current = apiFetch("/api/layout/umap", { method: "POST" })
        .then((res) => (res.ok ? parseJson(res, umapPositionsSchema) : null))
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

  const hasGraph = graph.nodes.length > 0;
  // Nothing to draw and both routes in have failed: say why. With a map on screen a failed
  // refresh stays quiet, as the socket reconnects by itself.
  const error = hasGraph ? null : atlasError && socketError ? `${atlasError}; ${socketError}` : null;
  const retry = useCallback(() => {
    setAtlasError(null);
    setSocketError(null);
    setAtlasDone(false);
    setTimedOut(false);
    setAttempt((a) => a + 1);
  }, []);

  return {
    data: hasGraph ? graph : null,
    error,
    loading: !hasGraph && !error,
    retry,
    baseNodes: graph.nodes as Node<WikiNodeData>[],
    wikilinkEdges: graph.edges,
    domains: graph.domains,
    areas: graph.areas,
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
