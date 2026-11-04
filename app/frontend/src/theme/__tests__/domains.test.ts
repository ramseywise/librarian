import { describe, expect, it } from "vitest";
import { COURSE_COLORS, KNOWN, PALETTE, courseColor, domainColor, tagColor } from "../domains";

describe("domainColor", () => {
  it("keeps historical colours for known domains", () => {
    expect(domainColor("rag")).toBe("#2196F3");
  });
  it("gives unknown domains a stable palette colour", () => {
    const c = domainColor("brand-new-domain");
    expect(c).toMatch(/^#[0-9A-F]{6}$/i);
    expect(domainColor("brand-new-domain")).toBe(c);
  });
  it("has a default for missing domains", () => {
    expect(domainColor(undefined)).toBe("#688897");
  });
  it("colours type tags as types", () => {
    expect(tagColor("decision")).toBe("#ef9a9a");
  });
});

/** WCAG relative luminance of a #RRGGBB colour. */
function luminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

describe("courseColor", () => {
  it("gives a new course a stable palette colour", () => {
    expect(PALETTE).toContain(courseColor("brand-new-course"));
    expect(courseColor("brand-new-course")).toBe(courseColor("brand-new-course"));
  });
  it("never reuses a directory colour, so the legend stays unambiguous", () => {
    const directories = new Set(Object.values(KNOWN));
    for (const c of Object.values(COURSE_COLORS)) expect(directories.has(c)).toBe(false);
  });
  it("gives every course its own colour", () => {
    const colours = Object.values(COURSE_COLORS);
    expect(new Set(colours).size).toBe(colours.length);
  });
});

describe("domain colour contrast", () => {
  const CARD_BG = "#1a1a1a"; // --surface-field in tokens.css
  it.each([...Object.entries(KNOWN), ...Object.entries(COURSE_COLORS), ...PALETTE.map((c) => [c, c]), ["default", domainColor(undefined)]])(
    "%s reaches 4.5:1 on the card background (small domain label text)",
    (_name, colour) => {
      const ratio = (luminance(colour) + 0.05) / (luminance(CARD_BG) + 0.05);
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    },
  );
});
