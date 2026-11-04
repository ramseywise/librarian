import { describe, expect, it } from "vitest";
import type { Node } from "@xyflow/react";
import type { Curriculum, WikiNodeData } from "../../types";
import { courseColor, domainColor } from "../../theme/domains";
import { applyView, curriculumSampleIds, filterPrimaryIds } from "../graphView";
import { facetsOf, withCourseGroups } from "../curriculum";

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
  ])("%s selects its pages", (id, expected) => {
    expect([...filterPrimaryIds(nodes, new Set([id]), facets)!].sort()).toEqual(expected);
  });

  it("plain directory and type tags still work alongside them", () => {
    expect([...filterPrimaryIds(nodes, new Set(["patterns"]), facets)!].sort()).toEqual(["c", "d", "e"]);
    expect([...filterPrimaryIds(nodes, new Set(["project", "module:ai/rag"]), facets)!].sort()).toEqual(["a", "p"]);
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

describe("curriculumSampleIds", () => {
  const degree = new Map([["e", 9], ["c", 5], ["d", 1], ["b", 3]]);

  it("takes projects, each course's main pages, and the best of each beyond directory", () => {
    expect([...curriculumSampleIds(nodes, degree, curriculum)].sort()).toEqual(["a", "b", "c", "e", "p"]);
  });

  it("ignores pages the graph no longer has", () => {
    const fewer = nodes.filter((n) => n.id !== "e");
    expect(curriculumSampleIds(fewer, degree, curriculum).has("e")).toBe(false);
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
