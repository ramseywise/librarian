import { describe, expect, it } from "vitest";
import type { Node } from "@xyflow/react";
import type { Area, Curriculum, WikiNodeData } from "../../types";
import { courseColor, domainColor } from "../../theme/domains";
import { applyView, filterPrimaryIds } from "../graphView";
import { facetPending, facetsOf, isFacetId, rankGroupsOf, withCourseGroups } from "../curriculum";

function node(id: string, domain = "rag", typeTag = "concept"): Node<WikiNodeData> {
  return {
    id,
    position: { x: 0, y: 0 },
    data: { title: id, tags: [], domain: [domain], typeTag, summary: "", updated: "", path: "", dimmed: false, highlighted: false },
  };
}

const curriculum: Curriculum = {
  courses: [
    { id: "ai", title: "AI Eng", pageIds: ["a", "b"], modules: [{ id: "rag", title: "RAG", firstLesson: null, pageIds: ["a"], notes: [] }] },
    { id: "data", title: "Data", pageIds: ["b"], modules: [] },
  ],
  beyond: [{ domain: "patterns", pageIds: ["c", "d", "e"] }],
  primaryCourse: { a: "ai", b: "ai" },
  stale: false,
};
const facets = facetsOf(curriculum);
const nodes = [node("a"), node("b"), node("c", "patterns"), node("d", "patterns"), node("e", "patterns"), node("p", "projects", "project")];

describe("area and gap facets", () => {
  const areas: Area[] = [{ id: "generative-ai", title: "Generative AI", domains: ["rag"] }];
  const withPaths = nodes.map((n) => ({ ...n, data: { ...n.data, path: `${n.data.domain[0]}/${n.id}.md` } }));

  it("an area is its directories' pages; its gap is those no lesson links, only with the curriculum", () => {
    const f = facetsOf(curriculum, [...withPaths, { ...node("q"), data: { ...node("q").data, path: "rag/q.md" } }], null, areas);
    expect([...f.get("area:generative-ai")!].sort()).toEqual(["a", "b", "q"]);
    expect([...f.get("gap:generative-ai")!]).toEqual(["q"]);
    expect(f.has("area:patterns")).toBe(false);
    const noCurriculum = facetsOf(null, withPaths, null, areas);
    expect(noCurriculum.has("area:generative-ai")).toBe(true);
    expect(noCurriculum.has("gap:generative-ai")).toBe(false);
    expect(facetPending("gap:generative-ai", null, null)).toBe(true);
    expect(facetPending("area:generative-ai", null, null)).toBe(false);
  });
});

describe("curriculum filters", () => {
  it.each([
    ["course:ai", ["a", "b"]],
    ["module:ai/rag", ["a"]],
    ["beyond:patterns", ["c", "d", "e"]],
    ["beyond:all", ["c", "d", "e"]],
  ])("%s selects its pages", (id, expected) => {
    expect([...filterPrimaryIds(nodes, new Set([id]), facets)!].sort()).toEqual(expected);
  });

  it("plain directory and type tags still work alongside them", () => {
    expect([...filterPrimaryIds(nodes, new Set(["patterns"]), facets)!].sort()).toEqual(["c", "d", "e"]);
    expect([...filterPrimaryIds(nodes, new Set(["project", "module:ai/rag"]), facets)!].sort()).toEqual(["a", "p"]);
  });

  it("a `dir:` facet selects the pages in that wiki directory", () => {
    const withPaths = [{ ...node("x"), data: { ...node("x").data, path: "foundations/x.md" } }, node("y")];
    expect([...facetsOf(null, withPaths).get("dir:foundations")!]).toEqual(["x"]);
  });

  it("selects nothing for a facet id before the curriculum loads", () => {
    expect(filterPrimaryIds(nodes, new Set(["course:ai"]))!.size).toBe(0);
  });

  it("highlights the same pages it selects", () => {
    const v = {
      focusId: null,
      focusIds: null,
      filterIds: new Set(["a"]),
      activeTags: new Set(["module:ai/rag"]),
      facets,
    };
    const lit = applyView(nodes, v).filter((n) => n.data.highlighted).map((n) => n.id);
    expect(lit).toEqual(["a"]);
  });
});

describe("withCourseGroups", () => {
  it("colours and labels linked pages by main course, leaving the rest alone", () => {
    const [a, c] = withCourseGroups([node("a"), node("c", "patterns")], curriculum);
    expect(a.data.groupColor).toBe(courseColor("ai"));
    expect(a.data.groupLabel).toBe("AI Eng");
    expect(c.data.groupColor).toBeUndefined();
    expect(domainColor(c.data.domain[0])).toBe(domainColor("patterns"));
  });

  it("does nothing before the curriculum loads", () => {
    const input = [node("a")];
    expect(withCourseGroups(input, null)).toBe(input);
  });
});

describe("tag and glossary filters", () => {
  const tagged = [
    { ...node("a"), data: { ...node("a").data, tags: ["rag", "pattern"] } },
    { ...node("b"), data: { ...node("b").data, tags: ["eval", "concept"] } },
  ];
  const glossary = { terms: [], mentions: { bm25: ["b"] } };
  const all = facetsOf(null, tagged, glossary);

  it("a tag selects the pages carrying it, a term the pages mentioning it", () => {
    expect([...filterPrimaryIds(tagged, new Set(["tag:rag"]), all)!]).toEqual(["a"]);
    expect([...filterPrimaryIds(tagged, new Set(["term:bm25"]), all)!]).toEqual(["b"]);
  });

  it("are there before the curriculum is", () => {
    expect(all.has("course:ai")).toBe(false);
    expect(all.get("tag:concept")).toEqual(new Set(["b"]));
  });

  it("a facet is pending only while its source is missing", () => {
    expect(facetPending("course:ai", null, glossary)).toBe(true);
    expect(facetPending("course:ai", curriculum, null)).toBe(false);
    expect(facetPending("term:bm25", curriculum, null)).toBe(true);
    expect(facetPending("tag:rag", null, null)).toBe(false);
  });
});

describe("notes", () => {
  const withNotes: Curriculum = {
    ...curriculum,
    courses: [
      {
        id: "ai",
        title: "AI Eng",
        pageIds: ["a", "b", "c"],
        modules: [
          {
            id: "rag",
            title: "RAG",
            firstLesson: null,
            pageIds: ["a", "b", "c"],
            notes: [
              { id: "ai/rag/notes/01-bm25", title: "BM25", pageIds: ["a", "b"] },
              { id: "ai/rag/notes/02-empty", title: "Empty", pageIds: [] },
              { id: "ai/rag/notes/03-rerank", title: "Rerank", pageIds: ["c"] },
            ],
          },
        ],
      },
    ],
  };
  const glossary = {
    terms: [{ id: "bm25", label: "BM25", aliases: [], def: "", page: "b", mentions: 2 }, { id: "x", label: "X", aliases: [], def: "", page: "zz", mentions: 1 }],
    mentions: { bm25: ["a", "b"] },
  };

  it("a note is a filter on the pages it links; an empty note is none", () => {
    const f = facetsOf(withNotes);
    expect([...f.get("note:ai/rag/notes/01-bm25")!]).toEqual(["a", "b"]);
    expect(f.has("note:ai/rag/notes/02-empty")).toBe(false);
    expect(isFacetId("note:ai/rag/notes/01-bm25")).toBe(true);
  });

  it("rank groups hold modules, notes and terms, with each module's notes in reading order", () => {
    const { groups, readingOrder } = rankGroupsOf(withNotes, glossary);
    expect(groups.map((g) => g.id)).toEqual([
      "module:ai/rag",
      "note:ai/rag/notes/01-bm25",
      "note:ai/rag/notes/03-rerank",
      "term:bm25",
    ]);
    expect(readingOrder).toEqual([["note:ai/rag/notes/01-bm25", "note:ai/rag/notes/03-rerank"]]);
  });
});
