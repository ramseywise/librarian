import { describe, expect, it } from "vitest";
import { domainColor, tagColor } from "../domains";

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
    expect(domainColor(undefined)).toBe("#607D8B");
  });
  it("colours type tags as types", () => {
    expect(tagColor("decision")).toBe("#ef9a9a");
  });
});
