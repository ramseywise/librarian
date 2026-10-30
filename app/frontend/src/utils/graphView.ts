import type { CSSProperties } from "react";
import type { Edge, Node } from "@xyflow/react";
import type { EdgeVisibility, WikiEdgeData, WikiNodeData } from "../types";

/**
 * Pure view derivation for the wiki graph: which nodes are hidden / dimmed / highlighted
 * and which edges are rendered, given the current filter, chat highlight, click focus and
 * overview toggle. WikiGraph memoises these; keeping them pure keeps them testable.
 */

type GraphNode = Node<WikiNodeData>;
type GraphEdge = Edge<WikiEdgeData>;
type Link = { source: string; target: string };

/** Nodes whose primary domain or type tag is one of the active filter chips. */
export function filterPrimaryIds(nodes: GraphNode[], activeTags: Set<string>): Set<string> | null {
  if (activeTags.size === 0) return null;
  return new Set(
    nodes
      .filter((n) => n.data.domain.some((t) => activeTags.has(t)) || activeTags.has(n.data.typeTag))
      .map((n) => n.id),
  );
}

/** Primary filter matches plus their 1-hop neighbours over structural edges. */
export function expandOneHop(primary: Set<string>, edges: Link[]): Set<string> {
  const out = new Set(primary);
  for (const e of edges) {
    if (primary.has(e.source)) out.add(e.target);
    if (primary.has(e.target)) out.add(e.source);
  }
  return out;
}

/**
 * Neighbourhood of a clicked node: 2 hops over structural edges (wikilink + tag-shared)
 * plus 1 hop over semantic edges. Independent of the edge-visibility toggles.
 */
export function focusNeighbourhood(
  focusId: string | null,
  structural: Link[],
  semantic: Link[],
): Set<string> | null {
  if (!focusId) return null;
  const out = new Set<string>([focusId]);
  const firstHop = new Set<string>();
  for (const e of structural) {
    if (e.source === focusId) firstHop.add(e.target);
    if (e.target === focusId) firstHop.add(e.source);
  }
  for (const id of firstHop) out.add(id);
  for (const e of structural) {
    if (firstHop.has(e.source)) out.add(e.target);
    if (firstHop.has(e.target)) out.add(e.source);
  }
  for (const e of semantic) {
    if (e.source === focusId) out.add(e.target);
    if (e.target === focusId) out.add(e.source);
  }
  return out;
}

export interface ViewState {
  /** Pages referenced by the last chat answer (empty/undefined = none). */
  chatHighlight?: Set<string>;
  /** Clicked node, and its neighbourhood from focusNeighbourhood(); both null when unset. */
  focusId: string | null;
  focusIds: Set<string> | null;
  /** Filter subgraph (primary matches + 1 hop), or null when no chip is active. */
  filterIds: Set<string> | null;
  activeTags: Set<string>;
  /** "Projects" overview: everything but project pages is dimmed when no chip is active. */
  overview: boolean;
}

/**
 * Apply hidden / dimmed / highlighted flags. Precedence: chat highlight, then click
 * focus, then domain filter, then overview. Returns new node objects; inputs untouched.
 */
export function applyView(nodes: GraphNode[], v: ViewState): GraphNode[] {
  const hp = v.chatHighlight;
  const hasChat = hp != null && hp.size > 0;
  const fn = v.focusIds;
  const fm = v.filterIds;
  const at = v.activeTags;
  const hasTagFilter = at.size > 0;

  return nodes.map((n) => {
    const inChat = hasChat && hp.has(n.id);
    const inFocus = fn != null && fn.has(n.id);
    const inTagFilter =
      hasTagFilter && (n.data.domain.some((t) => at.has(t)) || at.has(n.data.typeTag));
    const hidden = hasChat ? false : fm ? !fm.has(n.id) : false;
    const highlighted = hasChat ? inChat : fn ? inFocus && !hidden : inTagFilter;
    const dimmed = hasChat
      ? !inChat
      : fn && !hidden
        ? !inFocus
        : v.overview && !hasTagFilter
          ? n.data.typeTag !== "project"
          : false;
    return { ...n, hidden, data: { ...n.data, highlighted, dimmed } };
  });
}

export const EDGE_STYLES: Record<string, CSSProperties> = {
  wikilink: { stroke: "#666", strokeWidth: 1 },
  semantic: { stroke: "#4a90d9", strokeWidth: 1, strokeDasharray: "4 3" },
  "tag-shared": { stroke: "#e8943a", strokeWidth: 1, strokeDasharray: "2 4" },
};

export interface EdgeSources {
  wikilink: GraphEdge[];
  semantic: GraphEdge[];
  tagShared: GraphEdge[];
}

/**
 * Edges to hand to React Flow. Edges that would be invisible are omitted rather than
 * marked `hidden`, so React Flow never holds the full tag-shared set (~42k edges).
 *
 * - Filter active: all three edge types inside the filter subgraph (toggles ignored).
 * - Otherwise: the toggled-on types.
 * - Chat highlight: only edges touching a highlighted page. Focus: only edges touching
 *   the focused node. Filter: only edges with both ends in the subgraph.
 * - Tag-shared edges are additionally pruned to those with at least one *emphasised*
 *   endpoint (highlighted, or not dimmed when nothing is highlighted). Tag-shared is
 *   near-clique dense (median degree ~120), so this is what keeps the overview usable.
 */
export function visibleEdges(
  src: EdgeSources,
  vis: EdgeVisibility,
  viewNodes: GraphNode[],
  v: ViewState,
): GraphEdge[] {
  const hp = v.chatHighlight;
  const hasChat = hp != null && hp.size > 0;
  const focusId = v.focusId;
  const fm = v.filterIds;
  const filtering = v.activeTags.size > 0;

  const candidates: GraphEdge[] = [
    ...(filtering || vis.wikilink ? src.wikilink : []),
    ...(filtering || vis.semantic ? src.semantic : []),
    ...(filtering || vis["tag-shared"] ? src.tagShared : []),
  ];

  const anyHighlighted = viewNodes.some((n) => n.data.highlighted);
  const emphasised = new Set<string>();
  const hidden = new Set<string>();
  for (const n of viewNodes) {
    if (n.hidden) hidden.add(n.id);
    else if (anyHighlighted ? n.data.highlighted : !n.data.dimmed) emphasised.add(n.id);
  }

  const out: GraphEdge[] = [];
  for (const e of candidates) {
    if (hidden.has(e.source) || hidden.has(e.target)) continue;
    if (hasChat) {
      if (!hp.has(e.source) && !hp.has(e.target)) continue;
    } else if (focusId) {
      if (e.source !== focusId && e.target !== focusId) continue;
    } else if (fm) {
      if (!fm.has(e.source) || !fm.has(e.target)) continue;
    }
    const type = e.data?.edgeType ?? "wikilink";
    if (type === "tag-shared" && !emphasised.has(e.source) && !emphasised.has(e.target)) continue;
    out.push({ ...e, style: EDGE_STYLES[type], animated: type === "semantic" });
  }
  return out;
}
