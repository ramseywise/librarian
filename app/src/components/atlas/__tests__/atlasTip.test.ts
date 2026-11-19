import { describe, expect, it } from "vitest";
import type { AtlasSector, RingGeometry } from "../../../utils/atlas";
import { fillSectorTip, fillTip, hideTip, moveTip, TOOLTIP_W } from "../atlasTip";

const sector = { label: "RAG", pageIds: ["a", "b", "c"] } as unknown as AtlasSector;
const g = { width: 1000, height: 800 } as RingGeometry;
const lines = (tip: HTMLElement) => [...tip.children].map((c) => c.textContent);

describe("atlas tooltip", () => {
  it("fills a page: title, summary and its sector with the link count", () => {
    const tip = document.createElement("div");
    tip.hidden = true;
    fillTip(tip, { title: "RRF", summary: "Fuse lists." }, sector, 3, false);
    expect(tip.hidden).toBe(false);
    expect(lines(tip)).toEqual(["RRF", "Fuse lists.", "RAG · 3 links"]);
  });

  it("says singular for one link, and flags a page no lesson covers", () => {
    const tip = document.createElement("div");
    fillTip(tip, undefined, sector, 1, true);
    expect(lines(tip)).toEqual(["", "", "RAG · 1 link · not yet in a lesson"]);
  });

  it("fills a sector with its page count, and its gaps when it has any", () => {
    const tip = document.createElement("div");
    fillSectorTip(tip, sector, null);
    expect(lines(tip)).toEqual(["RAG", "3 pages · click to open the best linked"]);
    fillSectorTip(tip, sector, 2);
    expect(lines(tip)[1]).toBe("3 pages · 2 not yet in a lesson · click to open the best linked");
  });

  it("writes text, never markup", () => {
    const tip = document.createElement("div");
    fillTip(tip, { title: "<b>x</b>", summary: "" }, sector, 0, false);
    expect(tip.querySelector("b")).toBeNull();
  });

  it("hides, tolerating no element", () => {
    const tip = document.createElement("div");
    hideTip(tip);
    expect(tip.hidden).toBe(true);
    expect(() => hideTip(null)).not.toThrow();
  });

  it("sits beside the pointer, flipping where there is no room", () => {
    const tip = document.createElement("div");
    moveTip(tip, 100, 100, g);
    expect(tip.style.transform).toBe("translate(116px, 114px)");
    moveTip(tip, 900, 100, g); // right edge: to the left of the pointer
    expect(tip.style.transform).toBe(`translate(${900 - TOOLTIP_W - 16}px, 114px)`);
    moveTip(tip, 100, 700, g); // bottom edge: above the pointer
    expect(tip.style.transform).toBe("translate(116px, 570px)");
    moveTip(tip, 0, 0, { ...g, width: 100 }); // never off the top-left
    expect(tip.style.transform).toBe("translate(4px, 14px)");
  });
});
