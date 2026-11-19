import { describe, expect, it } from "vitest";
import type { AtlasSector } from "../../utils/atlas";
import { cardSize } from "../../utils/clusterLayout";
import { hopsFrom } from "../../utils/hopField";
import { fitPadding, fitToCanvasShape, layoutClusterField, positionsOf } from "../wikiGraphLayout";

describe("fitPadding", () => {
  it("clears the top for the bar, and pads the other sides evenly", () => {
    expect(fitPadding(0.15)).toEqual({ top: "110px", right: 0.15, bottom: 0.15, left: 0.15 });
  });
});

describe("positionsOf", () => {
  it("maps node ids to their positions", () => {
    const nodes = [
      { id: "a", position: { x: 1, y: 2 }, data: {} },
      { id: "b", position: { x: 3, y: 4 }, data: {} },
    ];
    expect(positionsOf(nodes)).toEqual({ a: { x: 1, y: 2 }, b: { x: 3, y: 4 } });
  });
});

describe("fitToCanvasShape", () => {
  const wide = { a: { x: 0, y: 0 }, b: { x: 400, y: 100 }, c: { x: 200, y: 50 }, far: { x: 0, y: 1000 } };

  it("stretches a wide subset vertically from its top, capped at 2.2, and moves pages outside it with the same scale", () => {
    const out = fitToCanvasShape(wide, new Set(["a", "b", "c"]));
    // width 400 / height 100 = 4, capped at 2.2
    expect(out.b.x).toBe(400);
    expect(out.b.y).toBeCloseTo(220);
    expect(out.a).toEqual({ x: 0, y: 0 });
    expect(out.far.y).toBeCloseTo(2200);
  });

  it("stretches only as far as the aspect ratio asks", () => {
    const out = fitToCanvasShape({ a: { x: 0, y: 0 }, b: { x: 150, y: 100 } }, new Set(["a", "b"]));
    expect(out.b.y).toBeCloseTo(100 * 1.5);
  });

  it("leaves a subset that is already tall or square, flat or empty, as it is", () => {
    const tall = { a: { x: 0, y: 0 }, b: { x: 10, y: 100 } };
    expect(fitToCanvasShape(tall, new Set(["a", "b"]))).toBe(tall);
    const flat = { a: { x: 0, y: 5 }, b: { x: 100, y: 5 } };
    expect(fitToCanvasShape(flat, new Set(["a", "b"]))).toBe(flat);
    expect(fitToCanvasShape(tall, new Set())).toBe(tall);
  });

  it("ignores ids that have no position", () => {
    const out = fitToCanvasShape(wide, new Set(["a", "b", "missing"]));
    expect(out.b.y).toBeCloseTo(220);
  });
});

describe("layoutClusterField", () => {
  const sectors = [{ id: "s", label: "S", pageIds: ["a", "b", "x"], color: "#000" }] as unknown as AtlasSector[];
  const reach = hopsFrom("a", [{ source: "a", target: "b" }, { source: "b", target: "x" }]);

  it("builds a circle around the cards, whose frame holds the cards' box", () => {
    const positions = { a: { x: 0, y: 0 }, b: { x: 500, y: 300 } };
    const depth = new Map([["a", 0], ["b", 2]]);
    const { frame } = layoutClusterField(positions, depth, reach, sectors, "a");
    const b = cardSize(2);
    expect(frame.x).toBeLessThanOrEqual(0);
    expect(frame.y).toBeLessThanOrEqual(0);
    expect(frame.x + frame.w).toBeGreaterThanOrEqual(500 + b.w);
    expect(frame.y + frame.h).toBeGreaterThanOrEqual(300 + b.h);
  });

  it("gives the same field for the same cards", () => {
    const positions = { a: { x: 0, y: 0 }, b: { x: 200, y: 0 } };
    const depth = new Map([["a", 0], ["b", 1]]);
    expect(layoutClusterField(positions, depth, reach, sectors, "a")).toEqual(
      layoutClusterField(positions, depth, reach, sectors, "a"),
    );
  });
});
