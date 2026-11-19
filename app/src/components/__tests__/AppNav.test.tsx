import { cleanup, render, screen, within } from "@testing-library/react";
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
const current = () => screen.getAllByRole("link").filter((a) => a.getAttribute("aria-current") === "page").map((a) => a.querySelector(".grow")?.textContent ?? a.textContent);

describe("AppNav", () => {
  it("lists the four sections, and under Courses every course as a group label over its modules", async () => {
    renderNav("/");
    expect(await screen.findByRole("link", { name: "Data Engineering" })).toHaveAttribute("href", "#/courses/de");
    for (const [name, href] of [["Graph", "#/"], ["Courses", "#/courses"], ["Study", "#/study"], ["Labs", "#/labs"]]) {
      expect(screen.getByRole("link", { name })).toHaveAttribute("href", href);
    }
    const group = within(screen.getByRole("group", { name: "Data Science" }));
    expect(group.getByRole("link", { name: "Classical ML" })).toHaveAttribute("href", "#/courses/ds/01-ml");
    expect(group.getByRole("link", { name: "Deep Learning" })).toHaveAttribute("href", "#/courses/ds/02-dl");
    expect(current()).toEqual(["Graph"]);
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("heads a course's modules with Core and Advanced when the course sorts them", async () => {
    const grouped = [{ ...courses[0], modules: [{ ...courses[0].modules[0], group: "core" }, { ...courses[0].modules[1], group: "advanced" }] }];
    vi.stubGlobal("fetch", vi.fn(async (url: string) =>
      new Response(JSON.stringify(url === "/api/courses" ? grouped : {}), { status: 200 })));
    renderNav("/courses");
    const group = await screen.findByRole("group", { name: "Data Science" });
    expect(group.textContent).toMatch(/Core.*Classical ML.*Advanced.*Deep Learning/);
  });

  it("shows each module's lesson count and no lessons, even for the module being read", async () => {
    const { container } = renderNav("/courses/ds/01-ml/notes/trees");
    await screen.findByRole("link", { name: "Classical ML" });
    expect(screen.queryByRole("link", { name: "Trees" })).toBeNull();
    expect([...container.querySelectorAll(".sidenav-count")].map((n) => n.textContent)).toEqual(["1", "1"]);
    expect(container.querySelector(".check")).toBeNull();
  });

  it("lists the folders of a course's only module under it, each opening on its readme", async () => {
    const inRound = (id: string, title: string, section: string) => ({ ...lesson(`iv/rounds/${id}`, title), section });
    const rounds = [{ ...courses[0], id: "iv", title: "Interviewing", modules: [{ ...courses[0].modules[0], id: "rounds", title: "Rounds", lessons: [
      inRound("behavioral/readme", "Behavioral Round", "Behavioral"), inRound("case-study/readme", "Case Study", "Case study"),
      inRound("behavioral/questions", "Questions", "Behavioral"), inRound("case-study/examples/a", "A", "Case study / Examples"),
    ] }] }];
    vi.stubGlobal("fetch", vi.fn(async (url: string) =>
      new Response(JSON.stringify(url === "/api/courses" ? rounds : {}), { status: 200 })));
    renderNav("/courses/iv/rounds/case-study/examples/a");
    const group = within(await screen.findByRole("group", { name: "Interviewing" }));
    expect(group.getByRole("link", { name: "Behavioral" })).toHaveAttribute("href", "#/courses/iv/rounds/behavioral/readme");
    expect(group.getByRole("link", { name: "Case study" })).toHaveClass("is-current");
    expect(group.getByRole("link", { name: "Behavioral" })).not.toHaveClass("is-current");
  });

  it("fills the current module's row, and marks it as the page only on the module page", async () => {
    const { unmount } = renderNav("/courses/ds/01-ml/notes/trees");
    expect(await screen.findByRole("link", { name: "Classical ML" })).toHaveClass("is-current");
    expect(screen.getByRole("link", { name: "Deep Learning" })).not.toHaveClass("is-current");
    expect(current()).toEqual([]);
    unmount();
    renderNav("/courses/ds/02-dl");
    await screen.findByRole("link", { name: "Deep Learning" });
    expect(current()).toEqual(["Deep Learning"]);
    expect(screen.getByRole("link", { name: "Data Science" })).toHaveClass("is-within");
    expect(screen.getByRole("link", { name: "Courses" })).toHaveClass("is-within");
  });

  it("keeps the module filled while its deck is showing", async () => {
    renderNav("/slides/ds/01-ml/lecture-1");
    expect(await screen.findByRole("link", { name: "Classical ML" })).toHaveClass("is-current");
  });

  it("marks Study for a quiz and Labs for a lab", async () => {
    const { unmount } = renderNav("/quiz/ds/01-ml?choice");
    expect(await screen.findByRole("link", { name: "Study" })).toHaveClass("is-within");
    unmount();
    renderNav("/labs");
    expect(current()).toEqual(["Labs"]);
  });
});
