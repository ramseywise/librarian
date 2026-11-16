import type { Glossary, GlossaryTerm } from "../types";

/**
 * Glossary-aware search over the map. Terms are not pages and are not drawn: a term filter
 * (`term:<id>`, in the sidebar) or a search hit lights the pages that mention it.
 */

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
