import { describe, expect, it } from "vitest";
import { lessonsOf, moduleGroups, splitCourseReadme, splitOverview, submoduleOf } from "../courseLogic";
import type { Course, CourseModule, Lesson } from "../types";

const mod = (id: string, group?: string, lessons: string[] = []) =>
  ({ id, group, lessons: lessons.map((l) => ({ id: l })) }) as unknown as CourseModule;
const readme = (body: string, title = "Course") => ({ id: "c/readme", title, body }) as unknown as Lesson;

describe("lessonsOf", () => {
  it("flattens a course's lessons in module order", () => {
    const c = { modules: [mod("a", undefined, ["a/1", "a/2"]), mod("b", undefined, ["b/1"])] } as unknown as Course;
    expect(lessonsOf(c).map((l) => l.id)).toEqual(["a/1", "a/2", "b/1"]);
  });
});

describe("moduleGroups", () => {
  it("keeps a course with no groups as one unlabelled group", () => {
    const g = moduleGroups([mod("a"), mod("b")]);
    expect(g).toHaveLength(1);
    expect(g[0].title).toBe("");
    expect(g[0].modules.map((m) => m.id)).toEqual(["a", "b"]);
  });

  it("starts a group when the key changes, and titles them", () => {
    const g = moduleGroups([mod("a", "core"), mod("b", "core"), mod("c", "advanced"), mod("d", "other")]);
    expect(g.map((x) => [x.key, x.title, x.modules.length])).toEqual([
      ["core", "Core modules", 2],
      ["advanced", "Advanced topics", 1],
      ["other", "More", 1],
    ]);
  });

  it("labels a single named group too", () => {
    expect(moduleGroups([mod("a", "core")])[0].title).toBe("Core modules");
  });

  it("is empty for no modules", () => {
    expect(moduleGroups([])).toEqual([]);
  });
});

describe("splitCourseReadme", () => {
  const body = [
    "# Course", "", "Lead.", "",
    "## What it is", "", "It is this.", "",
    "## Course outcomes", "", "- dropped", "",
    "## Core modules", "", "| syllabus |", "",
    "## Advanced topics", "", "| more |", "",
    "## Units", "", "dropped too", "",
    "## Sources", "", "Rest.", "",
  ].join("\n");

  it("sorts sections into intro, per-group syllabus and the rest, dropping outcomes and units", () => {
    const r = splitCourseReadme(readme(body));
    expect(r.intro).toContain("Lead.");
    expect(r.intro).toContain("It is this.");
    expect(r.intro).not.toContain("# Course");
    expect(Object.keys(r.groups).sort()).toEqual(["advanced", "core"]);
    expect(r.groups.core).toContain("| syllabus |");
    expect(r.rest).toContain("## Sources");
    expect(r.rest).not.toContain("dropped");
  });
});

describe("splitOverview", () => {
  it("returns the whole body as the lead when there are no sections", () => {
    expect(splitOverview(readme("Just text.\n"))).toEqual({ lead: "Just text.\n", rest: "" });
  });

  it("drops the Lecture and Next sections and keeps the rest below the lead", () => {
    const r = splitOverview(readme("Lead.\n\n## Lecture\n\nx\n\n## Syllabus\n\n| a |\n\n## Next\n\ny\n"));
    expect(r.lead).toBe("Lead.\n\n");
    expect(r.rest).toContain("## Syllabus");
    expect(r.rest).not.toMatch(/## (Lecture|Next)/);
  });
});

describe("submoduleOf", () => {
  const body = "| **1. Load**: x | [trees](notes/trees.md) |\n| **2. Fit** | [cnn](../notes/cnn#top) |\n| other |";
  it("reads the syllabus row a note belongs to", () => {
    expect(submoduleOf(body, "ds/01/notes/trees")).toBe("1. Load");
    expect(submoduleOf(body, "ds/01/notes/cnn")).toBe("2. Fit");
  });
  it("is null when no row names the note", () => {
    expect(submoduleOf(body, "ds/01/notes/missing")).toBeNull();
  });
});
