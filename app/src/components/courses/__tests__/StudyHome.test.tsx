import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { resetCourseCachesForTests } from "../../../hooks/useCourses";
import type { Course, CourseModule, LessonOutline } from "../types";
import { StudyHome } from "../StudyHome";

const lesson = (id: string, title: string, counts: Partial<LessonOutline> = {}): LessonOutline =>
  ({ id, title, section: "", kind: "lesson", summary: "", ...counts }) as LessonOutline;
const mod = (id: string, title: string, lessons: LessonOutline[], counts: Partial<CourseModule> = {}): CourseModule =>
  ({ id, title, summary: "", order: 1, readings: [], references: [], lessons, ...counts });

const courses: Course[] = [
  {
    id: "c1", title: "Course One", summary: "", order: 1, lessonCount: 3,
    modules: [
      mod("m1", "Module One", [
        lesson("c1/m1/a", "Lesson A", { flashcardCount: 4, quizCount: 3, problemCount: 2 }),
        lesson("c1/m1/b", "Lesson B"),
      ], { flashcardCount: 4, quizCount: 3, problemCount: 2 }),
      mod("m2", "Module Two", [lesson("c1/m2/a", "Lesson C")]),
    ],
  },
  {
    id: "c2", title: "Course Two", summary: "", order: 2, lessonCount: 1,
    modules: [mod("m1", "Module Three", [lesson("c2/m1/a", "Lesson D", { flashcardCount: 5 })], { flashcardCount: 5 })],
  },
];

function stub(body: unknown, status = 200) {
  const fetchMock = vi.fn(async () => new Response(JSON.stringify(body), { status }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  resetCourseCachesForTests();
});

describe("StudyHome", () => {
  it("lists each course's topics with a link per level, and leaves out a topic with nothing to study", async () => {
    const fetchMock = stub(courses);
    render(<StudyHome />);
    const one = within(await screen.findByRole("region", { name: "Course One" }));
    expect(fetchMock).toHaveBeenCalledWith("/api/courses", expect.anything());
    expect(one.getByRole("columnheader", { name: "Level 1 Multiple choice" })).toBeInTheDocument();
    expect(one.getByRole("link", { name: "Module One: multiple choice, 3 questions" })).toHaveAttribute("href", "#/quiz/c1/m1?choice");
    expect(one.getByRole("link", { name: "Module One: flashcards, 4 cards" })).toHaveAttribute("href", "#/flashcards/c1/m1");
    expect(one.getByRole("link", { name: "Module One: worked problems, 2 problems" })).toHaveAttribute("href", "#/quiz/c1/m1?worked");
    expect(one.queryByText("Module Two")).not.toBeInTheDocument();
    // A level the topic lacks is an empty cell, not a link.
    const two = within(screen.getByRole("region", { name: "Course Two" }));
    expect(two.getAllByRole("link", { name: /: / })).toHaveLength(1);
    expect(screen.queryByText(/due/i)).not.toBeInTheDocument();
  });

  it("links each topic to its module page, with nothing to expand or filter", async () => {
    stub(courses);
    render(<StudyHome />);
    expect(await screen.findByRole("link", { name: "Module One" })).toHaveAttribute("href", "#/courses/c1/m1");
    expect(screen.queryAllByRole("button")).toHaveLength(0);
  });

  it("says so when no course has anything to study", async () => {
    stub([]);
    render(<StudyHome />);
    expect(await screen.findByText("No flashcards or questions yet.")).toBeInTheDocument();
  });

  it("reports a failed request", async () => {
    stub({}, 500);
    render(<StudyHome />);
    expect(await screen.findByText(/Could not load the study topics: HTTP 500/)).toBeInTheDocument();
  });
});
