/**
 * Domain and type colours for the graph UI.
 *
 * The domain *list* is never hardcoded in the frontend: it comes from the graph payload
 * (`domains`, derived from data/wiki/ directories on the server). This module only maps a
 * domain name to a colour. Known domains keep their historical colours; any new wiki
 * directory gets a stable colour from the palette, so adding a domain needs no code change.
 */

const KNOWN: Record<string, string> = {
  rag: "#2196F3",
  langgraph: "#4CAF50",
  adk: "#FF9800",
  infra: "#607D8B",
  patterns: "#E91E63",
  eval: "#FFEB3B",
  "deep-agents": "#3F51B5",
  memory: "#00BCD4",
  mcp: "#9C27B0",
  meta: "#795548",
  projects: "#009688",
  foundations: "#7E57C2",
  interview: "#FF5722",
  context: "#26A69A",
  prompting: "#F06292",
  harness: "#8D6E63",
  loop: "#AED581",
  graph: "#4DD0E1",
  private: "#9E9E9E",
};

/** Fallback palette for domains not in KNOWN — distinct from the known hues where possible. */
const PALETTE = [
  "#FFB74D", "#BA68C8", "#81C784", "#64B5F6", "#E57373",
  "#4DB6AC", "#FFD54F", "#9575CD", "#A1887F", "#90A4AE",
];

/** Deterministic string hash (FNV-1a, 32-bit). */
function hash(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

export function domainColor(domain: string | undefined | null): string {
  if (!domain) return "#607D8B";
  return KNOWN[domain] ?? PALETTE[hash(domain) % PALETTE.length];
}

export const TYPE_COLORS: Record<string, string> = {
  concept: "#9e9e9e",
  pattern: "#b39ddb",
  decision: "#ef9a9a",
  project: "#80cbc4",
  comparison: "#ffe082",
  reference: "#a5d6a7",
  conflict: "#ff7043",
};

/** Colour for any tag shown as a chip: type tags first, then domains. */
export function tagColor(tag: string): string {
  return TYPE_COLORS[tag] ?? domainColor(tag);
}
