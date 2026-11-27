import type { PageOrigin } from "../../schemas/graph";
import type { AtlasSector } from "../../utils/atlas";

/** "k not yet in a lesson": the pages a course has still to cover. */
export function gapText(gaps: number): string {
  return `${gaps} not yet in a lesson`;
}

/** A sector in words: its pages, and how many of them no lesson links yet. */
export function sectorSummary(sector: AtlasSector, gaps: number | null): string {
  const pages = `${sector.label}: ${sector.pageIds.length} pages`;
  return gaps ? `${pages} · ${gapText(gaps)}` : pages;
}

export interface AtlasPageInfo {
  title: string;
  summary: string;
  tags?: string[];
  /** Relative to data/wiki/: the note's address in the repo. */
  path?: string;
  origins?: PageOrigin[];
  sourceCount?: number;
}

/** Public pages live in the repo, so a page's note is its file there. Private pages never reach the atlas. */
export const WIKI_BLOB = "https://github.com/ramseywise/librarian/blob/main/data/wiki";

export const wikiNoteHref = (path: string) => `${WIKI_BLOB}/${path.split("/").map(encodeURIComponent).join("/")}`;
