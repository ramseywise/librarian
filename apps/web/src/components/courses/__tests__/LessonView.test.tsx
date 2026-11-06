import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Lesson } from "../../../courses/types";
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
  <LessonView lesson={drill} courseTitle="Programming" done={false} onToggleDone={vi.fn()} onOpen={vi.fn()}
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
