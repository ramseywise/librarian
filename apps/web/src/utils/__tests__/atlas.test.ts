import { describe, expect, it } from "vitest";
import type { Curriculum } from "../../types";
import {
  BANDS,
  bandOf,
  bandRadius,
  BEYOND_SECTOR,
  hitTest,
  LABEL_ROW,
  layoutLabels,
  layoutRing,
  polar,
  ringGeometry,
  sectorIdOf,
  sectorsOf,
  type AtlasPage,
} from "../atlas";

const pages = (domain: string, n: number, from = 0): AtlasPage[] =>
  Array.from({ length: n }, (_, i) => ({ id: `${domain}-${from + i}`, domain }));

const curriculum: Curriculum = {
  courses: [
    {
      id: "ai",
      title: "AI",
      pageIds: ["a-0", "a-1"],
      modules: [{ id: "m", title: "M", firstLesson: null, pageIds: ["a-0", "a-1"] }],
    },
    { id: "ds", title: "DS", pageIds: ["a-1", "b-0"], modules: [] },
  ],
  beyond: [{ domain: "b", pageIds: ["b-1"] }],
  primaryCourse: { "a-0": "ai", "a-1": "ai", "b-0": "ds" },
  stale: false,
};

const insets = { left: 0, top: 0, bottom: 0, labelWidth: 100 };

describe("bandOf", () => {
  it("places degrees on the scale", () => {
    expect([0, 1, 2, 3, 4, 8, 9, 15, 16, 112].map(bandOf)).toEqual([0, 0, 1, 1, 2, 2, 3, 3, 4, 4]);
    expect(BANDS).toHaveLength(5);
  });
});

describe("sectorsOf", () => {
  it("groups by domain, largest first, each sorted by degree", () => {
    const degree = new Map([["b-1", 9], ["b-0", 2], ["a-0", 5]]);
    const sectors = sectorsOf([...pages("a", 1), ...pages("b", 2)], degree, "domain", null);
    expect(sectors.map((s) => s.id)).toEqual(["b", "a"]);
    expect(sectors[0].pageIds).toEqual(["b-1", "b-0"]);
  });

  it("puts a page in its main course only, and the rest in Beyond", () => {
    const all = [...pages("a", 2), ...pages("b", 2)];
    const sectors = sectorsOf(all, new Map(), "course", curriculum);
    const byId = new Map(sectors.map((s) => [s.id, s]));
    expect(byId.get("ai")?.pageIds.sort()).toEqual(["a-0", "a-1"]);
    expect(byId.get("ds")?.pageIds).toEqual(["b-0"]);
    expect(byId.get(BEYOND_SECTOR)?.pageIds).toEqual(["b-1"]);
    expect(sectors.flatMap((s) => s.pageIds).sort()).toEqual(all.map((p) => p.id).sort());
    expect(sectorIdOf({ id: "b-1", domain: "b" }, "course", curriculum)).toBe(BEYOND_SECTOR);
    expect(sectorIdOf({ id: "b-0", domain: "b" }, "course", curriculum)).toBe("ds");
    expect(sectorIdOf({ id: "b-0", domain: "b" }, "domain", curriculum)).toBe("b");
  });
});

describe("layoutRing", () => {
  const sectors = sectorsOf([...pages("big", 1200), ...pages("tiny", 1), ...pages("mid", 40)], new Map(), "domain", null);
  const ring = layoutRing(sectors);

  it("gives every page one spike, in angle order, inside a full turn", () => {
    expect(ring.spikes).toHaveLength(1241);
    for (let i = 1; i < ring.spikes.length; i++) {
      expect(ring.spikes[i].angle).toBeGreaterThan(ring.spikes[i - 1].angle);
    }
    expect(ring.spikes[ring.spikes.length - 1].angle).toBeLessThan(Math.PI * 2);
    expect(ring.spikes.every((s, i) => s.index === i)).toBe(true);
  });

  it("leaves a sector of one page a visible arc", () => {
    const tiny = ring.arcs[ring.sectors.findIndex((s) => s.id === "tiny")];
    expect(tiny.end - tiny.start).toBeGreaterThan(0.01);
  });
});

describe("geometry", () => {
  it("orders the band guides outward within the ring", () => {
    const g = ringGeometry(1000, 800, insets);
    const radii = BANDS.map((_, i) => bandRadius(g, i));
    expect(radii[0]).toBeGreaterThan(g.inner);
    for (let i = 1; i < radii.length; i++) expect(radii[i]).toBeGreaterThan(radii[i - 1]);
    expect(radii[radii.length - 1]).toBeLessThanOrEqual(g.outer);
  });
});

describe("layoutLabels", () => {
  // The real shape: a long run of tiny sectors, which all want the same spot on the ring.
  const shape: [string, number][] = [
    ["foundations", 437], ["patterns", 370], ["eval", 80], ["infra", 67], ["meta", 41], ["prompting", 36],
    ["interview", 35], ["rag", 34], ["harness", 31], ["context", 22], ["adk", 20], ["langgraph", 17],
    ["graph", 13], ["memory", 12], ["loop", 11], ["projects", 10], ["mcp", 9],
  ];
  const ring = layoutRing(sectorsOf(shape.flatMap(([d, n]) => pages(d, n)), new Map(), "domain", null));

  for (const [w, h] of [[1080, 860], [390, 700], [800, 420]]) {
    it(`keeps labels a row apart and on the stage at ${w}x${h}`, () => {
      const g = ringGeometry(w, h, { left: 0, top: 80, bottom: 10, labelWidth: 84 });
      const labels = layoutLabels(ring, g);
      expect(labels).toHaveLength(shape.length);
      for (const anchor of ["start", "end"] as const) {
        const ys = labels.filter((l) => l.anchor === anchor).map((l) => l.y).sort((a, b) => a - b);
        for (let i = 1; i < ys.length; i++) expect(ys[i] - ys[i - 1]).toBeGreaterThanOrEqual(LABEL_ROW - 0.001);
      }
      for (const l of labels) {
        expect(l.y).toBeGreaterThan(0);
        expect(l.y).toBeLessThanOrEqual(h);
      }
    });
  }

  it("truncates only for lack of room", () => {
    const g = ringGeometry(1400, 860, { left: 0, top: 80, bottom: 10, labelWidth: 84 });
    const long = layoutRing(sectorsOf(pages("a-rather-long-sector-name", 3), new Map(), "domain", null));
    expect(layoutLabels(long, g)[0].text).toBe("a-rather-long-sector-name");
  });
});

describe("hitTest", () => {
  const ring = layoutRing(sectorsOf([...pages("a", 300), ...pages("b", 300)], new Map(), "domain", null));
  const g = ringGeometry(1000, 800, insets);

  it("finds the spike under the pointer", () => {
    const spike = ring.spikes[250];
    const at = polar(g, spike.angle, (g.inner + g.outer) / 2);
    const hit = hitTest(ring, g, at.x, at.y);
    expect(hit).toMatchObject({ kind: "spike" });
    expect(hit?.kind === "spike" && hit.spike.id).toBe(spike.id);
  });

  it("finds a sector on its arc", () => {
    const arc = ring.arcs[1];
    const at = polar(g, arc.mid, g.outer + 7);
    expect(hitTest(ring, g, at.x, at.y)).toMatchObject({ kind: "sector", sector: 1 });
  });

  it("finds nothing in the hole, the label gap, or outside", () => {
    expect(hitTest(ring, g, g.cx, g.cy)).toBeNull();
    const gap = polar(g, 0, (g.inner + g.outer) / 2);
    expect(hitTest(ring, g, gap.x, gap.y)).toBeNull();
    expect(hitTest(ring, g, 2, 2)).toBeNull();
  });
});
