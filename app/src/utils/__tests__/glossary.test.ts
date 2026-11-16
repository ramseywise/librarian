import type { Node } from "@xyflow/react";
import { describe, expect, it } from "vitest";
import type { Glossary, WikiNodeData } from "../../types";
import { searchMap } from "../glossary";

const page = (id: string, x = 0, y = 0, title = id, summary = ""): Node<WikiNodeData> => ({
  id,
  type: "wikiNode",
  position: { x, y },
  data: { title, tags: [], domain: ["rag"], typeTag: "concept", summary, updated: "", path: "", dimmed: false, highlighted: false },
});

const term = (id: string, label = id, aliases: string[] = []) => ({ id, label, aliases, def: `${label} def`, page: null, mentions: 1 });

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
