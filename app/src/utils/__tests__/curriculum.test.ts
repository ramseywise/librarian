import { describe, expect, it } from "vitest";
import type { Node } from "@xyflow/react";
import type { Curriculum, WikiNodeData } from "../../types";
import { courseColor, domainColor } from "../../theme/domains";
import { applyView, filterPrimaryIds } from "../graphView";
import { facetPending, facetsOf, withCourseGroups } from "../curriculum";

function node(id: string, domain = "rag", typeTag = "concept"): Node<WikiNodeData> {
  return {
    id,
    position: { x: 0, y: 0 },
    data: { title: id, tags: [], domain: [domain], typeTag, summary: "", updated: "", path: "", dimmed: false, highlighted: false },
  };
}

const curriculum: Curriculum = {
  courses: [
    { id: "ai", title: "AI Eng", pageIds: ["a", "b"], modules: [{ id: "rag", title: "RAG", firstLesson: null, pageIds: ["a"] }] },
    { id: "data", title: "Data", pageIds: ["b"], modules: [] },
  ],
  beyond: [{ domain: "patterns", pageIds: ["c", "d", "e"] }],
  primaryCourse: { a: "ai", b: "ai" },
  stale: false,
};
const facets = facetsOf(curriculum);
const nodes = [node("a"), node("b"), node("c", "patterns"), node("d", "patterns"), node("e", "patterns"), node("p", "projects", "project")];

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
