import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { resetProgressStoreForTests } from "../../hooks/useCourseProgress";
import { resetCourseCachesForTests } from "../../hooks/useCourses";
import { AppNav } from "../AppNav";

const lesson = (id: string, title: string) => ({ id, title, section: "", kind: "reading", summary: "" });
const courses = [
  {
    id: "ds", title: "Data Science", summary: "", order: 1, lessonCount: 2,
    modules: [
      { id: "01-ml", title: "Classical ML", summary: "", order: 1, readings: [], references: [], lessons: [lesson("ds/01-ml/notes/trees", "Trees")] },
      { id: "02-dl", title: "Deep Learning", summary: "", order: 2, readings: [], references: [], lessons: [lesson("ds/02-dl/notes/cnn", "CNNs")] },
    ],
  },
  { id: "de", title: "Data Engineering", summary: "", order: 2, lessonCount: 0, modules: [] },
];

beforeEach(() => {
  resetProgressStoreForTests();
  resetCourseCachesForTests();
  vi.stubGlobal("fetch", vi.fn(async (url: string) =>
    new Response(JSON.stringify(url === "/api/courses" ? courses : {}), { status: 200 })));
  Element.prototype.scrollIntoView = vi.fn();
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const renderNav = (route: string) => render(<AppNav id="nav" route={route} open={false} />);
const current = () => screen.getAllByRole("link").filter((a) => a.getAttribute("aria-current") === "page").map((a) => a.textContent);

describe("AppNav", () => {
  it("lists the four sections and every course, with no module until a course is open", async () => {
    renderNav("/");
    expect(await screen.findByRole("link", { name: "Data Engineering" })).toHaveAttribute("href", "#/courses/de");
    for (const [name, href] of [["Graph", "#/"], ["Courses", "#/courses"], ["Study", "#/study"], ["Labs", "#/labs"]]) {
      expect(screen.getByRole("link", { name })).toHaveAttribute("href", href);
    }
    expect(screen.queryByRole("link", { name: "Classical ML" })).toBeNull();
    expect(current()).toEqual(["Graph"]);
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("shows the open course's modules and the open module's lessons, marking the lesson being read", async () => {
    renderNav("/courses/ds/01-ml/notes/trees");
    expect(await screen.findByRole("link", { name: "Trees" })).toHaveAttribute("href", "#/courses/ds/01-ml/notes/trees");
    expect(screen.getByRole("link", { name: "Deep Learning" })).toHaveAttribute("href", "#/courses/ds/02-dl");
    expect(screen.queryByRole("link", { name: "CNNs" })).toBeNull();
    expect(current()).toEqual(["Trees"]);
    for (const name of ["Courses", "Data Science", "Classical ML"]) {
      expect(screen.getByRole("link", { name })).toHaveClass("is-within");
    }
  });

  it("keeps the module open while its deck is showing", async () => {
    renderNav("/slides/ds/01-ml/lecture-1");
    expect(await screen.findByRole("link", { name: "Trees" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Classical ML" })).toHaveClass("is-within");
  });

  it("marks Study for a quiz and Labs for a lab", async () => {
    const { unmount } = renderNav("/quiz/ds/01-ml?choice");
    expect(await screen.findByRole("link", { name: "Study" })).toHaveClass("is-within");
    unmount();
    renderNav("/labs");
    expect(current()).toEqual(["Labs"]);
  });
});
