import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { FlashcardDeck } from "../types";
import { FlashcardsDue } from "../FlashcardsDue";
import { FlashcardsView, InlineMarkup } from "../FlashcardsView";

const deck: FlashcardDeck = {
  id: "c1/m1",
  title: "Module One",
  course: "c1",
  cards: [
    { id: "0", front: "First question", back: "First answer", lesson: "c1/m1/intro", lessonTitle: "Intro" },
    { id: "1", front: "Second question", back: "Second answer", lesson: null, lessonTitle: null },
    { id: "2", front: "Third question", back: "Third answer", lesson: null, lessonTitle: null },
  ],
};

function stubDeck(status = 200) {
  const fetchMock = vi.fn(async () => new Response(JSON.stringify(deck), { status }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("FlashcardsView", () => {
  it("fetches the deck, flips the card, and links the answer to its lesson", async () => {
    const fetchMock = stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    expect(await screen.findByText("First question")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledWith("/api/courses/flashcards/c1/m1");
    expect(screen.queryByText("First answer")).toBeNull();

    await userEvent.click(screen.getByRole("button", { pressed: false }));
    expect(screen.getByText("First answer")).toBeTruthy();
    expect(screen.queryByText("First question")).toBeNull();
    expect(screen.getByRole("link", { name: "Intro" }).getAttribute("href")).toBe("#/courses/c1/m1/intro");
  });

  it("next shows the question side of the following card and wraps at the end", async () => {
    stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await screen.findByText("First question");
    await userEvent.click(screen.getByRole("button", { pressed: false }));
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByText("Second question")).toBeTruthy();
    expect(screen.getByText("2 of 3")).toBeTruthy();
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByText("First question")).toBeTruthy();
  });

  it("shuffle reorders the deck and restarts it", async () => {
    stubDeck();
    vi.spyOn(Math, "random").mockReturnValue(0); // Fisher-Yates with j = 0: [1, 2, 0]
    render(<FlashcardsView deckId="c1/m1" />);
    await screen.findByText("First question");
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    await userEvent.click(screen.getByRole("button", { name: "Shuffle" }));
    expect(screen.getByText("Second question")).toBeTruthy();
    expect(screen.getByText("1 of 3")).toBeTruthy();
  });

  it("grading a flipped card logs it and moves on; Next logs nothing", async () => {
    const fetchMock = stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await screen.findByText("First question");
    expect(screen.queryByRole("button", { name: "Missed it" })).toBeNull();
    await userEvent.click(screen.getByRole("button", { pressed: false }));
    await userEvent.click(screen.getByRole("button", { name: "Missed it" }));
    expect(fetchMock).toHaveBeenCalledWith("/api/courses/flashcard-results", expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ deck: "c1/m1", card: "0", result: "missed" }),
    }));
    expect(screen.getByText("Second question")).toBeTruthy();
    const posts = () => fetchMock.mock.calls.filter((c) => (c as unknown[])[1]).length;
    expect(posts()).toBe(1);
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(posts()).toBe(1);
  });

  it("keeps going when a grade fails to save", async () => {
    const fetchMock = stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await screen.findByText("First question");
    fetchMock.mockRejectedValueOnce(new Error("offline"));
    await userEvent.click(screen.getByRole("button", { pressed: false }));
    await userEvent.click(screen.getByRole("button", { name: "Knew it" }));
    expect(screen.getByText("Second question")).toBeTruthy();
  });

  it("says so when there is no deck", async () => {
    stubDeck(404);
    render(<FlashcardsView deckId="c1/nope" />);
    expect(await screen.findByText("No flashcards here")).toBeTruthy();
  });
});

describe("InlineMarkup", () => {
  it("renders bold and code and leaves everything else as text", () => {
    const { container } = render(<InlineMarkup text={"Use **bold `x`** then `a*b` at 5 * 3 < $4"} />);
    expect(container.querySelector("strong")?.textContent).toBe("bold x");
    expect([...container.querySelectorAll("code")].map((c) => c.textContent)).toEqual(["x", "a*b"]);
    expect(container.textContent).toBe("Use bold x then a*b at 5 * 3 < $4");
  });
});

describe("FlashcardsView study filter", () => {
  const scheduled: FlashcardDeck = {
    id: "c1/m1",
    title: "Module One",
    course: "c1",
    dueCount: 1,
    newCount: 1,
    cards: [
      { id: "0", front: "Later question", back: "a", lesson: null, lessonTitle: null, box: 3, dueOn: "2099-01-01", status: "later" },
      { id: "1", front: "Due question", back: "b", lesson: null, lessonTitle: null, box: 2, dueOn: "2020-01-01", status: "due" },
      { id: "2", front: "New question", back: "c", lesson: null, lessonTitle: null, box: null, dueOn: null, status: "new" },
    ],
  };

  function stubScheduled() {
    const fetchMock = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(async () => new Response(JSON.stringify(scheduled), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    return fetchMock;
  }

  const gradeKnew = async (user: ReturnType<typeof userEvent.setup>) => {
    await user.click(screen.getByRole("button", { pressed: false, name: /Question/ }));
    await user.click(screen.getByRole("button", { name: "Knew it" }));
  };

  it("hides the filter for a deck with no schedule", async () => {
    stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await screen.findByText("First question");
    expect(screen.queryByRole("group", { name: "Study filter" })).toBeNull();
  });

  it("starts on all cards and shows today's counts", async () => {
    stubScheduled();
    render(<FlashcardsView deckId="c1/m1" />);
    await screen.findByText("Later question");
    expect(screen.getByRole("button", { name: "Due today: 1 + 1 new" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "All 3" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("1 of 3")).toBeInTheDocument();
    expect(screen.getByText(/Box 3/)).toBeInTheDocument();
  });

  it("the filter studies due and new cards only, and graded ones leave the queue", async () => {
    const user = userEvent.setup();
    const fetchMock = stubScheduled();
    render(<FlashcardsView deckId="c1/m1" />);
    await screen.findByText("Later question");
    await user.click(screen.getByRole("button", { name: /Due today/ }));
    expect(screen.getByText("Due question")).toBeInTheDocument();
    expect(screen.getByText("1 of 2")).toBeInTheDocument();

    await gradeKnew(user);
    expect(screen.getByText("New question")).toBeInTheDocument();
    expect(screen.getByText("1 of 1")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Due today: 0 + 1 new" })).toBeInTheDocument();

    await gradeKnew(user);
    expect(screen.getByText(/Nothing left to study today/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Due today: 0 + 0 new" })).toBeInTheDocument();
    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith("flashcard-results"))).toHaveLength(2);

    await user.click(screen.getByRole("button", { name: "All 3" }));
    expect(screen.getByText("Later question")).toBeInTheDocument();
  });

  it("a route ending in ?due opens filtered and fetches the plain deck id", async () => {
    const fetchMock = stubScheduled();
    render(<FlashcardsView deckId="c1/m1?due" />);
    await screen.findByText("Due question");
    expect(fetchMock.mock.calls[0][0]).toBe("/api/courses/flashcards/c1/m1");
    expect(screen.getByRole("button", { name: /Due today/ })).toHaveAttribute("aria-pressed", "true");
  });

  it("a deck with nothing due says so instead of hanging on Loading", async () => {
    const quiet = { ...scheduled, cards: [scheduled.cards[0]], dueCount: 0, newCount: 0 };
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(quiet), { status: 200 })));
    render(<FlashcardsView deckId="c1/m1?due" />);
    expect(await screen.findByText(/Nothing left to study today/)).toBeInTheDocument();
  });
});

describe("FlashcardsDue", () => {
  const stub = (body: unknown, status = 200) =>
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(body), { status })));

  it("shows the totals and links each module to its filtered deck", async () => {
    stub({ today: "2026-11-05", due: 4, new: 7, modules: [{ deck: "c1/m1", title: "Module One", due: 4, new: 7 }] });
    render(<FlashcardsDue />);
    const box = await screen.findByRole("region", { name: "Flashcards due today" });
    expect(box).toHaveTextContent("4 due today, 7 new");
    expect(screen.getByRole("link", { name: "Module One" })).toHaveAttribute("href", "#/flashcards/c1/m1?due");
  });

  it("renders nothing with nothing to study, or when the request fails", async () => {
    stub({ today: "2026-11-05", due: 0, new: 0, modules: [] });
    const { container, unmount } = render(<FlashcardsDue />);
    await new Promise((r) => setTimeout(r, 0));
    expect(container).toBeEmptyDOMElement();
    unmount();
    stub({}, 500);
    const failed = render(<FlashcardsDue />);
    await new Promise((r) => setTimeout(r, 0));
    expect(failed.container).toBeEmptyDOMElement();
  });
});
