import { describe, expect, it } from "vitest";
import type { Edge } from "@xyflow/react";
import { cardSize, clusterTree, depthsOf, layoutClusters, skeletonOf, withSideHandles } from "../clusterLayout";
import { degreeOf } from "../graphView";

const link = (source: string, target: string, relationship?: string) => ({
  id: `${source}->${target}`, source, target, data: relationship ? { relationship } : {},
});

describe("clusterTree", () => {
  it("gives the anchor's neighbours a cluster each and hangs the rest behind them", () => {
    const edges = [link("a", "h1"), link("a", "h2"), link("h1", "x"), link("h2", "y"), link("y", "z")];
    const ids = new Set(["a", "h1", "h2", "x", "y", "z"]);
    const parent = clusterTree("a", ids, [edges], degreeOf(edges));
    expect(Object.fromEntries(parent)).toEqual({ h1: "a", h2: "a", x: "h1", y: "h2", z: "y" });
  });

  it("puts typed links first and folds neighbours past the cap into a cluster they link to", () => {
    const edges = [link("a", "b"), link("a", "c"), link("a", "t", "extends"), link("t", "c")];
    const parent = clusterTree("a", new Set(["a", "b", "c", "t"]), [edges], degreeOf(edges), undefined, 1);
    // `t` is typed, so it heads the one cluster; `c` links into it; `b` links only to the anchor.
    expect(Object.fromEntries(parent)).toEqual({ t: "a", c: "t", b: "a" });
  });

  it("shares pages between the heads they link to, so a hub can't take them all", () => {
    const edges = [
      link("a", "hub"), link("a", "h2"),
      link("hub", "x"), link("hub", "y"), link("hub", "z"), link("h2", "y"), link("h2", "z"),
    ];
    const parent = clusterTree("a", new Set(["a", "hub", "h2", "x", "y", "z"]), [edges], degreeOf(edges));
    const of = (head: string) => [...parent].filter(([, to]) => to === head).length;
    expect(of("hub")).toBe(2);
    expect(of("h2")).toBe(1);
  });

  it("lets a later tier place only what the first left, then hints, then the anchor", () => {
    const wikilinks = [link("a", "h"), link("h", "x")];
    const semantic = [link("a", "x"), link("x", "s")];
    const ids = new Set(["a", "h", "x", "s", "m", "lost"]);
    const parent = clusterTree("a", ids, [wikilinks, semantic], degreeOf(wikilinks), new Map([["m", "x"]]));
    expect(Object.fromEntries(parent)).toEqual({ h: "a", x: "h", s: "x", m: "x", lost: "a" });
  });
});

describe("layoutClusters", () => {
  const edges = [link("a", "h1"), link("a", "h2"), link("h1", "x"), link("h1", "y"), link("h2", "z")];
  const parent = clusterTree("a", new Set(["a", "h1", "h2", "x", "y", "z"]), [edges], degreeOf(edges));
  const at = layoutClusters("a", parent);

  it("places clusters either side of the anchor, a column per hop", () => {
    expect(at.a.x).toBeLessThan(0);
    expect(at.h1.x).toBeGreaterThan(0);
    expect(at.h2.x).toBeLessThan(at.a.x);
    expect(at.x.x).toBeGreaterThan(at.h1.x);
    expect(at.z.x).toBeLessThan(at.h2.x);
    // A parent sits level with the middle of its children.
    const mid = (id: string, depth: number) => at[id].y + cardSize(depth).h / 2;
    expect(mid("h1", 1)).toBeCloseTo((mid("x", 2) + mid("y", 2)) / 2);
  });

  it("runs every cluster one way when told to, for a page at the side of the circle", () => {
    const left = layoutClusters("a", parent, -1);
    for (const id of ["h1", "h2", "x", "y", "z"]) expect(left[id].x).toBeLessThan(left.a.x);
    expect(left.h1.y).not.toBe(left.h2.y);
    const right = layoutClusters("a", parent, 1);
    for (const id of ["h1", "h2", "x", "y", "z"]) expect(right[id].x).toBeGreaterThan(right.a.x);
  });

  it("never overlaps two cards, which shrink with their hops from the anchor", () => {
    const depth = depthsOf("a", parent);
    expect(Object.fromEntries(depth)).toEqual({ a: 0, h1: 1, h2: 1, x: 2, y: 2, z: 2 });
    expect(cardSize(2).w).toBeLessThan(cardSize(1).w);
    expect(cardSize(1).w).toBeLessThan(cardSize(0).w);
    expect(cardSize(9)).toEqual(cardSize(3));
    const boxes = Object.entries(at).map(([id, p]) => ({ ...p, ...cardSize(depth.get(id)!) }));
    for (const p of boxes) {
      for (const q of boxes) {
        if (p === q) continue;
        const apart = p.x + p.w <= q.x || q.x + q.w <= p.x || p.y + p.h <= q.y || q.y + q.h <= p.y;
        expect(apart).toBe(true);
      }
    }
  });

  it("names its pairs, and sends edges between columns out by the sides", () => {
    expect(skeletonOf(parent)).toEqual(new Set(["a|h1", "a|h2", "h1|x", "h1|y", "h2|z"]));
    const [right, left, column] = withSideHandles<Edge>([link("h1", "x"), link("a", "h2"), link("x", "y")], at);
    expect(right).toMatchObject({ sourceHandle: "sr", targetHandle: "tl" });
    expect(left).toMatchObject({ sourceHandle: "sl", targetHandle: "tr" });
    expect(column.sourceHandle).toBeUndefined();
  });
});
