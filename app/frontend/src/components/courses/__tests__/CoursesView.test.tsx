import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Course, Lesson } from "../../../courses/types";
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

function mockFetch() {
  return vi.fn(async (url: string) => {
    const body = url === "/api/courses" ? [course] : url.startsWith("/api/courses/lessons/") ? lesson : [];
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

  it("exposes the page-contents toggle as its own button, not nested in the lesson button", async () => {
    render(<CoursesView route="c1/m1/intro" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    await screen.findByRole("heading", { name: "First heading" });
    const toggle = await screen.findByRole("button", { name: "Hide page contents" });
    expect(toggle).toHaveAttribute("aria-expanded", "true");
    expect(toggle.closest("button")).toBe(toggle);
    expect(toggle.parentElement?.closest("button")).toBeNull();
    await act(async () => { await userEvent.click(toggle); });
    expect(screen.getByRole("button", { name: "Show page contents" })).toHaveAttribute("aria-expanded", "false");
  });
});
