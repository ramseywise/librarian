import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { resetLearningForTests } from "../../../hooks/useLearning";
import { ConceptView } from "../ConceptView";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const lesson = (id: string, link: string | null) => ({ id, title: `T ${id}`, section: "s", kind: "reading", summary: "sum", course: "ai", link });
const HUB = {
  id: "chunking", title: "Chunking", summary: "Splitting text", domain: "rag",
  mastery: { strength: 0.42, recency: 1, lastSeen: "2026-11-01T00:00:00Z", due: true, evidence: "weak", counts: { lessons: 1, drills: 0, cards: 2 } },
  lessons: [lesson("ai/m/one", "explicit"), lesson("ai/m/two", "semantic")],
  drills: [lesson("ai/m/drill", null)],
  decks: [{ id: "ai/m", title: "M cards" }],
  catalogReady: true,
};

beforeEach(() => resetLearningForTests());
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("ConceptView", () => {
  it("shows mastery, the spokes and how each lesson is tied to the page", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(HUB)));
    render(<ConceptView id="chunking" navigate={vi.fn()} onShowInGraph={vi.fn()} />);
    expect(await screen.findByRole("heading", { name: "Chunking" })).toBeTruthy();
    expect(screen.getByText(/Strength 42%/)).toBeTruthy();
    expect(screen.getByText(/Weak evidence only/)).toBeTruthy();
    expect(screen.getByText(/ai · linked/)).toBeTruthy();
    expect(screen.getByText(/ai · similar text/)).toBeTruthy();
    expect(screen.getByRole("link", { name: "M cards" }).getAttribute("href")).toBe("#/flashcards/ai/m");
  });

  it("opens a lesson and the graph from its buttons", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(HUB)));
    const navigate = vi.fn();
    const onShowInGraph = vi.fn();
    render(<ConceptView id="chunking" navigate={navigate} onShowInGraph={onShowInGraph} />);
    await userEvent.click(await screen.findByRole("button", { name: "T ai/m/one" }));
    expect(navigate).toHaveBeenCalledWith("/courses/ai/m/one");
    await userEvent.click(screen.getByRole("button", { name: "Show in graph" }));
    expect(onShowInGraph).toHaveBeenCalledWith("chunking");
  });

  it("says there is no evidence rather than a strength of zero", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ ...HUB, mastery: null })));
    render(<ConceptView id="chunking" navigate={vi.fn()} onShowInGraph={vi.fn()} />);
    expect(await screen.findByText("No study evidence recorded for this page.")).toBeTruthy();
  });

  it("holds back the 'no lesson' claims while the courses build", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ ...HUB, lessons: [], drills: [], decks: [], catalogReady: false })));
    render(<ConceptView id="chunking" navigate={vi.fn()} onShowInGraph={vi.fn()} />);
    expect(await screen.findByRole("status")).toBeTruthy();
    expect(screen.queryByText("No lesson links this page.")).toBeNull();
  });

  it("says so for a page that is not there (private, retired or unknown)", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ detail: "no such page" }, 404)));
    render(<ConceptView id="secret" navigate={vi.fn()} onShowInGraph={vi.fn()} />);
    expect(await screen.findByText("No such page.")).toBeTruthy();
  });

  it("offers a retry when the server fails", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("x", { status: 500 })));
    render(<ConceptView id="chunking" navigate={vi.fn()} onShowInGraph={vi.fn()} />);
    expect(await screen.findByText(/Could not load this page/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Retry" })).toBeTruthy();
  });
});
