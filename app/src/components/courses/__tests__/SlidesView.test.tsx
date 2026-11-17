import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { SlideDeck, SlideFrameData } from "../types";
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

  it("shows the text, without spinning, when the build route is gone (a deployment)", async () => {
    const stale = { ...deck, status: "text" as const, images: false, stale: true, slides: [{ ...deck.slides[0], image: null }] };
    const fetchMock = vi.fn(async (_url: string, init?: RequestInit) =>
      init?.method === "POST" ? new Response("{}", { status: 404 }) : new Response(JSON.stringify(stale)),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByRole("status")).toHaveTextContent("Slide images are not available here");
    expect(screen.queryByText(/Rendering slide images/)).toBeNull();
    expect(screen.getByText("body one", { exact: false })).toBeInTheDocument();
  });

  it("fetches the deck, shows the image as a blob and keeps the slide text in the page", async () => {
    const fetchMock = stub(deck);
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByText("body one", { exact: false })).toBeInTheDocument();
    expect(fetchMock.mock.calls[0][0]).toBe("/api/courses/slides/c1/m1");
    const img = await screen.findByRole("img", { name: "First" });
    expect(img).toHaveAttribute("src", "blob:slide");
    expect(fetchMock).toHaveBeenCalledWith("/api/courses/slide-image/c1/m1/1", expect.anything());
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

const part = { n: 1, title: "Chance", of: 1 };
const frames: SlideFrameData[] = [
  { n: 1, kind: "title", title: "Module deck", subtitle: "", tagline: "", byline: "", reference: "", agenda: [{ n: 1, title: "Chance", summary: "" }], notes: "", narration: "Welcome. This is the plan." },
  { n: 2, kind: "divider", title: "Chance", summary: "Coins", part, notes: "", narration: "Part 1. Chance." },
  { n: 3, kind: "slide", layout: "bullets", beat: "practice", level: "core", title: "Toss a coin", kicker: "", lead: "", takeaway: "Half are heads.", source: "notes/01.md", part, body: { bullets: ["ten tosses"] }, notes: "Speaker note", narration: "Toss it ten times." },
];

/** A stand-in for the browser's voice: it records what it is asked to say and ends each on demand. */
function fakeSpeech() {
  const spoken: { text: string; rate: number; onend: (() => void) | null }[] = [];
  class Utterance {
    rate = 1;
    onend: (() => void) | null = null;
    onerror: ((e: { error: string }) => void) | null = null;
    constructor(public text: string) {}
  }
  vi.stubGlobal("SpeechSynthesisUtterance", Utterance);
  const synth = { speak: vi.fn((u: Utterance) => spoken.push(u)), cancel: vi.fn() };
  Object.defineProperty(window, "speechSynthesis", { value: synth, configurable: true });
  return { spoken, synth };
}

describe("SlidesView with slides drawn from the yaml", () => {
  afterEach(() => {
    delete (window as { speechSynthesis?: unknown }).speechSynthesis;
  });

  it("draws the frames without asking for a build, even when the images are stale", async () => {
    const fetchMock = stub({ ...deck, status: "text", images: false, stale: true, frames });
    render(<SlidesView deckId="c1/m1" />);
    expect(await screen.findByRole("heading", { name: "Module deck", level: 2 })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("status")).toBeNull();
    expect(screen.getByText("1 of 3")).toBeInTheDocument();
    // Nothing is read out, in text or in voice, until it is asked for.
    expect(screen.queryByTestId("slide-caption")).toBeNull();
    expect(screen.queryByLabelText("Reading speed")).toBeNull();
    await userEvent.click(screen.getByRole("button", { name: "Read along" }));
    expect(screen.getByTestId("slide-caption")).toHaveTextContent("Welcome. This is the plan.");
  });

  it("jumps from the outline, colours each tile by its beat, and links what comes after", async () => {
    const user = userEvent.setup();
    stub({ ...deck, frames });
    render(<SlidesView deckId="c1/m1" />);
    const tile = await screen.findByRole("button", { name: "Slide 3: Toss a coin" });
    expect(tile).toHaveClass("sf-b-applied");
    await user.click(tile);
    expect(screen.getByText("The application")).toBeInTheDocument();
    expect(screen.getByText("3 of 3")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Flashcards" })).toHaveAttribute("href", "#/flashcards/c1/m1");
    expect(screen.getByRole("link", { name: "Labs" })).toHaveAttribute("href", "#/labs");
    await user.keyboard("n");
    expect(screen.getByText("Speaker note")).toBeInTheDocument();
    await user.keyboard("c");
    expect(screen.getByTestId("slide-caption")).toBeInTheDocument();
    await user.keyboard("c");
    expect(screen.queryByTestId("slide-caption")).toBeNull();
  });

  it("cannot play where the browser has no voice", async () => {
    stub({ ...deck, frames });
    render(<SlidesView deckId="c1/m1?play=1" />);
    expect(await screen.findByRole("button", { name: "Read aloud" })).toBeDisabled();
  });

  it("reads a slide sentence by sentence, moves on when it ends and stops after the last", async () => {
    const user = userEvent.setup();
    const { spoken, synth } = fakeSpeech();
    stub({ ...deck, frames });
    render(<SlidesView deckId="c1/m1" />);
    await user.click(await screen.findByRole("button", { name: "Read aloud" }));
    expect(spoken.map((u) => u.text)).toEqual(["Welcome."]);
    act(() => spoken[0].onend?.());
    expect(spoken[1].text).toBe("This is the plan.");
    act(() => spoken[1].onend?.());
    await screen.findByText("2 of 3");
    expect(spoken[2].text).toBe("Part 1.");
    await user.click(screen.getByRole("button", { name: "Pause" }));
    expect(synth.cancel).toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Read aloud" }));
    expect(spoken[3].text).toBe("Part 1.");
    act(() => spoken[3].onend?.());
    act(() => spoken[4].onend?.());
    await screen.findByText("3 of 3");
    act(() => spoken[5].onend?.());
    expect(await screen.findByRole("button", { name: "Read aloud" })).toBeInTheDocument();
    expect(screen.getByText("3 of 3")).toBeInTheDocument();
  });

  it("starts reading when opened with ?play=1, at the chosen speed", async () => {
    const user = userEvent.setup();
    const { spoken } = fakeSpeech();
    stub({ ...deck, frames });
    render(<SlidesView deckId="c1/m1?play=1" />);
    await screen.findByRole("button", { name: "Pause" });
    await waitFor(() => expect(spoken[0]?.text).toBe("Welcome."));
    await user.selectOptions(screen.getByLabelText("Reading speed"), "1.5");
    expect(spoken[spoken.length - 1]).toMatchObject({ text: "Welcome.", rate: 1.5 });
  });

  it("pauses and hands the slide to the tutor", async () => {
    const user = userEvent.setup();
    fakeSpeech();
    const onAsk = vi.fn();
    stub({ ...deck, frames });
    render(<SlidesView deckId="c1/m1" onAsk={onAsk} />);
    await user.click(await screen.findByRole("button", { name: "Slide 3: Toss a coin" }));
    await user.click(screen.getByRole("button", { name: "Read aloud" }));
    await user.click(screen.getByRole("button", { name: "Ask about this slide" }));
    expect(screen.getByRole("button", { name: "Read aloud" })).toBeInTheDocument();
    expect(onAsk).toHaveBeenCalledWith(expect.stringMatching(/Module deck.*Toss a coin.*Half are heads\..*notes\/01\.md/));
  });
});
