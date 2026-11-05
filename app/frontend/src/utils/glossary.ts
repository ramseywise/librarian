import type { Edge, Node } from "@xyflow/react";
import type { Glossary, GlossaryTerm, WikiEdgeData, WikiNodeData } from "../types";
import type { XY } from "./layout";

/**
 * The glossary as a layer over a focused view, and glossary-aware search. Terms are not pages:
 * they carry a `term:` id no page can have (page ids are file stems) and never reach the atlas.
 */

type GraphNode = Node<WikiNodeData>;

const TERM_PREFIX = "term:";
export const termNodeId = (id: string) => `${TERM_PREFIX}${id}`;
export const isTermNodeId = (id: string) => id.startsWith(TERM_PREFIX);
export const termIdOf = (nodeId: string) => nodeId.slice(TERM_PREFIX.length);

/** More would be a second graph over the first. */
export const MAX_TERMS = 20;
/** A term on most of the view says nothing about any of it. */
const UNDISCRIMINATING = 0.8;
const MIN_PAGES_FOR_SHARE_RULE = 10;

export interface TermLayer {
  nodes: GraphNode[];
  edges: Edge<WikiEdgeData>[];
}

export const NO_TERMS: TermLayer = { nodes: [], edges: [] };

/** How far a pill grows to stay legible when zoomed out; its slot allows for the growth. */
export const MAX_TERM_SCALE = 1.6;
/** Term pill's slot in the rows; a pill is at most 225 wide before it grows. */
const TERM_SLOT = { w: 370, h: 78 };
/** Clear of the cards, whose full height the layout box underestimates. */
const TERM_MARGIN = 150;

/**
 * Terms for the pages on the canvas, in rows above and below them: they read as a layer, can't
 * land on a card, and don't widen the view (a semantic layout is wider than it is tall, so width
 * is what limits the zoom). The anchor page's own terms come first, then the most mentioned.
 * Each goes on the side its pages lie on, while that side has room, and left to right in the
 * order of where its pages are.
 */
export function termLayer(
  pages: GraphNode[],
  glossary: Glossary,
  opts: { anchorId?: string | null; focusIds?: Set<string> | null; focusId?: string | null; max?: number } = {},
): TermLayer {
  if (!pages.length) return NO_TERMS;
  const byId = new Map(pages.map((p) => [p.id, p]));
  const anchor = opts.anchorId;

  const ranked = glossary.terms
    .map((term) => {
      const here = (glossary.mentions[term.id] ?? []).filter((id) => byId.has(id));
      return { term, here, onAnchor: !!anchor && here.includes(anchor) };
    })
    .filter(({ here, onAnchor }) => {
      if (onAnchor) return true;
      if (here.length < 2) return false;
      return pages.length < MIN_PAGES_FOR_SHARE_RULE || here.length / pages.length <= UNDISCRIMINATING;
    })
    .sort(
      (a, b) =>
        Number(b.onAnchor) - Number(a.onAnchor) ||
        b.here.length - a.here.length ||
        a.term.id.localeCompare(b.term.id),
    )
    .slice(0, opts.max ?? MAX_TERMS);
  if (!ranked.length) return NO_TERMS;

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const p of pages) {
    minX = Math.min(minX, p.position.x);
    minY = Math.min(minY, p.position.y);
    maxX = Math.max(maxX, p.position.x + 190);
    maxY = Math.max(maxY, p.position.y + 64);
  }
  const cx = (minX + maxX) / 2;
  const n = ranked.length;
  const centred = ranked.map((t) => {
    const sx = t.here.reduce((sum, id) => sum + byId.get(id)!.position.x + 95, 0) / t.here.length;
    const sy = t.here.reduce((sum, id) => sum + byId.get(id)!.position.y + 32, 0) / t.here.length;
    return { ...t, sx, sy };
  });

  // Half above and half below, each by which side its pages lean to.
  const byLean = [...centred].sort((a, b) => a.sy - b.sy || a.term.id.localeCompare(b.term.id));
  const half = Math.ceil(n / 2);
  const perRow = Math.max(4, Math.floor((maxX - minX) / TERM_SLOT.w));
  const slots = new Map<string, XY>();
  const lay = (group: typeof centred, above: boolean) => {
    const sorted = [...group].sort((a, b) => a.sx - b.sx || a.term.id.localeCompare(b.term.id));
    const rows = Math.ceil(sorted.length / perRow);
    sorted.forEach((t, i) => {
      const row = Math.floor(i / perRow);
      const inRow = row === rows - 1 ? sorted.length - row * perRow : perRow;
      const x = cx + ((i % perRow) - (inRow - 1) / 2) * TERM_SLOT.w - TERM_SLOT.w / 2 + 10;
      const y = above
        ? minY - TERM_MARGIN - (rows - 1 - row) * TERM_SLOT.h
        : maxY + TERM_MARGIN + row * TERM_SLOT.h;
      slots.set(t.term.id, { x, y });
    });
  };
  lay(byLean.slice(0, half), true);
  lay(byLean.slice(half), false);

  const nodes: GraphNode[] = [];
  const edges: Edge<WikiEdgeData>[] = [];
  centred.forEach(({ term, here }) => {
    const id = termNodeId(term.id);
    const focused = opts.focusId === id;
    const related = !opts.focusIds || focused || here.some((pid) => opts.focusIds!.has(pid));
    nodes.push({
      id,
      type: "termNode",
      position: slots.get(term.id)!,
      data: {
        title: term.label,
        tags: [],
        domain: [],
        typeTag: "term",
        summary: term.def,
        updated: "",
        path: "",
        dimmed: !related,
        highlighted: focused,
        groupColor: "var(--concept)",
      },
    });
    for (const pid of here) {
      edges.push({ id: `mentions:${term.id}:${pid}`, source: id, target: pid, data: { edgeType: "mentions" } });
    }
  });
  return { nodes, edges };
}

export interface SearchHit {
  kind: "page" | "term";
  id: string;
  label: string;
  detail: string;
  /** Page to open: the page itself, or the page that explains the term. */
  page: string | null;
}

export interface SearchResult {
  hits: SearchHit[];
  /** Pages to light: every matching page and every page mentioning a matching term. */
  lit: Set<string>;
}

const MIN_QUERY = 2;
const MAX_HITS = 8;

interface SearchablePage {
  id: string;
  data: { title: string; summary: string };
}

const termForms = (t: GlossaryTerm) => [t.label, ...t.aliases];

/** Substring search over page titles, summaries and ids, and over term labels and aliases. */
export function searchMap(query: string, pages: SearchablePage[], glossary: Glossary | null): SearchResult | null {
  const q = query.trim().toLowerCase();
  if (q.length < MIN_QUERY) return null;
  const lit = new Set<string>();
  const present = new Set(pages.map((p) => p.id));

  const termHits: SearchHit[] = [];
  for (const term of glossary?.terms ?? []) {
    const form = termForms(term).find((f) => f.toLowerCase().includes(q));
    if (!form) continue;
    for (const id of glossary?.mentions[term.id] ?? []) if (present.has(id)) lit.add(id);
    const alias = form === term.label ? "" : ` (${form})`;
    termHits.push({ kind: "term", id: term.id, label: `${term.label}${alias}`, detail: term.def, page: term.page });
  }

  const pageHits: { hit: SearchHit; rank: number }[] = [];
  for (const p of pages) {
    const title = p.data.title.toLowerCase();
    const inTitle = title.indexOf(q);
    if (inTitle < 0 && !p.data.summary.toLowerCase().includes(q) && !p.id.includes(q)) continue;
    lit.add(p.id);
    pageHits.push({
      hit: { kind: "page", id: p.id, label: p.data.title, detail: p.data.summary, page: p.id },
      rank: inTitle === 0 ? 0 : inTitle > 0 ? 1 : 2,
    });
  }
  pageHits.sort((a, b) => a.rank - b.rank || a.hit.label.localeCompare(b.hit.label));

  return { hits: [...termHits, ...pageHits.map((h) => h.hit)].slice(0, MAX_HITS), lit };
}
