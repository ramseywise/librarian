import { describe, expect, it } from "vitest";
import type { Edge, Node } from "@xyflow/react";
import {
  applyView,
  expandOneHop,
  filterPrimaryIds,
  focusNeighbourhood,
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
  focusId: null, focusIds: null, filterIds: null, activeTags: new Set(), overview: false,
};
const ALL_ON: EdgeVisibility = { wikilink: true, semantic: true, "tag-shared": true };

const nodes = [node("p", "projects", "project"), node("a", "rag"), node("b", "eval"), node("c", "memory")];
const flags = (ns: Node<WikiNodeData>[]) =>
  Object.fromEntries(ns.map((n) => [n.id, { hidden: !!n.hidden, dimmed: n.data.dimmed, hl: n.data.highlighted }]));

describe("filter derivation", () => {
  it("is null without active chips", () => {
    expect(filterPrimaryIds(nodes, new Set())).toBeNull();
  });

  it("matches domain or type tag, then expands one hop", () => {
    const primary = filterPrimaryIds(nodes, new Set(["rag"]))!;
    expect([...primary]).toEqual(["a"]);
    const expanded = expandOneHop(primary, [{ source: "b", target: "a" }, { source: "b", target: "c" }]);
    expect([...expanded].sort()).toEqual(["a", "b"]);
  });
});

describe("focusNeighbourhood", () => {
  it("takes 2 structural hops and 1 semantic hop", () => {
    const ids = focusNeighbourhood(
      "a",
      [{ source: "a", target: "b" }, { source: "b", target: "c" }, { source: "c", target: "p" }],
      [{ source: "x", target: "a" }],
    )!;
    expect([...ids].sort()).toEqual(["a", "b", "c", "x"]);
  });
});

describe("applyView", () => {
  it("overview dims everything but project pages", () => {
    const f = flags(applyView(nodes, { ...NONE, overview: true }));
    expect(f.p.dimmed).toBe(false);
    expect(f.a.dimmed).toBe(true);
  });

  it("filter hides non-matches, highlights primaries, and overrides overview dimming", () => {
    const v = { ...NONE, overview: true, activeTags: new Set(["rag"]), filterIds: new Set(["a", "b"]) };
    const f = flags(applyView(nodes, v));
    expect(f.c.hidden).toBe(true);
    expect(f.a).toEqual({ hidden: false, dimmed: false, hl: true });
    expect(f.b).toEqual({ hidden: false, dimmed: false, hl: false });
  });

  it("focus dims everything outside the neighbourhood", () => {
    const f = flags(applyView(nodes, { ...NONE, focusId: "a", focusIds: new Set(["a", "b"]) }));
    expect(f.a.hl && f.b.hl).toBe(true);
    expect(f.c.dimmed).toBe(true);
  });

  it("chat highlight wins over filter and focus and never hides nodes", () => {
    const v = {
      ...NONE,
      chatHighlight: new Set(["c"]),
      focusId: "a", focusIds: new Set(["a"]),
      activeTags: new Set(["rag"]), filterIds: new Set(["a"]),
    };
    const f = flags(applyView(nodes, v));
    expect(f.c).toEqual({ hidden: false, dimmed: false, hl: true });
    expect(f.a).toEqual({ hidden: false, dimmed: true, hl: false });
  });

  it("ignores a chat highlight that names no existing node", () => {
    const v = { ...NONE, chatHighlight: new Set(["no-such-page"]), focusId: "a", focusIds: new Set(["a"]) };
    const f = flags(applyView(nodes, v));
    expect(f.a).toEqual({ hidden: false, dimmed: false, hl: true }); // focus applies as if no chat
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

  it("prunes tag-shared edges with no emphasised endpoint (overview)", () => {
    const v = { ...NONE, overview: true };
    const out = visibleEdges(src, ALL_ON, applyView(nodes, v), v);
    // a and b are dimmed, p (project) is not: only p–a survives among tag-shared edges.
    expect(out.filter((e) => e.data?.edgeType === "tag-shared").map((e) => e.id)).toEqual(["tag-shared:p->a"]);
    // Wikilink / semantic edges are not pruned by dimming.
    expect(out.some((e) => e.id === "wikilink:a->b")).toBe(true);
  });

  it("renders no tag-shared edges when nothing is emphasised (All mode, no selection)", () => {
    const v = NONE;
    const out = visibleEdges(src, ALL_ON, applyView(nodes, v), v);
    expect(out.some((e) => e.data?.edgeType === "tag-shared")).toBe(false);
    expect(out.some((e) => e.data?.edgeType === "wikilink")).toBe(true);
  });

  it("filter mode shows all types inside the subgraph, ignoring toggles", () => {
    const v = { ...NONE, activeTags: new Set(["rag"]), filterIds: new Set(["a", "b"]) };
    const off = { wikilink: false, semantic: false, "tag-shared": false };
    const ids = visibleEdges(src, off, applyView(nodes, v), v).map((e) => e.id);
    expect(ids.sort()).toEqual(["tag-shared:a->b", "wikilink:a->b"]);
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
