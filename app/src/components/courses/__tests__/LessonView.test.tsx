import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Lesson } from "../types";
import { LessonView } from "../LessonView";

const drill: Lesson = {
  id: "programming/ts/group-by", title: "Typed groupBy", section: "Types", kind: "drill", summary: "",
  drill: { track: "typescript", difficulty: "medium", timebox_min: 20 },
  course: "programming", module: "programming/ts", source: "", concepts: [], prev: null, next: null,
  body: "## Prompt\n\nDo it.\n\n<details>\n<summary>Solution</summary>\n\n```ts\nconst secret = 42;\n```\n\n</details>\n\n## Notes\n\nAfter.",
};

beforeEach(() => {
  sessionStorage.clear();
  Element.prototype.scrollTo = vi.fn() as unknown as Element["scrollTo"];
});
afterEach(cleanup);

const renderLesson = () => render(
  <LessonView lesson={drill} courseTitle="Programming" done={false} onMarkDone={vi.fn()} onOpen={vi.fn()}
    onOpenConcept={vi.fn()} onAsk={vi.fn()} onToc={vi.fn()} onActiveHeading={vi.fn()} />,
);

describe("LessonView drill", () => {
  it("keeps the solution hidden until asked for, with raw HTML enabled", async () => {
    renderLesson();
    expect(screen.queryByText(/secret = 42/)).toBeNull();
    expect(screen.getByRole("heading", { name: "Notes" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Show solution" }));
    expect(screen.getByText(/secret = 42/)).toBeInTheDocument();
    expect(document.querySelector(".lesson-prose details")).toBeNull();
  });

  it("shows a timer from the timebox and keeps it in sessionStorage", async () => {
    renderLesson();
    expect(screen.getByRole("timer")).toHaveTextContent("20:00");
    await userEvent.click(screen.getByRole("button", { name: "Start" }));
    expect(screen.getByRole("button", { name: "Pause" })).toBeInTheDocument();
    expect(sessionStorage.getItem("librarian.timer.programming/ts/group-by")).toContain("startedAt");
    await userEvent.click(screen.getByRole("button", { name: "Pause" }));
    cleanup();
    renderLesson();
    expect(screen.getByRole("button", { name: "Resume" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(sessionStorage.getItem("librarian.timer.programming/ts/group-by")).toBeNull();
  });
});

describe("LessonView report", () => {
  it("posts a lesson report with the lesson id", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ id: "f1" }), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    renderLesson();
    await userEvent.click(screen.getByRole("button", { name: /Report or suggest a change to this lesson/ }));
    await userEvent.type(screen.getByRole("textbox"), "unclear");
    await userEvent.click(screen.getByRole("button", { name: "Send" }));
    await screen.findByText(/your note was sent/);
    const post = (fetchMock.mock.calls as unknown as [string, RequestInit][]).find(([, i]) => i?.method === "POST");
    expect(post?.[0]).toBe("/api/feedback");
    expect(JSON.parse(String(post?.[1].body))).toEqual({ kind: "lesson", target: "programming/ts/group-by", body: "unclear" });
    vi.unstubAllGlobals();
  });
});

describe("LessonView parts", () => {
  const lab = {
    id: "ds/01-m/practice/importance_noise.py", title: "Importance noise", course: "ds", module: "01-m",
    path: "practice/importance_noise.py", purpose: "P", pattern: "evaluation", language: "python",
    runsOffline: true, hasRun: true, hasCheck: false,
  };
  const body = [
    "## Idea", "", "The idea in words.", "",
    "```python", "a = 1", "b = 2", "c = a + b", "print(c)", "```", "",
    "## Try it", "", "1. Change b.", "", "<details>", "<summary>Answers</summary>", "", "Seven.", "", "</details>", "", "---", "",
    "## Interview checklist", "", "| Prompt | Answer |", "|---|---|", "| Why add? | To get three |",
  ].join("\n");
  const renderNote = () => render(
    <LessonView lesson={{ ...drill, kind: "reading", drill: undefined, labs: [lab], quizCount: 2, body }} courseTitle="DS" done={false}
      decks={[{ id: "programming/ts", title: "Classical ML" }, { id: "programming/ts/other-note", title: "Other" }]}
      onMarkDone={vi.fn()} onOpen={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} onToc={vi.fn()} onActiveHeading={vi.fn()} />,
  );

  it("opens on the lecture: the deck, the objectives and the prose, without the code, exercises or answers", () => {
    renderNote();
    expect(screen.getByRole("tab", { name: "Lecture" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("link", { name: /Lecture deck: Classical ML/ })).toHaveAttribute("href", "#/slides/programming/ts");
    expect(screen.queryByRole("link", { name: /Lecture deck: Other/ })).toBeNull();
    expect(screen.getByText("The idea in words.")).toBeInTheDocument();
    expect(screen.queryByText(/c = a \+ b/)).toBeNull();
    expect(screen.queryByText("Change b.")).toBeNull();
    expect(screen.getByRole("region", { name: "Objectives" })).toHaveTextContent("Why add?");
    expect(screen.queryByText("To get three")).toBeNull();
  });

  it("puts the levels and the review questions on Study", async () => {
    renderNote();
    await userEvent.click(screen.getByRole("tab", { name: "Study" }));
    expect(screen.getByRole("link", { name: "Level 1: multiple choice, 2 questions" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Review questions" })).toBeInTheDocument();
    expect(screen.getByText("Why add?")).toBeInTheDocument();
    expect(screen.queryByText("The idea in words.")).toBeNull();
  });

  it("puts the labs, the exercises and the code on Labs", async () => {
    renderNote();
    await userEvent.click(screen.getByRole("tab", { name: "Labs" }));
    expect(screen.getByRole("link", { name: /Importance noise/ })).toHaveAttribute("href", "#/labs/ds/01-m/practice/importance_noise.py");
    expect(screen.getByText("Change b.")).toBeInTheDocument();
    expect(screen.getByText(/c = a \+ b/)).toBeInTheDocument();
    expect(screen.queryByText("Seven.")).toBeNull();
    expect(document.querySelector("details")).toBeNull();
    await userEvent.click(screen.getByRole("button", { name: "Show answers" }));
    expect(screen.getByText("Seven.")).toBeInTheDocument();
  });

  it("leaves the answers to the flashcards when the note has them", async () => {
    render(
      <LessonView lesson={{ ...drill, kind: "reading", drill: undefined, flashcardCount: 1, body }} courseTitle="DS" done={false}
        onMarkDone={vi.fn()} onOpen={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} onToc={vi.fn()} onActiveHeading={vi.fn()} />,
    );
    await userEvent.click(screen.getByRole("tab", { name: "Study" }));
    expect(screen.queryByRole("heading", { name: "Review questions" })).toBeNull();
    expect(screen.queryByText("To get three")).toBeNull();
  });

  it("opens with the lecture made for this note when the module has one", () => {
    render(
      <LessonView lesson={{ ...drill, kind: "reading", drill: undefined, body }} courseTitle="DS" done={false}
        decks={[{ id: "programming/ts", title: "Whole" }, { id: "programming/ts/group-by", title: "Grouping", subtitle: "Why group" }]}
        onMarkDone={vi.fn()} onOpen={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} onToc={vi.fn()} onActiveHeading={vi.fn()} />,
    );
    expect(screen.getByRole("link", { name: /Lecture deck: Grouping/ })).toHaveTextContent("Why group");
    expect(screen.queryByRole("link", { name: /Lecture deck: Whole/ })).toBeNull();
  });

  it("opens Labs from a code link in the lecture", async () => {
    renderNote();
    await userEvent.click(screen.getByRole("link", { name: /Code 1 in Labs/ }));
    expect(screen.getByRole("tab", { name: "Labs" })).toHaveAttribute("aria-selected", "true");
  });
});
