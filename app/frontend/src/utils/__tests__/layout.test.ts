import { describe, expect, it } from "vitest";
import { layoutEdges, placeMissingNodes } from "../layout";

const n = (id: string, domain: string) => ({ id, data: { domain: [domain] } });

describe("placeMissingNodes", () => {
  it("keeps cached positions untouched", () => {
    const pos = { a: { x: 1, y: 2 } };
    expect(placeMissingNodes([n("a", "rag")], pos, [])).toEqual(pos);
  });

  it("places a new node at the centroid of its positioned wikilink neighbours", () => {
    const pos = { a: { x: 0, y: 0 }, b: { x: 10, y: 20 }, c: { x: 500, y: 500 } };
    const out = placeMissingNodes(
      [n("a", "rag"), n("b", "eval"), n("c", "rag"), n("new", "rag")],
      pos,
      [{ source: "new", target: "a" }, { source: "b", target: "new" }],
    );
    expect(out.new).toEqual({ x: 5, y: 10 });
  });

  it("falls back to the domain centroid when no neighbour has a position", () => {
    const pos = { a: { x: 0, y: 0 }, b: { x: 10, y: 10 }, c: { x: 900, y: 900 } };
    const out = placeMissingNodes(
      [n("a", "rag"), n("b", "rag"), n("c", "eval"), n("new", "rag"), n("other", "rag")],
      pos,
      [{ source: "new", target: "other" }], // neighbour is itself unplaced
    );
    expect(out.new).toEqual({ x: 5, y: 5 });
    expect(out.other).toEqual({ x: 5, y: 5 });
  });

  it("falls back to the origin for an unknown domain with no neighbours", () => {
    const out = placeMissingNodes([n("a", "rag"), n("new", "loop")], { a: { x: 3, y: 3 } }, []);
    expect(out.new).toEqual({ x: 0, y: 0 });
  });
});

describe("layoutEdges", () => {
  it("keeps one incoming edge per node, drops self-loops and dangling edges", () => {
    const ids = new Set(["a", "b", "c"]);
    const edges = [
      { source: "a", target: "b" },
      { source: "c", target: "b" },
      { source: "a", target: "a" },
      { source: "a", target: "zzz" },
      { source: "b", target: "c" },
    ];
    expect(layoutEdges(ids, edges)).toEqual([
      { source: "a", target: "b" },
      { source: "b", target: "c" },
    ]);
  });
});
