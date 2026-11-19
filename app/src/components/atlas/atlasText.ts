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
}
