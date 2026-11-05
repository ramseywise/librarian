import type { Node } from "@xyflow/react";
import { describe, expect, it } from "vitest";
import type { Glossary, WikiNodeData } from "../../types";
import { isTermNodeId, MAX_TERMS, searchMap, termIdOf, termLayer, termNodeId } from "../glossary";

const page = (id: string, x = 0, y = 0, title = id, summary = ""): Node<WikiNodeData> => ({
  id,
  type: "wikiNode",
  position: { x, y },
  data: { title, tags: [], domain: ["rag"], typeTag: "concept", summary, updated: "", path: "", dimmed: false, highlighted: false },
});

const term = (id: string, label = id, aliases: string[] = []) => ({ id, label, aliases, def: `${label} def`, page: null, mentions: 1 });

describe("term ids", () => {
  it("round-trips and can't be a page's", () => {
    expect(isTermNodeId(termNodeId("rrf"))).toBe(true);
    expect(termIdOf(termNodeId("rrf"))).toBe("rrf");
    expect(isTermNodeId("rrf")).toBe(false);
  });
});

describe("termLayer", () => {
  const pages = [page("a", 0, 0), page("b", 400, 0), page("c", 0, 300), page("d", 400, 300)];

  it("draws a term with its mention edges, not one with a single mention", () => {
    const glossary: Glossary = {
      terms: [term("two"), term("one")],
      mentions: { two: ["a", "b", "elsewhere"], one: ["a"] },
    };
    const layer = termLayer(pages, glossary);
    expect(layer.nodes.map((n) => n.id)).toEqual([termNodeId("two")]);
    expect(layer.edges.map((e) => e.target).sort()).toEqual(["a", "b"]);
    expect(layer.edges.every((e) => e.data?.edgeType === "mentions")).toBe(true);
  });

  it("keeps a term on the anchor page even with one mention, and ranks it first", () => {
    const glossary: Glossary = {
      terms: Array.from({ length: 30 }, (_, i) => term(`t${i}`)).concat(term("mine")),
      mentions: {
        mine: ["a"],
        ...Object.fromEntries(Array.from({ length: 30 }, (_, i) => [`t${i}`, ["b", "c", "d"]])),
      },
    };
    const layer = termLayer(pages, glossary, { anchorId: "a" });
    expect(layer.nodes).toHaveLength(MAX_TERMS);
    expect(layer.nodes.map((n) => n.id)).toContain(termNodeId("mine"));
  });

  it("drops a term on nearly every page of a large view", () => {
    const many = Array.from({ length: 20 }, (_, i) => page(`p${i}`, i * 200));
    const glossary: Glossary = { terms: [term("everywhere")], mentions: { everywhere: many.map((p) => p.id) } };
    expect(termLayer(many, glossary).nodes).toHaveLength(0);
  });

  it("places pills apart from each other and clear of every card", () => {
    const glossary: Glossary = {
      terms: Array.from({ length: MAX_TERMS }, (_, i) => term(`t${i}`)),
      mentions: Object.fromEntries(Array.from({ length: MAX_TERMS }, (_, i) => [`t${i}`, ["a", "b"]])),
    };
    const { nodes } = termLayer(pages, glossary);
    const [w, h] = [270, 44];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i].position;
        const b = nodes[j].position;
        expect(Math.abs(a.x - b.x) >= w || Math.abs(a.y - b.y) >= h).toBe(true);
      }
      for (const p of pages) {
        const a = nodes[i].position;
        expect(a.y + h <= p.position.y - 40 || a.y >= p.position.y + 64 + 40).toBe(true);
      }
    }
  });

  it("dims a term with no page in the focus", () => {
    const glossary: Glossary = { terms: [term("t"), term("u")], mentions: { t: ["a", "b"], u: ["c", "d"] } };
    const { nodes } = termLayer(pages, glossary, { focusIds: new Set(["a"]), focusId: "a" });
    const byId = new Map(nodes.map((n) => [n.id, n.data.dimmed]));
    expect(byId.get(termNodeId("t"))).toBe(false);
    expect(byId.get(termNodeId("u"))).toBe(true);
  });

  it("has nothing to add to no pages", () => {
    expect(termLayer([], { terms: [term("t")], mentions: { t: ["a"] } }).nodes).toEqual([]);
  });
});

describe("searchMap", () => {
  const pages = [page("rrf-page", 0, 0, "Fusion Methods", "How lists merge"), page("other", 0, 0, "Chunking")];
  const glossary: Glossary = {
    terms: [{ ...term("reciprocal", "Reciprocal rank fusion", ["RRF"]), page: "rrf-page" }],
    mentions: { reciprocal: ["rrf-page", "other"] },
  };

  it("matches a term by an alias and lights the pages that mention it", () => {
    const result = searchMap("rrf", pages, glossary)!;
    expect(result.hits[0]).toMatchObject({ kind: "term", id: "reciprocal", page: "rrf-page" });
    expect([...result.lit].sort()).toEqual(["other", "rrf-page"]);
  });

  it("matches a page by title", () => {
    const result = searchMap("chunk", pages, null)!;
    expect(result.hits.map((h) => h.id)).toEqual(["other"]);
    expect([...result.lit]).toEqual(["other"]);
  });

  it("waits for two characters", () => {
    expect(searchMap("r", pages, glossary)).toBeNull();
    expect(searchMap("  ", pages, glossary)).toBeNull();
  });
});
