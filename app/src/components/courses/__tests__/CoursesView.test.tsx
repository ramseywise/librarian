import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Course, Lesson } from "../types";
import { resetProgressStoreForTests } from "../../../hooks/useCourseProgress";
import { resetCourseCachesForTests } from "../../../hooks/useCourses";
import { CoursesView } from "../CoursesView";

const outline = { id: "c1/m1/intro", title: "Intro", section: "", kind: "reading", summary: "" };
const course: Course = {
  id: "c1", title: "Course One", summary: "", order: 1, lessonCount: 1,
  modules: [{ id: "c1/m1", title: "Module", summary: "", order: 1, readings: [], references: [], lessons: [outline] }],
};
const lesson: Lesson = {
  ...outline, course: "c1", module: "c1/m1", source: "", concepts: [], prev: null, next: null,
  body: "## First heading\n\ntext\n\n## Second heading\n\nmore",
};

const lab = {
  id: "c1/m1/practice/puzzles", title: "Probability puzzles", course: "c1", module: "c1/m1", path: "practice/puzzles",
  purpose: "Simulate the classics", pattern: "", language: "python", runsOffline: true, hasRun: true, hasCheck: false, notes: [],
};

function mockFetch() {
  return vi.fn(async (url: string) => {
    const body = url === "/api/courses" ? [course]
      : url === "/api/courses/labs" ? { labs: [lab], canRun: false }
      : url.startsWith("/api/courses/lessons/") ? lesson : [];
    return new Response(JSON.stringify(body), { status: 200 });
  });
}

class FakeObserver {
  observe() {}
  disconnect() {}
  unobserve() {}
}

beforeEach(() => {
  localStorage.clear();
  resetProgressStoreForTests();
  resetCourseCachesForTests();
  vi.stubGlobal("fetch", mockFetch());
  vi.stubGlobal("IntersectionObserver", FakeObserver);
  Element.prototype.scrollIntoView = vi.fn();
  Element.prototype.scrollTo = vi.fn() as unknown as Element["scrollTo"];
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("CoursesView course page", () => {
  it("opens the course page from a course card, even with a lesson already visited", async () => {
    const visited = { lessons: { "c1/m1/intro": { state: "opened", updatedAt: "2026-11-16T10:00:00Z" } } };
    vi.stubGlobal("fetch", vi.fn(async (url: string) =>
      new Response(JSON.stringify(url === "/api/courses" ? [course] : url === "/api/courses/progress" ? visited : []), { status: 200 })));
    const navigate = vi.fn();
    render(<CoursesView route="" navigate={navigate} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    await userEvent.click(await screen.findByRole("button", { name: /Course One/ }));
    await act(async () => {}); // let the progress request settle
    await userEvent.click(screen.getByRole("button", { name: /Course One/ }));
    expect(navigate).toHaveBeenCalledWith("/courses/c1");
  });

  it("shows each module as a card that opens the module's page", async () => {
    const navigate = vi.fn();
    render(<CoursesView route="c1" navigate={navigate} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    const card = await screen.findByRole("button", { name: /Module/ });
    await waitFor(() => expect(card).toHaveTextContent("1 lessons · 1 labs"));
    await userEvent.click(card);
    expect(navigate).toHaveBeenCalledWith("/courses/c1/c1/m1");
  });

  it("shows a module's study levels, lessons and labs together, with nothing to open", async () => {
    const studied: Course = {
      ...course,
      modules: [{ ...course.modules[0], quizCount: 3, flashcardCount: 5, decks: [{ id: "c1/m1", title: "Module deck" }] }],
    };
    vi.stubGlobal("fetch", vi.fn(async (url: string) =>
      new Response(JSON.stringify(url === "/api/courses" ? [studied] : { labs: [lab], canRun: false }), { status: 200 })));
    render(<CoursesView route="c1/c1/m1" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByRole("link", { name: "Level 1: multiple choice, 3 questions" })).toHaveAttribute("href", "#/quiz/c1/c1/m1?choice");
    expect(screen.getByRole("link", { name: "Level 2: flashcards, 5 cards" })).toHaveAttribute("href", "#/flashcards/c1/c1/m1");
    expect(screen.queryByRole("link", { name: /Level 3/ })).toBeNull();
    expect(screen.getByRole("link", { name: /Module deck/ })).toHaveAttribute("href", "#/slides/c1/m1");
    expect(screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent).slice(0, 4)).toEqual(["Lectures", "Lessons", "Study", "Labs"]);
    expect(screen.getByRole("link", { name: "Intro" })).toHaveAttribute("href", "#/courses/c1/m1/intro");
    expect(await screen.findByRole("link", { name: "Probability puzzles" })).toHaveAttribute("href", "#/labs/c1/m1/practice/puzzles");
    expect(screen.queryByRole("button", { expanded: true })).toBeNull();
  });
});

describe("CoursesView lesson", () => {
  it("keeps heading DOM nodes when progress changes (TOC observer stays attached)", async () => {
    const navigate = vi.fn();
    render(<CoursesView route="c1/m1/intro" navigate={navigate} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    const before = await screen.findByRole("heading", { name: "First heading" });
    await userEvent.click(screen.getByRole("button", { name: "Mark as complete" }));
    await waitFor(() => expect(screen.getByRole("button", { name: /Completed/ })).toBeInTheDocument());
    const after = screen.getByRole("heading", { name: "First heading" });
    expect(after).toBe(before);
    expect(before.isConnected).toBe(true);
  });

  it("sets the document title from the lesson and course", async () => {
    render(<CoursesView route="c1/m1/intro" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    await screen.findByRole("heading", { name: "First heading" });
    await waitFor(() => expect(document.title).toBe("Intro · Course One · Librarian"));
  });

  it("lists the page's headings beside the lesson, with nothing to open", async () => {
    render(<CoursesView route="c1/m1/intro" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    await screen.findByRole("heading", { name: "First heading" });
    const toc = await screen.findByRole("navigation", { name: "On this page" });
    expect(toc).toHaveTextContent("First heading");
    expect(toc).toHaveTextContent("Second heading");
    expect(screen.queryByRole("button", { name: /page contents/ })).toBeNull();
  });
});
