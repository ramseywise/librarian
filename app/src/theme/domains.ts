/**
 * Domain and type colours for the graph UI.
 *
 * The domain *list* is never hardcoded in the frontend: it comes from the graph payload
 * (`domains`, derived from data/wiki/ directories on the server). This module only maps a
 * domain name to a colour. Known domains keep their historical colours; any new wiki
 * directory gets a stable colour from the palette, so adding a domain needs no code change.
 * Every colour must reach 4.5:1 on the card background (--surface-field), since it
 * colours the small domain label on each card; domains.test.ts enforces this.
 *
 * The tables hold the dark-theme colours, which are light tints. In the light theme each is
 * darkened at its own hue until it reaches the same contrast, so a domain stays the same
 * colour family and no second table can drift.
 */

import { currentTheme, type Theme } from "../utils/theme";

export const KNOWN: Record<string, string> = {
  rag: "#2196F3",
  langgraph: "#4CAF50",
  adk: "#FF9800",
  infra: "#688897",
  patterns: "#EC3F7A",
  eval: "#FFEB3B",
  "deep-agents": "#717FCD",
  memory: "#00BCD4",
  mcp: "#C552D9",
  meta: "#A67A6A",
  projects: "#009688",
  foundations: "#9473CC",
  interview: "#FF5722",
  context: "#26A69A",
  prompting: "#F06292",
  harness: "#9C7D72",
  loop: "#AED581",
  graph: "#4DD0E1",
  multimodal: "#FFAB91",
  private: "#9E9E9E",
};

/** Fallback palette for domains not in KNOWN — distinct from the known hues where possible. */
export const PALETTE = [
  "#FFB74D", "#BA68C8", "#81C784", "#64B5F6", "#E57373",
  "#4DB6AC", "#FFD54F", "#9575CD", "#A1887F", "#90A4AE",
];

/** One per course; these colour the map's cards, so they share the 4.5:1 rule above. */
export const COURSE_COLORS: Record<string, string> = {
  programming: "#64B5F6",
  "data-analytics": "#FFD54F",
  "data-science": "#BA68C8",
  "data-engineering": "#4DB6AC",
  "generative-ai": "#FF8A65",
  "ai-engineering": "#81C784",
  interviewing: "#F48FB1",
};

/** Deterministic string hash (FNV-1a, 32-bit). */
function hash(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** --surface-field under [data-theme="light"] in tokens.css; tokens.test.ts keeps them equal. */
export const LIGHT_CARD_BG = "#efeee9";
const LIGHT_TARGET_RATIO = 4.6;

/** WCAG relative luminance of a #RRGGBB colour. */
export function luminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export function contrastRatio(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Hue and saturation of a #RRGGBB colour, h in 0-1. */
function hueSat(hex: string): { h: number; s: number; l: number } {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  const d = max - min;
  if (!d) return { h: 0, s: 0, l };
  const s = d / (1 - Math.abs(2 * l - 1));
  const h = max === r ? ((g - b) / d + 6) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return { h: h / 6, s, l };
}

function fromHsl(h: number, s: number, l: number): string {
  const a = s * Math.min(l, 1 - l);
  const channel = (n: number) => {
    const k = (n + h * 12) % 12;
    const v = l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1));
    return Math.round(v * 255).toString(16).padStart(2, "0");
  };
  return `#${channel(0)}${channel(8)}${channel(4)}`.toUpperCase();
}

const lightCache = new Map<string, string>();

/** The colour at its own hue, darkened until it is readable on the light card background. */
export function lightVariant(hex: string): string {
  const cached = lightCache.get(hex);
  if (cached) return cached;
  const { h, s, l } = hueSat(hex);
  let out = hex;
  for (let next = l; next > 0 && contrastRatio(out, LIGHT_CARD_BG) < LIGHT_TARGET_RATIO; next -= 0.005) {
    out = fromHsl(h, s, next);
  }
  lightCache.set(hex, out);
  return out;
}

const forTheme = (hex: string, theme: Theme) => (theme === "light" ? lightVariant(hex) : hex);

export function domainColor(domain: string | undefined | null, theme: Theme = currentTheme()): string {
  if (!domain) return forTheme("#688897", theme);
  return forTheme(KNOWN[domain] ?? PALETTE[hash(domain) % PALETTE.length], theme);
}

export function courseColor(course: string, theme: Theme = currentTheme()): string {
  return forTheme(COURSE_COLORS[course] ?? PALETTE[hash(course) % PALETTE.length], theme);
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
export function tagColor(tag: string, theme: Theme = currentTheme()): string {
  return TYPE_COLORS[tag] ? forTheme(TYPE_COLORS[tag], theme) : domainColor(tag, theme);
}
