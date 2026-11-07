import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { SlideDeck } from "../types";
import { SlidesView } from "../SlidesView";

const deck: SlideDeck = {
  id: "c1/m1",
  title: "Module deck",
  course: "c1",
  module: "c1/m1",
  status: "ready",
  images: true,
  needs: [],
  error: "",
  decks: [{ id: "c1/m1", title: "Module deck" }, { id: "c1/m1/01-intro", title: "Intro lecture" }],
  slides: [
    { n: 1, title: "First", text: "First\nbody one", notes: "Say hello", image: "/api/courses/slide-image/c1/m1/1" },
    { n: 2, title: "Second", text: "Second\nbody two", notes: "", image: null },
  ],
};

function stub(body: SlideDeck | null, status = 200) {
  const fetchMock = vi.fn(async (url: string) =>
    url.includes("slide-image")
      ? new Response("png", { status: 200 })
      : new Response(JSON.stringify(body), { status }),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

beforeEach(() => {
  URL.createObjectURL = vi.fn(() => "blob:slide");
  URL.revokeObjectURL = vi.fn();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("SlidesView", () => {
  it("asks for a build with POST when the deck is stale, and never triggers one with GET", async () => {
    const stale = { ...deck, status: "text" as const, images: false, stale: true };
    const building = { ...deck, status: "building" as const, images: false, stale: false };
    const fetchMock = vi.fn(async (_url: string, init?: RequestInit) =>
      new Response(JSON.stringify(init?.method === "POST" ? building : stale)),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByRole("status")).toHaveTextContent("Rendering slide images");
    expect(fetchMock.mock.calls[0][0]).toBe("/api/courses/slides/c1/m1");
    expect(fetchMock.mock.calls[1][0]).toBe("/api/courses/slides/c1/m1/build");
    expect(fetchMock.mock.calls[1][1]).toMatchObject({ method: "POST" });
  });

  it("fetches the deck, shows the image as a blob and keeps the slide text in the page", async () => {
    const fetchMock = stub(deck);
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByText("body one", { exact: false })).toBeInTheDocument();
    expect(fetchMock.mock.calls[0][0]).toBe("/api/courses/slides/c1/m1");
    const img = await screen.findByRole("img", { name: "First" });
    expect(img).toHaveAttribute("src", "blob:slide");
    expect(fetchMock).toHaveBeenCalledWith("/api/courses/slide-image/c1/m1/1");
    expect(screen.getByText("1 of 2")).toBeInTheDocument();
  });

  it("moves with the arrow keys, Home and End, and stops at the ends", async () => {
    const user = userEvent.setup();
    stub(deck);
    render(<SlidesView deckId="c1/m1" />);
    await screen.findByText("1 of 2");
    await user.keyboard("{ArrowLeft}");
    expect(screen.getByText("1 of 2")).toBeInTheDocument();
    await user.keyboard("{ArrowRight}");
    expect(screen.getByText("2 of 2")).toBeInTheDocument();
    expect(screen.getByText("body two", { exact: false })).toBeInTheDocument();
    await user.keyboard("{ArrowRight}");
    expect(screen.getByText("2 of 2")).toBeInTheDocument();
    await user.keyboard("{Home}");
    expect(screen.getByText("1 of 2")).toBeInTheDocument();
    await user.keyboard("{End}");
    expect(screen.getByText("2 of 2")).toBeInTheDocument();
  });

  it("n toggles the speaker notes", async () => {
    const user = userEvent.setup();
    stub(deck);
    render(<SlidesView deckId="c1/m1" />);
    await screen.findByText("1 of 2");
    expect(screen.queryByText("Say hello")).toBeNull();
    await user.keyboard("n");
    expect(screen.getByText("Say hello")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Notes" }));
    expect(screen.queryByText("Say hello")).toBeNull();
    await user.keyboard("{ArrowRight}n");
    expect(screen.getByText("No notes for this slide.")).toBeInTheDocument();
  });

  it("without images it shows the text alone and says what is missing", async () => {
    stub({ ...deck, status: "text", images: false, needs: ["macOS Quick Look"], slides: [{ ...deck.slides[0], image: null }] });
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByText(/Slide images are not available here \(needs macOS Quick Look\)/)).toBeInTheDocument();
    expect(screen.queryByRole("img")).toBeNull();
    expect(screen.getByText("body one", { exact: false })).toBeVisible();
  });

  it("reports a failed build with its error and still shows the text", async () => {
    stub({ ...deck, status: "failed", error: "boom", slides: [{ ...deck.slides[0], image: null }] });
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByRole("alert")).toHaveTextContent("The slide build failed: boom");
    expect(screen.getByText("body one", { exact: false })).toBeInTheDocument();
  });

  it("asks again while the build runs, and shows the images once ready", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const fetchMock = vi.fn(async (url: string) => {
      if (url.includes("slide-image")) return new Response("png");
      const building = fetchMock.mock.calls.filter(([u]) => String(u).includes("/slides/")).length <= 1;
      const body = building ? { ...deck, status: "building", images: false, slides: [{ ...deck.slides[0], image: null }] } : deck;
      return new Response(JSON.stringify(body));
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByRole("status")).toHaveTextContent("Rendering slide images");
    await vi.advanceTimersByTimeAsync(3100);
    await waitFor(() => expect(screen.queryByRole("status", { name: "" })?.textContent ?? "").not.toContain("Rendering"));
    expect(await screen.findByRole("img", { name: "First" })).toBeInTheDocument();
  });

  it("links the other decks of the module and marks the current one", async () => {
    stub(deck);
    render(<SlidesView deckId="c1/m1" />);
    await screen.findByText("1 of 2");
    expect(screen.getByRole("link", { name: "Intro lecture" })).toHaveAttribute("href", "#/slides/c1/m1/01-intro");
    expect(screen.getByRole("link", { name: "Module deck" })).toHaveAttribute("aria-current", "page");
  });

  it("says so when there is no deck", async () => {
    stub(null, 404);
    render(<SlidesView deckId="c1/nope" />);
    expect(await screen.findByText("No slides here")).toBeInTheDocument();
  });
});
