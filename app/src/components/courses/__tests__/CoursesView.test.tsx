import { act, cleanup, render, screen, waitFor, within } from "@testing-library/react";
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

  it("is where the course starts: outcomes, core then advanced modules, the guide and references last", async () => {
    const mod = (id: string, title: string, group: string) => ({ ...course.modules[0], id, title, group });
    const grouped: Course = {
      ...course,
      outcomes: ["Estimate honestly"],
      modules: [mod("c1/m1", "Frames", "core"), mod("c1/m2", "Stats", "core"), mod("c1/m3", "Bayes", "advanced")],
      guide: [
        { ...outline, id: "c1/00-start-here/readme", title: "Course One" },
        { ...outline, id: "c1/00-start-here/references", title: "References" },
      ],
      readingsCount: 12,
    };
    vi.stubGlobal("fetch", vi.fn(async (url: string) =>
      new Response(JSON.stringify(url === "/api/courses" ? [grouped] : []), { status: 200 })));
    render(<CoursesView route="c1" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByText("Estimate honestly")).toBeInTheDocument();
    const headings = screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent);
    expect(headings).toEqual(["By the end you can", "Core modules", "Advanced topics", "Guide and references"]);
    expect(within(screen.getByRole("region", { name: "Core modules" })).getAllByRole("button")).toHaveLength(2);
    expect(within(screen.getByRole("region", { name: "Advanced topics" })).getByRole("button")).toHaveTextContent("Bayes");
    expect(screen.queryByText(/Module \d/)).toBeNull();
    expect(screen.getByRole("link", { name: "Course guide" })).toHaveAttribute("href", "#/courses/c1/00-start-here/readme");
    expect(screen.getByRole("link", { name: "References" })).toHaveAttribute("href", "#/courses/c1/00-start-here/references");
  });

  it("opens a course on its readme, with each group's syllabus under its cards and no raw reading list", async () => {
    const mod = (id: string, title: string, group: string) => ({ ...course.modules[0], id, title, group });
    const grouped: Course = {
      ...course,
      outcomes: ["Estimate honestly"],
      modules: [mod("m1", "Frames", "core"), mod("m3", "Bayes", "advanced")],
      guide: [
        { ...outline, id: "c1/00-start-here/readme", title: "Course One" },
        { ...outline, id: "c1/00-start-here/references", title: "References" },
      ],
      readings: [{ title: "raw file name", source: "c1/sources/raw.pdf" }],
      readingsCount: 1,
    };
    const readme = {
      ...lesson, id: "c1/00-start-here/readme", title: "Course One",
      body: "# Course One\n\nThe lead.\n\n## What it is\n\nAn analyst owes an answer.\n\n## Course outcomes\n\n1. Listed twice otherwise\n\n"
        + "## Core modules\n\n| Module | Lecture |\n|---|---|\n| [Frames](../m1/readme.md) | [deck](../m1/slides/frames.pptx) |\n\n"
        + "## Units\n\n### [Frames](../m1/readme.md)\n\nThe unit text.\n\n## Rules of thumb\n\nCount first.",
    };
    vi.stubGlobal("fetch", vi.fn(async (url: string) =>
      new Response(JSON.stringify(url === "/api/courses" ? [grouped]
        : url === "/api/courses/lessons/c1/00-start-here/readme" ? readme : []), { status: 200 })));
    render(<CoursesView route="c1" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByText("An analyst owes an answer.")).toBeInTheDocument();
    const headings = screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent);
    expect(headings).toEqual(["By the end you can", "Core modules", "Advanced topics", "Rules of thumb", "References"]);
    expect(screen.getByText("The lead.")).toBeInTheDocument();
    // The syllabus row sits with its group, and its deck link opens the lecture.
    const core = within(screen.getByRole("region", { name: "Core modules" }));
    expect(core.getByRole("link", { name: "deck" })).toHaveAttribute("href", "#/slides/c1/m1");
    expect(screen.queryByText("Listed twice otherwise")).toBeNull();
    expect(screen.queryByText("The unit text.")).toBeNull();
    expect(screen.queryByRole("link", { name: "Course guide" })).toBeNull();
    expect(screen.queryByText("raw file name")).toBeNull();
    expect(screen.getByRole("link", { name: "References" })).toHaveAttribute("href", "#/courses/c1/00-start-here/references");
  });

  const studied: Course = {
    ...course,
    modules: [{
      ...course.modules[0], quizCount: 3, flashcardCount: 5, decks: [{ id: "c1/m1", title: "Module deck" }],
      wikiCount: 14,
      wiki: [{ id: "agents", title: "Agent Loops", summary: "How an agent loops." }],
    }],
  };
  const stub = (progress: unknown = {}) =>
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      const body = url === "/api/courses" ? [studied] : url === "/api/courses/study-progress" ? progress : { labs: [lab], canRun: false };
      return new Response(JSON.stringify(body), { status: 200 });
    }));

  it("lays the topic page out as lecture, test yourself, notes, hands-on, wiki, with nothing to open", async () => {
    stub();
    render(<CoursesView route="c1/c1/m1" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByRole("link", { name: "Level 1: multiple choice, 3 questions" })).toHaveAttribute("href", "#/quiz/c1/c1/m1?choice");
    expect(screen.getByRole("link", { name: "Level 2: flashcards, 5 cards" })).toHaveAttribute("href", "#/flashcards/c1/c1/m1");
    expect(screen.queryByRole("link", { name: /Level 3/ })).toBeNull();
    expect(screen.getByRole("link", { name: "Module deck" })).toHaveAttribute("href", "#/slides/c1/m1");
    const headings = screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent);
    expect(headings.slice(0, 5)).toEqual(["Lecture", "Test yourself", "Notes", "Hands-on", "Wiki"]);
    expect(screen.getByRole("link", { name: "Intro" })).toHaveAttribute("href", "#/courses/c1/m1/intro");
    expect(await screen.findByRole("link", { name: "Probability puzzles" })).toHaveAttribute("href", "#/labs/c1/m1/practice/puzzles");
    expect(screen.queryByRole("button", { expanded: true })).toBeNull();
  });

  it("says what the module teaches straight after the lecture", async () => {
    const taught = { ...studied, modules: [{ ...studied.modules[0], objectives: ["Build a confidence interval", "Read a p-value"] }] };
    vi.stubGlobal("fetch", vi.fn(async (url: string) =>
      new Response(JSON.stringify(url === "/api/courses" ? [taught] : url === "/api/courses/labs" ? { labs: [], canRun: false } : {}), { status: 200 })));
    render(<CoursesView route="c1/c1/m1" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByText("Build a confidence interval")).toBeInTheDocument();
    const headings = screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent);
    expect(headings.slice(0, 3)).toEqual(["Lecture", "After this module you can", "Test yourself"]);
  });

  it("opens on the module's readme and lists only the notes as notes", async () => {
    const part = (id: string, title: string, kind = "reading") => ({ ...outline, id: `c1/c1/m1/${id}`, title, kind });
    const full: Course = {
      ...studied,
      modules: [
        {
          ...studied.modules[0], objectives: ["Read a p-value"],
          decks: [{ id: "c1/c1/m1", title: "Frames lecture", parts: [{ n: 2, title: "Loading a table", summary: "Read it in", notes: ["01-frames"] }] }],
          lessons: [part("readme", "Module"), part("notes/01-frames", "Frames"), part("practice/puzzles/one", "Puzzle one", "notebook"),
            part("practice/extra", "Extra notebook", "notebook"), part("references", "References")],
        },
        { ...course.modules[0], id: "c1/m2", title: "What follows" },
      ],
    };
    const readme = { ...lesson, id: "c1/c1/m1/readme", title: "Module", body: "# Module\n\nWhat it is for.\n\n## Lecture\n\nStart with the deck.\n\n## The core\n\nFive steps.\n\n## Syllabus\n\n| Submodule | Study |\n|---|---|\n| **1. Load:** a table | [Frames](notes/01-frames.md) |\n\n## Next\n\nGo on." };
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      const body = url === "/api/courses" ? [full] : url === "/api/courses/labs" ? { labs: [lab], canRun: false }
        : url === "/api/courses/lessons/c1/c1/m1/readme" ? readme : {};
      return new Response(JSON.stringify(body), { status: 200 });
    }));
    // A link to the readme lands on the module's page.
    render(<CoursesView route="c1/c1/m1/readme" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByText("Five steps.")).toBeInTheDocument();
    // The syllabus carries the labs and sources, so the page ends on what to do next.
    const headings = screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent);
    expect(headings).toEqual(["Lecture", "The core", "Syllabus", "Test yourself", "Notes", "What's next"]);
    expect(screen.getByText("What it is for.")).toBeInTheDocument();
    expect(screen.queryByText("Start with the deck.")).toBeNull();
    expect(screen.queryByText("Go on.")).toBeNull();
    expect(screen.queryByText("Read a p-value")).toBeNull();
    // Once in the syllabus row and once in the notes list.
    expect(screen.getAllByRole("link", { name: "Frames" })).toHaveLength(2);
    expect(screen.queryByRole("link", { name: "Module" })).toBeNull();
    expect(screen.getByRole("link", { name: "Start: Frames" })).toHaveAttribute("href", "#/courses/c1/c1/m1/notes/01-frames");
    // The notes are grouped by submodule (the deck's parts), and what's next names the one it is in.
    const sub = within(screen.getByRole("region", { name: "Loading a table" }));
    expect(sub.getByRole("link", { name: "Slides" })).toHaveAttribute("href", "#/slides/c1/c1/m1?part=2");
    expect(sub.getByText("Read it in")).toBeInTheDocument();
    expect(sub.getByRole("link", { name: "Frames" })).toBeInTheDocument();
    expect(screen.getByText("In Loading a table")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "What follows" })).toHaveAttribute("href", "#/courses/c1/c1/m2");
  });

  it("without a syllabus, lists a notebook once: as its lab, or under hands-on when no lab opens it", async () => {
    const part = (id: string, title: string, kind = "reading") => ({ ...outline, id: `c1/c1/m1/${id}`, title, kind });
    const full: Course = {
      ...studied,
      modules: [{
        ...studied.modules[0],
        lessons: [part("notes/01-frames", "Frames"), part("practice/puzzles/one", "Puzzle one", "notebook"),
          part("practice/extra", "Extra notebook", "notebook"), part("references", "References")],
      }],
    };
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      const body = url === "/api/courses" ? [full] : url === "/api/courses/labs" ? { labs: [{ ...lab, id: "c1/c1/m1/practice/puzzles" }], canRun: false } : {};
      return new Response(JSON.stringify(body), { status: 200 });
    }));
    render(<CoursesView route="c1/c1/m1" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByRole("link", { name: "Probability puzzles" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Puzzle one" })).toBeNull();
    expect(screen.getByRole("link", { name: "Extra notebook" })).toHaveAttribute("href", "#/courses/c1/c1/m1/practice/extra");
    expect(screen.getByRole("link", { name: "References" })).toHaveAttribute("href", "#/courses/c1/c1/m1/references");
  });

  it("lists the wiki pages the lessons cite and links to them on the graph", async () => {
    stub();
    const onOpenConcept = vi.fn();
    render(<CoursesView route="c1/c1/m1" navigate={vi.fn()} onOpenConcept={onOpenConcept} onAsk={vi.fn()} />);
    await userEvent.click(await screen.findByRole("button", { name: /Agent Loops/ }));
    expect(onOpenConcept).toHaveBeenCalledWith("agents");
    expect(screen.getByText("How an agent loops.")).toBeInTheDocument();
    expect(screen.getByText(/13 more cited by these lessons/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Show on the graph" })).toHaveAttribute("href", "#/map/all?tags=module%3Ac1%2Fc1%2Fm1");
  });

  it("shows progress on each level from the attempts store", async () => {
    stub({ "c1/c1/m1": { choice: { total: 32, right: 20, redo: 4 }, cards: { total: 71, right: 25, redo: 0 } } });
    render(<CoursesView route="c1/c1/m1" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
    expect(await screen.findByText("20 of 32 right · 4 to redo")).toBeInTheDocument();
    expect(screen.getByText("25 of 71 known")).toBeInTheDocument();
    expect(screen.getAllByRole("meter").length).toBeGreaterThan(0);
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
