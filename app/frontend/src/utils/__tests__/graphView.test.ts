import { describe, expect, it } from "vitest";
import type { Edge, Node } from "@xyflow/react";
import {
  applyView,
  degreeOf,
  expandBridges,
  filterPrimaryIds,
  neighbours,
  renderIds,
  sampleIds,
  visibleEdges,
  type ViewState,
} from "../graphView";
import type { EdgeVisibility, WikiEdgeData, WikiNodeData } from "../../types";

const node = (id: string, domain: string, typeTag = "concept"): Node<WikiNodeData> => ({
  id,
  position: { x: 0, y: 0 },
  data: {
    title: id, tags: [domain, typeTag], domain: [domain], typeTag,
    summary: "", updated: "", path: "", dimmed: false, highlighted: false,
  },
});
const edge = (source: string, target: string, edgeType: WikiEdgeData["edgeType"]): Edge<WikiEdgeData> => ({
  id: `${edgeType}:${source}->${target}`, source, target, data: { edgeType },
});

const NONE: ViewState = {
  focusId: null, focusIds: null, filterIds: null, activeTags: new Set(),
};
const ALL_ON: EdgeVisibility = { wikilink: true, semantic: true, "tag-shared": true };

const nodes = [node("p", "projects", "project"), node("a", "rag"), node("b", "eval"), node("c", "memory")];
const flags = (ns: Node<WikiNodeData>[]) =>
  Object.fromEntries(ns.map((n) => [n.id, { dimmed: n.data.dimmed, hl: n.data.highlighted }]));

describe("filter derivation", () => {
  it("is null without active chips", () => {
    expect(filterPrimaryIds(nodes, new Set())).toBeNull();
  });

  it("matches domain or type tag", () => {
    expect([...filterPrimaryIds(nodes, new Set(["rag"]))!]).toEqual(["a"]);
    expect([...filterPrimaryIds(nodes, new Set(["project"]))!]).toEqual(["p"]);
  });

  it("expands only to bridges: outside pages linked to >= 2 primaries", () => {
    const primary = new Set(["a", "b"]);
    const out = expandBridges(primary, [
      { source: "c", target: "a" }, { source: "b", target: "c" }, // c bridges a and b
      { source: "a", target: "p" }, // p touches the set once
    ]);
    expect([...out].sort()).toEqual(["a", "b", "c"]);
    expect([...expandBridges(primary, [{ source: "a", target: "p" }], 1)].sort()).toEqual(["a", "b", "p"]);
  });
});

describe("sample and reveal", () => {
  const many = [
    node("p", "projects", "project"),
    node("r1", "rag"), node("r2", "rag"), node("r3", "rag"), node("r4", "rag"),
    node("e1", "eval"),
  ];
  const links = [
    { source: "r1", target: "r2" }, { source: "r1", target: "r3" }, { source: "r1", target: "e1" },
    { source: "r2", target: "r3" },
  ];

  it("keeps every project page plus each domain's best-linked pages", () => {
    const ids = sampleIds(many, degreeOf(links), 2);
    expect([...ids].sort()).toEqual(["e1", "p", "r1", "r2"]);
  });

  it("neighbours: typed links first, then by degree, capped", () => {
    const edges = [
      { source: "r1", target: "r2" },
      { source: "r3", target: "r1", data: { relationship: "extends" } },
      { source: "r1", target: "e1" },
    ];
    const deg = degreeOf([...edges, { source: "r2", target: "r4" }]);
    expect(neighbours("r1", edges, deg)).toEqual(["r3", "r2", "e1"]);
    expect(neighbours("r1", edges, deg, 2)).toEqual(["r3", "r2"]);
  });

  it("renderIds: all, sample + revealed, filter, plus focus and chat", () => {
    const sample = new Set(["p"]);
    const revealed = new Set(["a"]);
    expect(renderIds(true, sample, revealed, NONE)).toBeNull();
    expect([...renderIds(false, sample, revealed, NONE)!].sort()).toEqual(["a", "p"]);
    const v = { ...NONE, filterIds: new Set(["b"]), focusIds: new Set(["c"]), chatHighlight: new Set(["x"]) };
    expect([...renderIds(false, sample, revealed, v)!].sort()).toEqual(["b", "c", "x"]);
  });
});

describe("applyView", () => {
  it("dims nothing without a filter, focus or chat", () => {
    const f = flags(applyView(nodes, NONE));
    expect(Object.values(f).every((x) => !x.dimmed && !x.hl)).toBe(true);
  });

  it("filter highlights primaries without dimming the rest", () => {
    const v = { ...NONE, activeTags: new Set(["rag"]), filterIds: new Set(["a", "b"]) };
    const f = flags(applyView(nodes, v));
    expect(f.a).toEqual({ dimmed: false, hl: true });
    expect(f.b).toEqual({ dimmed: false, hl: false });
  });

  it("focus dims everything outside the neighbourhood", () => {
    const f = flags(applyView(nodes, { ...NONE, focusId: "a", focusIds: new Set(["a", "b"]) }));
    expect(f.a.hl && f.b.hl).toBe(true);
    expect(f.c.dimmed).toBe(true);
  });

  it("chat highlight wins over filter and focus", () => {
    const v = {
      ...NONE,
      chatHighlight: new Set(["c"]),
      focusId: "a", focusIds: new Set(["a"]),
      activeTags: new Set(["rag"]), filterIds: new Set(["a"]),
    };
    const f = flags(applyView(nodes, v));
    expect(f.c).toEqual({ dimmed: false, hl: true });
    expect(f.a).toEqual({ dimmed: true, hl: false });
  });

  it("enlarges chat hits only, never a filter or focus highlight", () => {
    const big = (v: typeof NONE) => applyView(nodes, v).filter((n) => n.data.enlarged).map((n) => n.id);
    expect(big({ ...NONE, activeTags: new Set(["rag"]), filterIds: new Set(["a"]) })).toEqual([]);
    expect(big({ ...NONE, focusId: "a", focusIds: new Set(["a", "b"]) })).toEqual([]);
    expect(big({ ...NONE, chatHighlight: new Set(["c"]) })).toEqual(["c"]);
  });

  it("ignores a chat highlight that names no existing node", () => {
    const v = { ...NONE, chatHighlight: new Set(["no-such-page"]), focusId: "a", focusIds: new Set(["a"]) };
    const f = flags(applyView(nodes, v));
    expect(f.a).toEqual({ dimmed: false, hl: true }); // focus applies as if no chat
    expect(f.b.dimmed).toBe(true);
    const ids = visibleEdges({ wikilink: [edge("a", "b", "wikilink")], semantic: [], tagShared: [] },
      ALL_ON, applyView(nodes, v), v).map((e) => e.id);
    expect(ids).toEqual(["wikilink:a->b"]);
  });
});

describe("visibleEdges", () => {
  const src = {
    wikilink: [edge("a", "b", "wikilink")],
    semantic: [edge("a", "c", "semantic")],
    tagShared: [edge("a", "b", "tag-shared"), edge("p", "a", "tag-shared")],
  };

  it("respects the toggles when no filter is active", () => {
    const v = NONE;
    const out = visibleEdges(src, { wikilink: true, semantic: false, "tag-shared": false }, applyView(nodes, v), v);
    expect(out.map((e) => e.id)).toEqual(["wikilink:a->b"]);
    expect(out[0].style).toBeDefined();
  });

  it("prunes tag-shared edges with no emphasised endpoint", () => {
    // Chat cites p: p is highlighted, a/b/c dimmed. Only p–a survives among tag-shared edges.
    const v = { ...NONE, chatHighlight: new Set(["p"]) };
    const out = visibleEdges(src, ALL_ON, applyView(nodes, v), v);
    expect(out.filter((e) => e.data?.edgeType === "tag-shared").map((e) => e.id)).toEqual(["tag-shared:p->a"]);
  });

  it("drops edges whose endpoint is not rendered", () => {
    const v = NONE;
    const rendered = nodes.filter((n) => n.id !== "b");
    const ids = visibleEdges(src, ALL_ON, applyView(rendered, v), v).map((e) => e.id);
    expect(ids).toEqual(["semantic:a->c"]);
  });

  it("renders no tag-shared edges when nothing is emphasised (no selection)", () => {
    const v = NONE;
    const out = visibleEdges(src, ALL_ON, applyView(nodes, v), v);
    expect(out.some((e) => e.data?.edgeType === "tag-shared")).toBe(false);
    expect(out.some((e) => e.data?.edgeType === "wikilink")).toBe(true);
  });

  it("filter mode honours the toggles inside the subgraph", () => {
    const v = { ...NONE, activeTags: new Set(["rag"]), filterIds: new Set(["a", "b"]) };
    const on = visibleEdges(src, ALL_ON, applyView(nodes, v), v).map((e) => e.id);
    expect(on.sort()).toEqual(["tag-shared:a->b", "wikilink:a->b"]);
    const noTagShared = { ...ALL_ON, "tag-shared": false };
    const ids = visibleEdges(src, noTagShared, applyView(nodes, v), v).map((e) => e.id);
    expect(ids).toEqual(["wikilink:a->b"]);
    const off = { wikilink: false, semantic: false, "tag-shared": false };
    expect(visibleEdges(src, off, applyView(nodes, v), v)).toEqual([]);
  });

  it("focus keeps only edges touching the focused node", () => {
    const v = { ...NONE, focusId: "b", focusIds: new Set(["b", "a"]) };
    const ids = visibleEdges(src, ALL_ON, applyView(nodes, v), v).map((e) => e.id);
    expect(ids.sort()).toEqual(["tag-shared:a->b", "wikilink:a->b"]);
  });

  it("marks semantic edges animated", () => {
    const v = NONE;
    const out = visibleEdges(src, ALL_ON, applyView(nodes, v), v);
    expect(out.find((e) => e.data?.edgeType === "semantic")?.animated).toBe(true);
  });
});
