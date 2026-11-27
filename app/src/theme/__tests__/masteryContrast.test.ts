/// <reference types="vite/client" />
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { contrastRatio } from "../domains";

// Read from disk: Vitest empties CSS imports under `css: false`.
const here = import.meta.url;
const read = (path: string) => readFileSync(decodeURIComponent(new URL(path, here).pathname), "utf8");
const source = read("../tokens.css");
const courses = read("../../components/courses/courses.css");

function tokensIn(block: string): Record<string, string> {
  return Object.fromEntries([...block.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));
}
const hex = (v: string) => {
  const s = v.match(/^#([0-9a-f])([0-9a-f])([0-9a-f])$/i);
  return s ? `#${s[1]}${s[1]}${s[2]}${s[2]}${s[3]}${s[3]}` : v;
};

const LIGHT_START = source.indexOf('[data-theme="light"] {');
const dark = tokensIn(source.slice(source.indexOf(":root {"), LIGHT_START));
const light = { ...dark, ...tokensIn(source.slice(LIGHT_START)) };

/** The token a mastery rule reads for `prop`, so the test checks what the stylesheet really uses. */
function tokenOf(selector: string, prop: string): string {
  const rule = courses.match(new RegExp(`${selector.replace(/[.]/g, "\\.")}\\s*\\{([^}]*)\\}`))?.[1] ?? "";
  const m = rule.match(new RegExp(`${prop}[^;]*var\\((--[\\w-]+)\\)`));
  if (!m) throw new Error(`${selector} sets no ${prop} from a token`);
  return m[1];
}

describe.each([["dark", dark], ["light", light]] as const)("mastery bar contrast, %s theme", (_name, t) => {
  const fill = tokenOf(".mastery-fill", "background");
  const track = tokenOf(".mastery-seg", "background");
  const outline = tokenOf(".mastery-seg.is-empty", "border");
  const label = tokenOf(".mastery-label", "color");

  it("the fill stands out from its track (3:1)", () => {
    expect(contrastRatio(hex(t[fill]), hex(t[track]))).toBeGreaterThanOrEqual(3);
  });

  // The bar sits on a catalog card, an overview card and the page.
  describe.each(["--surface-card", "--bg", "--surface"])("on %s", (surface) => {
    it("the no-data outline is a visible graphic (3:1)", () => {
      expect(contrastRatio(hex(t[outline]), hex(t[surface]))).toBeGreaterThanOrEqual(3);
    });
    it("the fill is a visible graphic (3:1)", () => {
      expect(contrastRatio(hex(t[fill]), hex(t[surface]))).toBeGreaterThanOrEqual(3);
    });
    it("the label is readable text (4.5:1)", () => {
      expect(contrastRatio(hex(t[label]), hex(t[surface]))).toBeGreaterThanOrEqual(4.5);
    });
  });
});
