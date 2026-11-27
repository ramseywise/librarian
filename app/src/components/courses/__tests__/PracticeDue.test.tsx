import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { resetLearningForTests } from "../../../hooks/useLearning";
import { MasteryBar } from "../courseBits";
import { PracticeView } from "../PracticeView";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const outline = (id: string, title: string) => ({ id, title, section: "s", kind: "reading", summary: "sum", course: "ai", link: null });
const DUE = [{
  concept: { id: "chunking", title: "Chunking", summary: "Splitting text", domain: "rag" },
  strength: 0.31, due: true, reason: "last seen 9 days ago",
  lessons: [outline("ai/m/one", "Lesson one")], drills: [outline("ai/m/d1", "Split it")],
  decks: [{ id: "ai/m", title: "M cards" }],
}];

function stub(due: unknown, dueStatus = 200) {
  vi.stubGlobal("fetch", vi.fn(async (u: string) => {
    if (u.startsWith("/api/learning/next")) return json(due, dueStatus);
    return json([]);
  }));
}

beforeEach(() => resetLearningForTests());
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Due for review", () => {
  it("lists the weakest concepts with what to open for each", async () => {
    stub(DUE);
    const onOpenLesson = vi.fn();
    const onOpenConcept = vi.fn();
    render(<PracticeView onOpenLesson={onOpenLesson} onOpenConcept={onOpenConcept} />);
    const section = await screen.findByRole("region", { name: "Due for review" });
    expect(section.textContent).toContain("31%");
    expect(section.textContent).toContain("last seen 9 days ago");
    await userEvent.click(screen.getByRole("button", { name: "Chunking" }));
    expect(onOpenConcept).toHaveBeenCalledWith("chunking");
    await userEvent.click(screen.getByRole("button", { name: "Drill: Split it" }));
    expect(onOpenLesson).toHaveBeenCalledWith("ai/m/d1");
    expect(screen.getByRole("link", { name: "Recall: M cards" }).getAttribute("href")).toBe("#/flashcards/ai/m");
  });

  it("draws nothing when nothing is due or the request fails", async () => {
    stub([]);
    const { unmount } = render(<PracticeView onOpenLesson={vi.fn()} onOpenConcept={vi.fn()} />);
    await screen.findByText(/No drills yet/);
    expect(screen.queryByRole("region", { name: "Due for review" })).toBeNull();
    unmount();
    stub({ detail: "x" }, 500);
    render(<PracticeView onOpenLesson={vi.fn()} onOpenConcept={vi.fn()} />);
    await screen.findByText(/No drills yet/);
    expect(screen.queryByRole("region", { name: "Due for review" })).toBeNull();
  });
});

describe("MasteryBar", () => {
  it("says 'no data yet' for a null strength, never 0%", () => {
    render(<MasteryBar mastery={{ strength: null, concepts: 4, withEvidence: 0 }} />);
    expect(screen.getByRole("img").getAttribute("aria-label")).toBe("Mastery: no data yet");
    expect(screen.getByTestId("mastery").textContent).toContain("0 of 4 concepts practised");
    expect(screen.getByTestId("mastery").textContent).not.toContain("0%");
  });

  it("shows a percentage, and nothing for a module with no concepts", () => {
    const { rerender } = render(<MasteryBar mastery={{ strength: 0.5, concepts: 2, withEvidence: 1 }} />);
    expect(screen.getByRole("img").getAttribute("aria-label")).toBe("Mastery 50%");
    rerender(<MasteryBar mastery={{ strength: null, concepts: 0, withEvidence: 0 }} />);
    expect(screen.queryByTestId("mastery")).toBeNull();
    rerender(<MasteryBar mastery={undefined} />);
    expect(screen.queryByTestId("mastery")).toBeNull();
  });
});
