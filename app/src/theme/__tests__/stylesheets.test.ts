import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { duplicates, hexColours, sectionHeaders, stylesheets } from "./stylesheets";

// A variable, not an inline `import.meta.url`: Vite rewrites `new URL("x", import.meta.url)` to an asset URL.
const here = import.meta.url;
const srcDir = decodeURIComponent(new URL("../../", here).pathname);
const source = (rel: string) => readFileSync(decodeURIComponent(new URL(rel, here).pathname), "utf8");
const sheets = stylesheets(srcDir);

describe("stylesheets", () => {
  it("finds the sheets, so the checks below are not vacuous", () => {
    const files = sheets.map((s) => s.file);
    for (const f of ["tokens.css", "ui.css", "graph.css", "filter.css", "card.css", "chat.css", "courses.css"]) {
      expect(files, f).toContain(f);
    }
    expect(files).not.toContain("components.css");
    expect(files).not.toContain("light.css");
  });

  it("writes no hex colour outside tokens.css", () => {
    const found = sheets.filter((s) => s.file !== "tokens.css").map((s) => [s.file, hexColours(s.css)] as const);
    expect(found.filter(([, hexes]) => hexes.length > 0)).toEqual([]);
  });

  it("repeats no section header within one stylesheet", () => {
    const repeated = sheets.map((s) => [s.file, duplicates(sectionHeaders(s.css))] as const);
    expect(repeated.filter(([, d]) => d.length > 0)).toEqual([]);
  });

  it("imports tokens.css then ui.css in main.tsx only", () => {
    const main = source("../../main.tsx");
    expect(main.indexOf("theme/tokens.css")).toBeGreaterThan(-1);
    expect(main.indexOf("theme/ui.css")).toBeGreaterThan(main.indexOf("theme/tokens.css"));
    expect(main.indexOf("./App")).toBeGreaterThan(main.indexOf("theme/ui.css"));
    expect(source("../../App.tsx")).not.toMatch(/^import\s+"[^"]*theme\/(tokens|ui)\.css"/m);
  });
});

describe("the checks have teeth", () => {
  it("sees a hex colour, but not one in a comment", () => {
    expect(hexColours(".a { color: #fff; background: #0b0b0b80; }")).toEqual(["#fff", "#0b0b0b80"]);
    expect(hexColours("/* #fff */ .a { color: var(--x); }")).toEqual([]);
  });

  it("sees a repeated section header", () => {
    const css = "/* ---- Chat ---- */\n.a{}\n/* ---- Graph ---- */\n.b{}\n/* ---- Chat ---- */\n.c{}";
    expect(sectionHeaders(css)).toEqual(["Chat", "Graph", "Chat"]);
    expect(duplicates(sectionHeaders(css))).toEqual(["Chat"]);
  });
});
