import { describe, expect, it } from "vitest";
import { lessonSections, moduleNotes, subsectionOf } from "../sections";
import type { CourseModule, LessonOutline } from "../types";

const lesson = (id: string, section = "", kind = "reading"): LessonOutline => ({ id, title: id, section, kind, summary: "" });

describe("lessonSections", () => {
  it("groups lessons by the top folder of their section, in first-appearance order", () => {
    const a = lesson("c/m/b/readme", "B");
    const sections = lessonSections([lesson("c/m/a/questions", "A"), a, lesson("c/m/a/readme", "A"), lesson("c/m/b/examples/x", "B / Examples")]);
    expect(sections.map((s) => [s.title, s.lessons.length, s.first.id])).toEqual([["A", 2, "c/m/a/readme"], ["B", 2, "c/m/b/readme"]]);
    expect(subsectionOf(sections[1].lessons[1])).toBe("Examples");
    expect(subsectionOf(a)).toBe("");
  });

  it("is empty when every lesson sits in one folder", () => {
    expect(lessonSections([lesson("c/m/notes/1", "Notes"), lesson("c/m/notes/2", "Notes")])).toEqual([]);
  });
});

describe("moduleNotes", () => {
  it("leaves out the module's readme and references, drills and practice files", () => {
    const m = { lessons: [
      lesson("c/m/readme"), lesson("c/m/references"), lesson("c/m/notes/1"), lesson("c/m/d", "", "drill"),
      lesson("c/m/practice/p"), lesson("c/m/nb", "", "notebook"), lesson("c/m/a/readme"),
    ] } as CourseModule;
    expect(moduleNotes("c/m", m).map((l) => l.id)).toEqual(["c/m/notes/1", "c/m/a/readme"]);
  });
});
