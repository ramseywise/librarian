import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { StudyHomeData } from "../../../courses/types";
import { StudyHome } from "../StudyHome";

const home: StudyHomeData = {
  today: "2026-11-07",
  due: 3,
  new: 5,
  modules: [
    { module: "c1/m1", title: "Module One", cards: { due: 2, new: 1 }, questions: { due: 1, new: 4 } },
    { module: "c1/m2", title: "Module Two", cards: { due: 0, new: 0 }, questions: { due: 0, new: 2 } },
  ],
  nextDrill: {
    id: "c1/m1/d1", title: "Join two tables", section: "", kind: "drill", summary: "",
    drill: { track: "sql", difficulty: "easy" }, course: "c1", track: "sql", reason: "weakest track",
  },
  lecture: { module: "c1/m1", title: "Module One", decks: [{ id: "c1/m1", title: "Overview" }, { id: "c1/m1/01-a", title: "Lecture A" }] },
};

function stub(body: unknown, status = 200) {
  const fetchMock = vi.fn(async () => new Response(JSON.stringify(body), { status }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("StudyHome", () => {
  it("shows the totals and links each module's cards and questions to their due views", async () => {
    const fetchMock = stub(home);
    render(<StudyHome />);
    expect(await screen.findByText("3 due today, 5 new.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/courses/study");
    expect(screen.getByRole("link", { name: "Flashcards (2 due, 1 new)" })).toHaveAttribute("href", "#/flashcards/c1/m1?due");
    expect(screen.getByRole("link", { name: "Quiz (1 due, 4 new)" })).toHaveAttribute("href", "#/quiz/c1/m1?due");
    // A module with no cards gets no flashcards link.
    expect(screen.getByRole("link", { name: "Quiz (0 due, 2 new)" })).toHaveAttribute("href", "#/quiz/c1/m2?due");
    expect(screen.getAllByRole("link", { name: /^Flashcards/ })).toHaveLength(1);
  });

  it("names the next drill and its track, and lists the lecture's decks", async () => {
    stub(home);
    render(<StudyHome />);
    expect(await screen.findByRole("link", { name: "Join two tables" })).toHaveAttribute("href", "#/practice");
    expect(screen.getByText(/sql, easy \(your weakest track\)/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Overview" })).toHaveAttribute("href", "#/slides/c1/m1");
    expect(screen.getByRole("link", { name: "Lecture A" })).toHaveAttribute("href", "#/slides/c1/m1/01-a");
  });

  it("says so when there is nothing due, no drill and no slides", async () => {
    stub({ today: "2026-11-07", due: 0, new: 0, modules: [], nextDrill: null, lecture: null });
    render(<StudyHome />);
    expect(await screen.findByText("Nothing due today.")).toBeInTheDocument();
    expect(screen.getByText("No flashcards or questions are due.")).toBeInTheDocument();
    expect(screen.getByText("No drills yet.")).toBeInTheDocument();
    expect(screen.getByText("No slides yet.")).toBeInTheDocument();
  });

  it("reports a failed request", async () => {
    stub({}, 500);
    render(<StudyHome />);
    expect(await screen.findByText(/Could not load the study queue: HTTP 500/)).toBeInTheDocument();
  });
});
