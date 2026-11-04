import type { CSSProperties } from "react";
import type { Edge, Node } from "@xyflow/react";
import type { Curriculum, EdgeVisibility, Facets, WikiEdgeData, WikiNodeData } from "../types";

/**
 * Pure view derivation for the wiki graph: which nodes are rendered, which are dimmed /
 * highlighted, and which edges are drawn, given the current filter, chat highlight, click
 * focus and sample/all toggle. WikiGraph memoises these; keeping them pure keeps them
 * testable.
 *
 * The graph is sample-first: by default React Flow only receives a small seed (project
 * pages plus the best-linked pages of each course and directory), and clicking a node reveals its direct
 * neighbours. Rendering all ~900 nodes is an explicit opt-in ("All"). Neighbourhoods and
 * filters expand over wikilink (and loaded semantic) edges only — never tag-shared ones,
 * which form near-cliques (median degree ~120) and pulled most of the graph into every
 * filter and click.
 */

type GraphNode = Node<WikiNodeData>;
type GraphEdge = Edge<WikiEdgeData>;
type Link = { source: string; target: string; data?: { relationship?: string } };

/** Pages kept per domain in the default sample, ranked by wikilink degree. */
export const SAMPLE_PER_DOMAIN = 3;
/** Pages kept per course, and per directory of pages no lesson links, once the curriculum is in. */
export const SAMPLE_PER_COURSE = 5;
export const SAMPLE_PER_BEYOND = 2;
/** Most neighbours a single click reveals; the best-linked ones win. */
export const REVEAL_CAP = 40;

export function degreeOf(edges: Link[]): Map<string, number> {
  const deg = new Map<string, number>();
  for (const e of edges) {
    deg.set(e.source, (deg.get(e.source) ?? 0) + 1);
    deg.set(e.target, (deg.get(e.target) ?? 0) + 1);
  }
  return deg;
}

/** Default sample: every project page plus the `perDomain` best-linked pages of each domain. */
export function sampleIds(
  nodes: GraphNode[],
  degree: Map<string, number>,
  perDomain = SAMPLE_PER_DOMAIN,
): Set<string> {
  const out = new Set<string>();
  const byDomain = new Map<string, GraphNode[]>();
  for (const n of nodes) {
    if (n.data.typeTag === "project") out.add(n.id);
    const d = n.data.domain[0] ?? "";
    const list = byDomain.get(d);
    if (list) list.push(n);
    else byDomain.set(d, [n]);
  }
  for (const list of byDomain.values()) {
    list
      .sort((a, b) => (degree.get(b.id) ?? 0) - (degree.get(a.id) ?? 0) || a.id.localeCompare(b.id))
      .slice(0, perDomain)
      .forEach((n) => out.add(n.id));
  }
  return out;
}

/**
 * The sample once the curriculum is in, so the map opens matching the panel: every project
 * page, the best-linked pages of each course (by main course, the one that colours them), and
 * a few from each directory of unlinked pages.
 */
export function curriculumSampleIds(
  nodes: GraphNode[],
  degree: Map<string, number>,
  c: Curriculum,
): Set<string> {
  const present = new Set(nodes.map((n) => n.id));
  const out = new Set(nodes.filter((n) => n.data.typeTag === "project").map((n) => n.id));
  const takeBest = (ids: string[], count: number) =>
    ids
      .filter((id) => present.has(id))
      .sort((a, b) => (degree.get(b) ?? 0) - (degree.get(a) ?? 0) || a.localeCompare(b))
      .slice(0, count)
      .forEach((id) => out.add(id));
  for (const course of c.courses) {
    takeBest(
      course.pageIds.filter((id) => c.primaryCourse[id] === course.id),
      SAMPLE_PER_COURSE,
    );
  }
  for (const b of c.beyond) takeBest(b.pageIds, SAMPLE_PER_BEYOND);
  return out;
}

/** Does an active filter select this node? By directory, type tag, or curriculum facet. */
function matchesFilter(n: GraphNode, activeTags: Set<string>, facets?: Facets): boolean {
  if (n.data.domain.some((t) => activeTags.has(t)) || activeTags.has(n.data.typeTag)) return true;
  if (facets) for (const t of activeTags) if (facets.get(t)?.has(n.id)) return true;
  return false;
}

/** Nodes selected by the active filters. */
export function filterPrimaryIds(
  nodes: GraphNode[],
  activeTags: Set<string>,
  facets?: Facets,
): Set<string> | null {
  if (activeTags.size === 0) return null;
  return new Set(nodes.filter((n) => matchesFilter(n, activeTags, facets)).map((n) => n.id));
}

/**
 * Primary filter matches plus the outside pages that link to at least `minLinks` of them
 * ("bridges"). A plain one-hop expansion roughly doubles most domains with pages that
 * touch the domain once; requiring two links keeps the cross-domain structure.
 */
export function expandBridges(primary: Set<string>, edges: Link[], minLinks = 2): Set<string> {
  const out = new Set(primary);
  const links = new Map<string, number>();
  const bump = (id: string) => links.set(id, (links.get(id) ?? 0) + 1);
  for (const e of edges) {
    const s = primary.has(e.source);
    const t = primary.has(e.target);
    if (s && !t) bump(e.target);
    if (t && !s) bump(e.source);
  }
  for (const [id, n] of links) if (n >= minLinks) out.add(id);
  return out;
}

/**
 * Direct neighbours of `id` over the given edges (wikilinks, plus semantic once loaded),
 * capped at `cap`: typed See Also links first, then the better-linked pages.
 */
export function neighbours(
  id: string,
  edges: Link[],
  degree: Map<string, number>,
  cap = REVEAL_CAP,
): string[] {
  const typed = new Map<string, boolean>();
  for (const e of edges) {
    const other = e.source === id ? e.target : e.target === id ? e.source : null;
    if (!other || other === id) continue;
    typed.set(other, (typed.get(other) ?? false) || !!e.data?.relationship);
  }
  return [...typed.keys()]
    .sort(
      (a, b) =>
        Number(typed.get(b)) - Number(typed.get(a)) ||
        (degree.get(b) ?? 0) - (degree.get(a) ?? 0) ||
        a.localeCompare(b),
    )
    .slice(0, cap);
}

export interface ViewState {
  /** Pages referenced by the last chat answer (empty/undefined = none). */
  chatHighlight?: Set<string>;
  /** Clicked node, and it plus its neighbours(); both null when unset. */
  focusId: string | null;
  focusIds: Set<string> | null;
  /** Filter subgraph (primary matches + bridges), or null when no chip is active. */
  filterIds: Set<string> | null;
  activeTags: Set<string>;
  /** Curriculum filter ids and their pages, once loaded. */
  facets?: Facets;
}

/**
 * Ids handed to React Flow, or null for every node ("All"). Filter mode starts from the
 * filter subgraph, otherwise from the sample plus everything revealed by clicks; the
 * focused neighbourhood and chat-cited pages are always added so they can be shown.
 */
export function renderIds(
  showAll: boolean,
  sample: Set<string>,
  revealed: Set<string>,
  v: Pick<ViewState, "filterIds" | "focusIds" | "chatHighlight">,
): Set<string> | null {
  if (showAll) return null;
  const out = new Set(v.filterIds ?? [...sample, ...revealed]);
  for (const id of v.focusIds ?? []) out.add(id);
  for (const id of v.chatHighlight ?? []) out.add(id);
  return out;
}

/**
 * Apply dimmed / highlighted flags to the rendered nodes. Precedence: chat highlight,
 * then click focus, then domain filter. Returns new node objects; inputs untouched.
 * Only chat hits are `enlarged`: a focus neighbourhood or a whole domain drawn at 1.5x
 * would spill past the layout box and bury its neighbours.
 */
export function applyView(nodes: GraphNode[], v: ViewState): GraphNode[] {
  const hp = v.chatHighlight;
  // Only ids that exist count: a citation of an unknown or private page must not dim
  // the whole graph with nothing highlighted.
  const hasChat = hp != null && nodes.some((n) => hp.has(n.id));
  const fn = v.focusIds;
  const at = v.activeTags;
  const hasTagFilter = at.size > 0;

  return nodes.map((n) => {
    const inChat = hasChat && hp.has(n.id);
    const inFocus = fn != null && fn.has(n.id);
    const inTagFilter = hasTagFilter && matchesFilter(n, at, v.facets);
    const highlighted = hasChat ? inChat : fn ? inFocus : inTagFilter;
    const dimmed = hasChat ? !inChat : fn ? !inFocus : false;
    return { ...n, data: { ...n.data, highlighted, dimmed, enlarged: inChat } };
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
 * marked `hidden`, so React Flow never holds the full tag-shared set (~42k edges). Only
 * edges with both endpoints among `viewNodes` (the rendered nodes) are considered.
 *
 * - The toggled-on types only. Tag-shared is off by default: it was ~19k of the edges under
 *   a large filter and froze the tab for over a second.
 * - Chat highlight: only edges touching a highlighted page. Focus: only edges touching
 *   the focused node. Filter: only edges with both ends in the subgraph.
 * - Tag-shared edges are additionally pruned to those with at least one *emphasised*
 *   endpoint: a highlighted node, or else a non-dimmed node when some are dimmed. With
 *   nothing highlighted or dimmed (no filter/focus/chat) none are emphasised, so no
 *   tag-shared edges render. Tag-shared is near-clique dense (median degree ~120):
 *   rendering all ~42k froze the tab for ~50 s.
 */
export function visibleEdges(
  src: EdgeSources,
  vis: EdgeVisibility,
  viewNodes: GraphNode[],
  v: ViewState,
): GraphEdge[] {
  const hp = v.chatHighlight;
  const hasChat = hp != null && viewNodes.some((n) => hp.has(n.id)); // as in applyView
  const focusId = v.focusId;
  const fm = v.filterIds;

  const candidates: GraphEdge[] = [
    ...(vis.wikilink ? src.wikilink : []),
    ...(vis.semantic ? src.semantic : []),
    ...(vis["tag-shared"] ? src.tagShared : []),
  ];

  const anyHighlighted = viewNodes.some((n) => n.data.highlighted);
  const anyDimmed = viewNodes.some((n) => n.data.dimmed);
  const emphasised = new Set<string>();
  const present = new Set<string>();
  for (const n of viewNodes) {
    present.add(n.id);
    if (anyHighlighted ? n.data.highlighted : anyDimmed && !n.data.dimmed) emphasised.add(n.id);
  }

  const out: GraphEdge[] = [];
  for (const e of candidates) {
    if (!present.has(e.source) || !present.has(e.target)) continue;
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
