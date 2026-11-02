import { describe, expect, it } from "vitest";
import { KNOWN, PALETTE, domainColor, tagColor } from "../domains";

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

describe("domain colour contrast", () => {
  const CARD_BG = "#1a1a1a"; // --surface-field in tokens.css
  it.each([...Object.entries(KNOWN), ...PALETTE.map((c) => [c, c]), ["default", domainColor(undefined)]])(
    "%s reaches 4.5:1 on the card background (small domain label text)",
    (_name, colour) => {
      const ratio = (luminance(colour) + 0.05) / (luminance(CARD_BG) + 0.05);
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    },
  );
});
