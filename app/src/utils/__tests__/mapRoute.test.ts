import { afterEach, describe, expect, it } from "vitest";
import { ATLAS, DEFAULT_CAP, levelKey, mapPath, MAX_CAP, PAGE_CAP, parentOf, parseMapRoute, replaceRoute, type MapView } from "../mapRoute";

describe("parseMapRoute", () => {
  it("opens on the atlas", () => {
    expect(parseMapRoute("/")).toEqual(ATLAS);
    expect(parseMapRoute("/nonsense")).toEqual(ATLAS);
    expect(parseMapRoute("/map/nonsense")).toEqual(ATLAS);
  });

  it("leaves the other tabs alone, so the mounted graph keeps its level", () => {
    for (const path of ["/courses", "/courses/a/b", "/practice", "/flashcards/x"]) {
      expect(parseMapRoute(path)).toBeNull();
    }
  });

  it("round-trips every level", () => {
    const views: MapView[] = [
      { level: "atlas", grouping: "course" },
      { level: "sector", grouping: "domain", sector: "rag", cap: DEFAULT_CAP },
      { level: "sector", grouping: "domain", sector: "rag", cap: 300 },
      { level: "page", grouping: "course", sector: "beyond the/curriculum", page: "a&b", cap: PAGE_CAP },
      { level: "page", grouping: "domain", sector: "rag", page: "p", cap: 120 },
      { level: "all", tags: [] },
      { level: "all", tags: ["rag", "course:data-science"] },
    ];
    for (const v of views) expect(parseMapRoute(mapPath(v))).toEqual(v);
  });

  it("keeps a default cap out of the link, per level", () => {
    expect(mapPath({ level: "sector", grouping: "domain", sector: "rag", cap: DEFAULT_CAP })).toBe("/map/domain/rag");
    expect(mapPath({ level: "page", grouping: "domain", sector: "rag", page: "p", cap: PAGE_CAP })).toBe(
      "/map/domain/rag/p",
    );
  });

  it("clamps a hand-edited cap", () => {
    expect(parseMapRoute("/map/domain/rag?cap=999999")).toMatchObject({ cap: MAX_CAP });
    expect(parseMapRoute("/map/domain/rag?cap=-4")).toMatchObject({ cap: DEFAULT_CAP });
    expect(parseMapRoute("/map/domain/rag/p?cap=abc")).toMatchObject({ cap: PAGE_CAP });
  });

  it("survives a malformed escape", () => {
    expect(parseMapRoute("/map/domain/%E0%A4%A")).toEqual(ATLAS);
  });
});

describe("parentOf and levelKey", () => {
  it("steps page, sector, atlas, and stops", () => {
    const page: MapView = { level: "page", grouping: "course", sector: "s", page: "p", cap: 120 };
    const sector = parentOf(page)!;
    expect(sector).toEqual({ level: "sector", grouping: "course", sector: "s", cap: DEFAULT_CAP });
    const atlas = parentOf(sector)!;
    expect(atlas).toEqual({ level: "atlas", grouping: "course" });
    expect(parentOf(atlas)).toBeNull();
    expect(parentOf({ level: "all", tags: ["x"] })).toEqual(ATLAS);
  });

  it("treats a wider cap as the same level", () => {
    const a: MapView = { level: "sector", grouping: "domain", sector: "s", cap: DEFAULT_CAP };
    expect(levelKey(a)).toBe(levelKey({ ...a, cap: 600 }));
    expect(levelKey({ level: "all", tags: [] })).toBe(levelKey({ level: "all", tags: ["x"] }));
  });
});

describe("replaceRoute", () => {
  afterEach(() => {
    window.location.hash = "";
  });

  it("changes the hash without a new history entry and tells the router", () => {
    const before = window.history.length;
    let told = 0;
    const listener = () => told++;
    window.addEventListener("hashchange", listener);
    replaceRoute("/map/course");
    window.removeEventListener("hashchange", listener);
    expect(window.location.hash).toBe("#/map/course");
    expect(window.history.length).toBe(before);
    expect(told).toBe(1);
  });
});
