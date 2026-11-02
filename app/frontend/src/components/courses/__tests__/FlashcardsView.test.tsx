import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { FlashcardDeck } from "../../../courses/types";
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
