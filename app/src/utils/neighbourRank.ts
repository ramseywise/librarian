/**
 * Which pages a page's level holds, and why: a personalised PageRank from the open page over every
 * kind of connection that is switched on, each kind with its own weight.
 *
 * Links and similar meaning (each page's nearest pages by embedding) are page-to-page edges. Modules, notes and glossary terms are group nodes: a page passes
 * score to the groups it is in and a group shares it among its pages, so a module of 50 pages costs
 * 50 edges, not 1,225, and a term mentioned on many pages spreads thin by itself (a rare term counts
 * for more). Course order joins each note's group to the next note's, so the notes either side of
 * a page's note are near it.
 *
 * A page reached by several kinds of evidence outranks one that is only one link away, and the
 * ranking is recomputed whenever the filters or the switched-on kinds change.
 *
 * This ranks the map's neighbours only. It is not retrieval ranking (`graph_expansion.py`), which
 * has its own eval gate.
 */

type Link = { source: string; target: string; data?: { relationship?: string } };

export type RankKind = "typed" | "link" | "module" | "note" | "term" | "course" | "similar";

/** Starting weights: how much of a page's score each kind of connection carries on. */
export const RANK_WEIGHTS: Record<RankKind, number> = {
  typed: 1,
  link: 0.7,
  course: 0.8,
  note: 0.6,
  module: 0.5,
  term: 0.4,
  similar: 0.3,
};

/** `related` says only that two pages relate, like an untyped link. */
const WEAK = new Set(["related"]);

/** A term on more pages than this says little about any two of them, and is left out. */
export const COMMON_TERM = 80;

export interface RankGroup {
  /** Facet id: `module:…`, `note:…` or `term:…`. */
  id: string;
  kind: "module" | "note" | "term";
  pages: string[];
}

export interface RankInput {
  links: Link[];
  /** Pages alike by embedding. */
  similar?: Link[];
  groups: RankGroup[];
  /** Note group ids in reading order, one list per module: the course order. */
  readingOrder: string[][];
  /** Kinds switched on and their weights; a kind left out counts for nothing. */
  weights: Partial<Record<RankKind, number>>;
}

interface Graph {
  /** Node → [neighbour, weight] for every node, page or group. */
  out: Map<string, [string, number][]>;
  groups: Set<string>;
}

const RESTART = 0.25;
const ITERATIONS = 30;

/** The weighted graph a ranking walks. Build it once per input; rank from as many pages as you like. */
export function rankGraph({ links, similar = [], groups, readingOrder, weights }: RankInput): Graph {
  // Per node, per kind, the neighbours; each kind's share is then split among its neighbours.
  const byKind = new Map<string, Map<RankKind, string[]>>();
  const add = (from: string, kind: RankKind, to: string) => {
    if (!weights[kind]) return;
    let kinds = byKind.get(from);
    if (!kinds) byKind.set(from, (kinds = new Map()));
    const list = kinds.get(kind);
    if (list) list.push(to);
    else kinds.set(kind, [to]);
  };
  for (const e of links) {
    if (e.source === e.target) continue;
    const kind: RankKind = e.data?.relationship && !WEAK.has(e.data.relationship) ? "typed" : "link";
    add(e.source, kind, e.target);
    add(e.target, kind, e.source);
  }
  for (const e of similar) {
    if (e.source === e.target) continue;
    add(e.source, "similar", e.target);
    add(e.target, "similar", e.source);
  }
  const groupIds = new Set<string>();
  for (const g of groups) {
    if (!weights[g.kind] || g.pages.length < 2) continue;
    if (g.kind === "term" && g.pages.length > COMMON_TERM) continue;
    groupIds.add(g.id);
    for (const p of g.pages) {
      add(p, g.kind, g.id);
      // Inside a group every page gets the same share; the kind is only the label.
      add(g.id, g.kind, p);
    }
  }
  if (weights.course) {
    for (const notes of readingOrder) {
      for (let i = 1; i < notes.length; i++) {
        if (!groupIds.has(notes[i - 1]) || !groupIds.has(notes[i])) continue;
        add(notes[i - 1], "course", notes[i]);
        add(notes[i], "course", notes[i - 1]);
      }
    }
  }
  const out = new Map<string, [string, number][]>();
  for (const [node, kinds] of byKind) {
    const total = [...kinds.keys()].reduce((s, k) => s + (weights[k] ?? 0), 0);
    const edges: [string, number][] = [];
    for (const [kind, list] of kinds) {
      const share = (weights[kind] ?? 0) / total / list.length;
      for (const to of list) edges.push([to, share]);
    }
    out.set(node, edges);
  }
  return { out, groups: groupIds };
}

/** Every page's score from `anchor`; pages it cannot reach are absent. The anchor itself is left out. */
export function rankFrom(anchor: string, graph: Graph): Map<string, number> {
  let r = new Map<string, number>([[anchor, 1]]);
  for (let i = 0; i < ITERATIONS; i++) {
    const next = new Map<string, number>([[anchor, RESTART]]);
    for (const [node, score] of r) {
      const edges = graph.out.get(node);
      // A dead end hands its score back to the anchor, so it is not lost.
      if (!edges?.length) {
        next.set(anchor, (next.get(anchor) ?? 0) + (1 - RESTART) * score);
        continue;
      }
      for (const [to, w] of edges) next.set(to, (next.get(to) ?? 0) + (1 - RESTART) * score * w);
    }
    r = next;
  }
  const pages = new Map<string, number>();
  for (const [id, s] of r) if (id !== anchor && !graph.groups.has(id) && s > 1e-9) pages.set(id, s);
  return pages;
}

export interface RankedNeighbourhood {
  ids: Set<string>;
  /** Steps from the anchor to the furthest page held; a shared group is one step. */
  hops: number;
  /** Pages the anchor reaches at all. */
  total: number;
  /** Score of each page held, the anchor excluded. */
  scores: Map<string, number>;
}

/** The anchor and its `cap - 1` best-scored pages. */
export function rankedNeighbourhood(anchor: string, graph: Graph, cap: number): RankedNeighbourhood {
  const scores = rankFrom(anchor, graph);
  const top = [...scores].sort(([a, x], [b, y]) => y - x || a.localeCompare(b)).slice(0, Math.max(0, cap - 1));
  const ids = new Set([anchor, ...top.map(([id]) => id)]);
  return { ids, hops: stepsTo(anchor, ids, graph), total: scores.size + 1, scores: new Map(top) };
}

/** Breadth-first from the anchor, counting page-to-page steps; a step through a group is one. */
function stepsTo(anchor: string, ids: Set<string>, graph: Graph): number {
  const seen = new Set([anchor]);
  let frontier = [anchor];
  let step = 0;
  let found = 1;
  let furthest = 0;
  while (frontier.length && found < ids.size) {
    step++;
    const next: string[] = [];
    const visit = (to: string) => {
      if (seen.has(to)) return;
      seen.add(to);
      if (graph.groups.has(to)) {
        // Through the group to its pages in the same step; the next note's group is a step on.
        for (const [p] of graph.out.get(to) ?? []) {
          if (!graph.groups.has(p)) visit(p);
          else if (!seen.has(p)) next.push(p);
        }
        return;
      }
      next.push(to);
      if (ids.has(to)) {
        found++;
        furthest = step;
      }
    };
    for (const from of frontier) for (const [to] of graph.out.get(from) ?? []) visit(to);
    frontier = next;
  }
  return furthest;
}

/** What ties `other` to `anchor`, in a few words: the card's "Here because". */
export function whyLinked(
  anchor: string,
  other: string,
  { links, similar = [], groups, readingOrder }: Pick<RankInput, "links" | "similar" | "groups" | "readingOrder">,
  termLabel: (id: string) => string = (id) => id,
): string[] {
  const out: string[] = [];
  const link = links.find((e) => (e.source === anchor && e.target === other) || (e.source === other && e.target === anchor));
  if (link) out.push(link.data?.relationship && !WEAK.has(link.data.relationship) ? link.data.relationship.replace(/-/g, " ") : "linked");
  if (similar.some((e) => (e.source === anchor && e.target === other) || (e.source === other && e.target === anchor))) out.push("similar meaning");
  const shared = groups.filter((g) => g.pages.includes(anchor) && g.pages.includes(other));
  if (shared.some((g) => g.kind === "note")) out.push("same lesson");
  else if (shared.some((g) => g.kind === "module")) out.push("same module");
  const notesOf = (p: string) => new Set(groups.filter((g) => g.kind === "note" && g.pages.includes(p)).map((g) => g.id));
  const mine = notesOf(anchor);
  const theirs = notesOf(other);
  for (const order of readingOrder) {
    const at = (set: Set<string>) => order.findIndex((n) => set.has(n));
    const a = at(mine);
    const b = at(theirs);
    if (a < 0 || b < 0 || a === b) continue;
    if (Math.abs(a - b) === 1) {
      out.push(b < a ? "lesson before" : "lesson after");
      break;
    }
  }
  const terms = shared.filter((g) => g.kind === "term" && g.pages.length <= COMMON_TERM);
  if (terms.length === 1) out.push(`shares ${termLabel(terms[0].id.slice(5))}`);
  else if (terms.length > 1) out.push(`${terms.length} shared terms`);
  return out;
}
