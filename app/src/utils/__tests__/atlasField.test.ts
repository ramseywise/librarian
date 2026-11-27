import { describe, expect, it } from "vitest";
import { layoutRing, ringGeometry, sectorsOf, type AtlasPage } from "../atlas";
import { FIELD_R, fieldHit, fieldScale, layoutField } from "../atlasField";

const pages = (domain: string, n: number): AtlasPage[] =>
  Array.from({ length: n }, (_, i) => ({ id: `${domain}-${i}`, domain }));

const all = [...pages("a", 40), ...pages("b", 25), ...pages("c", 10)];
const edges = [
  { source: "a-0", target: "a-1" },
  { source: "a-0", target: "b-0" },
  { source: "a-0", target: "c-3" },
  { source: "b-0", target: "a-0" }, // the same pair the other way: counted once
  { source: "a-1", target: "a-1" }, // a self-link: dropped
  { source: "a-2", target: "gone" }, // a page not in the ring: dropped
];
const degree = new Map<string, number>([
  ["a-0", 3],
  ["a-1", 1],
  ["b-0", 1],
  ["c-3", 1],
]);
const ring = layoutRing(sectorsOf(all, degree, "wiki", []));

describe("layoutField", () => {
  const field = layoutField(ring, degree, edges);
  const at = (id: string) => ring.spikes.findIndex((s) => s.id === id);

  it("keeps every dot inside the ring", () => {
    expect(field.x).toHaveLength(all.length);
    for (let i = 0; i < field.x.length; i++) {
      expect(Math.hypot(field.x[i], field.y[i]) + field.r[i]).toBeLessThanOrEqual(FIELD_R + 1e-6);
    }
  });

  it("sizes a dot by its links", () => {
    expect(field.r[at("a-0")]).toBeGreaterThan(field.r[at("a-1")]);
    expect(field.r[at("a-1")]).toBeGreaterThan(field.r[at("a-5")]);
  });

  it("lists each page's neighbours once, both ways", () => {
    expect(new Set(field.neighbours[at("a-0")])).toEqual(new Set([at("a-1"), at("b-0"), at("c-3")]));
    expect(field.neighbours[at("b-0")]).toEqual([at("a-0")]);
    expect(field.neighbours[at("a-2")]).toEqual([]);
    expect(field.links).toHaveLength(6);
  });

  it("lays the same wiki out the same way", () => {
    const again = layoutField(ring, degree, edges);
    expect(Array.from(again.x)).toEqual(Array.from(field.x));
    expect(Array.from(again.y)).toEqual(Array.from(field.y));
  });

  it("accepts links d3 has already resolved to nodes", () => {
    const resolved = layoutField(ring, degree, [{ source: { id: "a-0" }, target: { id: "c-3" } }]);
    expect(resolved.neighbours[at("c-3")]).toEqual([at("a-0")]);
  });
});

describe("fieldHit", () => {
  const field = layoutField(ring, degree, edges);
  const g = ringGeometry(900, 700, { left: 0, top: 0, bottom: 0, labelWidth: 100 });
  const k = fieldScale(g);

  it("finds the dot under a point, and nothing outside the field", () => {
    const i = ring.spikes.findIndex((s) => s.id === "a-0");
    expect(fieldHit(field, g, g.cx + field.x[i] * k, g.cy + field.y[i] * k, 0)).toBe(i);
    expect(fieldHit(field, g, g.cx + g.inner * 2, g.cy, 0)).toBeNull();
  });
});
