import { describe, expect, it } from "vitest";
import { growDir, hopsFrom, layoutField, NEAR_HOPS } from "../hopField";
import type { AtlasSector } from "../atlas";

const link = (source: string, target: string) => ({ source, target });

describe("hopsFrom", () => {
  const edges = [link("a", "b"), link("c", "b"), link("c", "d"), link("d", "e"), link("e", "f"), link("a", "a")];

  it("counts links either way and names the page each is reached through", () => {
    const reach = hopsFrom("a", edges);
    expect(Object.fromEntries(reach)).toEqual({
      b: { hop: 1, via: "a" },
      c: { hop: 2, via: "b" },
      d: { hop: 3, via: "c" },
      e: { hop: 4, via: "d" },
      f: { hop: 5, via: "e" },
    });
  });

  it("stops at the hop limit", () => {
    expect([...hopsFrom("a", edges, 2).keys()]).toEqual(["b", "c"]);
  });
});

describe("layoutField", () => {
  const sectors: AtlasSector[] = [
    { id: "rag", label: "RAG", color: "#f00", pageIds: ["a", "b", "c", "d"] },
    { id: "llm", label: "LLM", color: "#0f0", pageIds: ["e", "f", "g"] },
  ];
  const edges = [link("a", "b"), link("b", "c"), link("b", "g"), link("c", "d"), link("d", "e"), link("e", "f")];
  const box = { x: -500, y: -300, w: 1000, h: 600 };
  const centres = new Map([["a", { x: 0, y: 0 }], ["b", { x: 300, y: 0 }]]);
  const field = layoutField(hopsFrom("a", edges), new Set(centres.keys()), box, sectors, (id) => centres.get(id), "a");
  const dot = (id: string) => field.dots.find((d) => d.id === id)!;
  const radius = (d: { x: number; y: number }) => Math.hypot(d.x - field.circle.x, d.y - field.circle.y);

  it("gives every page a point in a circular band clear of the cards, cards' pages included", () => {
    expect(field.dots.map((d) => d.id).sort()).toEqual(["a", "b", "c", "d", "e", "f", "g"]);
    const radii = field.dots.map(radius);
    // Past the cards' corners, and a band, not a box: the radii stay close together.
    expect(Math.min(...radii)).toBeGreaterThan(field.circle.inner);
    expect(Math.max(...radii)).toBeLessThan(field.circle.outer);
    expect(field.circle.outer - field.circle.inner).toBeLessThan(120);
    for (const [x, y] of [[-500, -300], [500, -300], [-500, 300], [500, 300]]) expect(radius({ x, y })).toBeLessThan(field.circle.inner - 60);
    for (const d of field.dots) for (const o of field.dots) if (d !== o) expect(Math.hypot(d.x - o.x, d.y - o.y)).toBeGreaterThan(10);
    expect([field.near, field.far, field.beyond]).toEqual([2, 2, 1]);
  });

  it("puts the open page's card out towards its own point, as far as the cards fit", () => {
    // Its card (at the origin), its point and the circle's middle are in line, the card between.
    const own = dot("a");
    const toOwn = Math.atan2(own.y - field.circle.y, own.x - field.circle.x);
    const toCard = Math.atan2(-field.circle.y, -field.circle.x);
    expect(toCard).toBeCloseTo(toOwn, 3);
    expect(radius({ x: 0, y: 0 })).toBeGreaterThan(100);
    // As far as fits: some corner of the cards is at the clear space before the band.
    const reach = Math.max(...[[-500, -300], [500, -300], [-500, 300], [500, 300]].map(([x, y]) => radius({ x, y })));
    expect(reach).toBeCloseTo(field.circle.inner - 70, 0);
  });

  it("says which way a page's clusters grow into the circle", () => {
    const wide: AtlasSector[] = [{ id: "s", label: "S", color: "#000", pageIds: ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7"] }];
    expect(wide[0].pageIds.map((id) => growDir(wide, id))).toEqual([0, -1, -1, 0, 0, 1, 1, 0]);
    expect(growDir(wide, "missing")).toBe(0);
  });

  it("keeps a sector's points together in its wedge, inside the box the sector zooms to", () => {
    const angle = (d: { x: number; y: number }) => (Math.atan2(d.x - field.circle.x, field.circle.y - d.y) + Math.PI * 2) % (Math.PI * 2);
    const rag = field.dots.filter((d) => d.sector === 0).map(angle);
    const llm = field.dots.filter((d) => d.sector === 1).map(angle);
    expect(Math.max(...rag)).toBeLessThan(Math.min(...llm));
    for (const d of field.dots) {
      const b = field.arcs[d.sector].box;
      expect(d.x).toBeGreaterThan(b.x);
      expect(d.x).toBeLessThan(b.x + b.w);
      expect(d.y).toBeGreaterThan(b.y);
      expect(d.y).toBeLessThan(b.y + b.h);
    }
  });

  it("records how far each page is and ties it to the page it is reached through", () => {
    expect(["a", "b", "c", "g", "d", "e", "f"].map((id) => dot(id).hop)).toEqual([0, 1, 2, 2, 3, 4, 5]);
    expect(dot("a").card && dot("b").card).toBe(true);
    expect(dot("c").card).toBe(false);
    expect(NEAR_HOPS).toBe(2);
    // A card's point to its card, a near point to the card it hangs off, a further one to a point.
    expect(dot("b").from).toEqual({ x: 300, y: 0 });
    expect(dot("c").from).toEqual({ x: 300, y: 0 });
    expect(dot("d").from).toEqual({ x: dot("c").x, y: dot("c").y });
    expect(dot("e").via).toBe("d");
  });

  it("draws each sector's arc outside the band and labels it with its pages in reach, inside the frame", () => {
    expect(field.arcs.map((a) => a.lit)).toEqual([true, true]);
    expect(field.labels.map((l) => l.text).sort()).toEqual(["LLM · 3", "RAG · 4"]);
    for (const l of field.labels) {
      expect(radius(l)).toBeGreaterThan(Math.max(...field.dots.map(radius)));
      expect(l.x).toBeGreaterThan(field.frame.x);
      expect(l.x).toBeLessThan(field.frame.x + field.frame.w);
      expect(l.y).toBeGreaterThan(field.frame.y);
      expect(l.y).toBeLessThan(field.frame.y + field.frame.h);
    }
  });
});
