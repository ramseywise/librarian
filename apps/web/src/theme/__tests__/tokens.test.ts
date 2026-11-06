/// <reference types="vite/client" />
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { THEME_STORAGE_KEY } from "../../utils/theme";
import { contrastRatio, LIGHT_CARD_BG } from "../domains";

// Read from disk: Vitest empties CSS imports, `?raw` included, under `css: false`.
const here = import.meta.url;
const read = (path: string) => readFileSync(decodeURIComponent(new URL(path, here).pathname), "utf8");
const html = read("../../../index.html");
const courses = read("../../components/courses/courses.css");
const components = read("../components.css");
const source = read("../tokens.css");

function tokensIn(block: string): Record<string, string> {
  return Object.fromEntries([...block.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));
}

function hex(value: string): string {
  const short = value.match(/^#([0-9a-f])([0-9a-f])([0-9a-f])$/i);
  return short ? `#${short[1]}${short[1]}${short[2]}${short[2]}${short[3]}${short[3]}` : value;
}

const LIGHT_START = source.indexOf('[data-theme="light"] {');
const dark = tokensIn(source.slice(source.indexOf(":root {"), LIGHT_START));
const lightOwn = tokensIn(source.slice(LIGHT_START));
const light = { ...dark, ...lightOwn };

const SURFACES = [
  "--bg", "--surface", "--surface-sidebar", "--surface-raised", "--surface-card", "--surface-pager",
  "--surface-field", "--surface-tab", "--surface-active", "--surface-selected", "--surface-user-msg",
];
const TEXT = [
  "--text-strong", "--text", "--text-body", "--text-soft", "--text-dim", "--text-secondary",
  "--text-muted", "--text-faint", "--text-ghost", "--text-void", "--prose-text", "--prose-heading",
  "--prose-quote",
];
/** Small text on panels and page backgrounds, though not on a pressed or tinted control. */
const ACCENT_TEXT = [
  "--accent", "--accent-text", "--link", "--success", "--danger", "--offline", "--warn", "--concept",
  "--error-note", "--warn-soft", "--edge-wikilink-label", "--edge-semantic", "--edge-tag",
];
const PANELS = ["--bg", "--surface", "--surface-sidebar", "--surface-raised", "--surface-card", "--surface-pager"];
/** Filled controls with white text. */
const FILLS = ["--accent-fill", "--send", "--stop"];
const AA = 4.5;
const DARK_ONLY_EXCEPTIONS = new Set([
  // Pre-existing: the dark ladder's dimmest greys were only ever set against panels.
  "--text-secondary", "--text-muted", "--text-faint", "--text-ghost", "--text-void", "--text-dim",
]);

const themes = [["dark", dark], ["light", light]] as const;

describe.each(themes)("%s theme tokens", (name, t) => {
  it("defines every token the checks read", () => {
    for (const k of [...SURFACES, ...TEXT, ...ACCENT_TEXT, ...FILLS]) expect(t[k], k).toMatch(/^#/);
  });

  it.each(TEXT)("%s reaches 4.5:1 on the surfaces it can sit on", (token) => {
    const on = name === "dark" && DARK_ONLY_EXCEPTIONS.has(token) ? PANELS : SURFACES;
    for (const s of on) {
      expect(contrastRatio(hex(t[token]), hex(t[s])), `${token} on ${s}`).toBeGreaterThanOrEqual(AA);
    }
  });

  it.each(ACCENT_TEXT)("%s reaches 4.5:1 on panels", (token) => {
    for (const s of PANELS) {
      expect(contrastRatio(hex(t[token]), hex(t[s])), `${token} on ${s}`).toBeGreaterThanOrEqual(AA);
    }
  });

  it.each(FILLS)("white text stays readable on %s", (token) => {
    expect(contrastRatio("#ffffff", hex(t[token]))).toBeGreaterThanOrEqual(AA);
  });

  it.each(["--prose-text", "--link", "--concept", "--text-strong"])("%s reaches 4.5:1 on code and quote surfaces", (token) => {
    for (const s of ["--code-bg", "--pre-bg"]) {
      expect(contrastRatio(hex(t[token]), hex(t[s])), `${token} on ${s}`).toBeGreaterThanOrEqual(AA);
    }
  });
});

describe("light theme", () => {
  it("overrides every colour the dark theme sets", () => {
    const colours = Object.entries(dark).filter(([, v]) => /^#/.test(v)).map(([k]) => k);
    expect(colours.filter((k) => !(k in lightOwn))).toEqual([]);
  });

  it("domains.ts darkens against the real card background", () => {
    expect(LIGHT_CARD_BG).toBe(light["--surface-field"]);
  });
});

describe("index.html first paint", () => {
  it("reads the same storage key as utils/theme.ts", () => {
    expect(html).toContain(`localStorage.getItem("${THEME_STORAGE_KEY}")`);
  });
  it("paints the themes' real backgrounds before the stylesheet loads", () => {
    expect(html).toContain(`var(--bg, ${light["--bg"]})`);
    expect(html).toContain(`var(--bg, ${dark["--bg"]})`);
  });
});

describe("reading typography", () => {
  const prose = courses.match(/\.lesson-prose \{([^}]*)\}/)?.[1] ?? "";
  it("sets lesson text in a serif at about 68 characters", () => {
    expect(prose).toContain("font-family: var(--font-reading)");
    expect(prose).toContain("max-width: var(--measure-reading)");
    expect(dark["--measure-reading"]).toBe("68ch");
    expect(dark["--font-reading"]).toMatch(/serif$/);
  });
  it("keeps code monospaced", () => {
    expect(courses.match(/\.lesson-prose code \{([^}]*)\}/)?.[1]).toMatch(/monospace/);
  });
  it("leaves the app chrome alone", () => {
    expect(components).not.toContain("--font-reading");
    expect(courses.match(/font-reading/g)).toHaveLength(1);
  });
});
