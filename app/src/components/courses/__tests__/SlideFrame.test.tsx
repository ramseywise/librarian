import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SlideFrame, beatClass } from "../SlideFrame";
import type { SlideFrameData } from "../types";

type Slide = Extract<SlideFrameData, { kind: "slide" }>;

function slide(layout: string, body: Record<string, unknown>, over: Partial<Slide> = {}): Slide {
  return {
    n: 3, kind: "slide", layout, beat: "fundamentals", level: "core", title: "A slide", kicker: "", lead: "",
    takeaway: "Keep this.", source: "notes/01.md", part: { n: 1, title: "First part", of: 4 }, body, notes: "", narration: "",
    ...over,
  };
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("SlideFrame", () => {
  it("names the beat, the part and the place, and shows the takeaway", () => {
    const { container } = render(<SlideFrame frame={slide("bullets", { bullets: ["one", { text: "two", sub: ["under two"] }] })} total={9} />);
    expect(screen.getByText("The principle")).toBeInTheDocument();
    expect(screen.getByText("1 First part · 3 / 9")).toBeInTheDocument();
    expect(screen.getByText("Keep this.")).toBeInTheDocument();
    expect(screen.getByText("under two")).toBeInTheDocument();
    expect(container.querySelector(".sf")).toHaveClass("sf-b-principle");
  });

  it("gives each beat its own hue and a slide without one a neutral one", () => {
    const hues = (["problem", "fundamentals", "practice", "pitfalls", "wrap"] as const).map((beat) => beatClass(slide("bullets", {}, { beat })));
    expect(hues).toEqual(["sf-b-idea", "sf-b-principle", "sf-b-applied", "sf-b-pitfall", "sf-b-keep"]);
    expect(beatClass(slide("bullets", {}, { beat: null }))).toBe("sf-b-none");
  });

  it("draws the deck's inline markup as bold and code, and nothing else as markup", () => {
    render(<SlideFrame frame={slide("statement", { statement: "A **bold** claim about `p_value` <b>not html</b>", attribution: "the note" })} total={9} />);
    expect(screen.getByText("bold").tagName).toBe("B");
    expect(screen.getByText("p_value").tagName).toBe("CODE");
    expect(screen.getByText(/<b>not html<\/b>/)).toBeInTheDocument();
    expect(screen.getByText("the note")).toBeInTheDocument();
  });

  it("draws a flow with its last step accented, a loop and a caption", () => {
    const { container } = render(<SlideFrame frame={slide("flow", { steps: ["Ask", { label: "Measure", sub: "twice" }, "Decide"], loop: "repeat weekly", caption: "The whole cycle" })} total={9} />);
    expect(screen.getByText("twice")).toBeInTheDocument();
    expect(screen.getByText(/repeat weekly/)).toBeInTheDocument();
    expect(screen.getByText("The whole cycle")).toBeInTheDocument();
    const steps = container.querySelectorAll(".sf-step");
    expect(steps).toHaveLength(3);
    expect(steps[2]).toHaveClass("sf-step--accent");
  });

  it("draws numbered steps, a table with its marked row, and code beside bullets", () => {
    const { container, rerender } = render(<SlideFrame frame={slide("steps", { steps: [{ title: "Load", text: "the file" }, { title: "Check", n: "B" }] })} total={9} />);
    expect(screen.getByText("the file")).toBeInTheDocument();
    expect(screen.getByText("B")).toBeInTheDocument();
    rerender(<SlideFrame frame={slide("table", { header: ["Test", "Use"], rows: [["t", "means"], ["chi", "counts"]], highlight: [1] })} total={9} />);
    expect(screen.getByRole("columnheader", { name: "Use" })).toBeInTheDocument();
    expect(container.querySelectorAll("tbody tr")[1]).toHaveClass("sf-row--hit");
    rerender(<SlideFrame frame={slide("code", { lang: "python", code: "# a comment\nx = 1\n", bullets: ["reads once"] })} total={9} />);
    expect(screen.getByText("python")).toBeInTheDocument();
    expect(container.querySelector(".sf-code-comment")).toHaveTextContent("# a comment");
    expect(screen.getByText("reads once")).toBeInTheDocument();
  });

  it("draws a comparison with the right side emphasised unless told otherwise, and cards", () => {
    const body = { left: { title: "Before", bullets: ["slow"] }, right: { title: "After", body: "fast", tag: "use this" } };
    const { container, rerender } = render(<SlideFrame frame={slide("compare", body)} total={9} />);
    expect(container.querySelectorAll(".sf-col")[1]).toHaveClass("sf-col--win");
    expect(screen.getByText("use this")).toBeInTheDocument();
    rerender(<SlideFrame frame={slide("compare", { ...body, emphasis: "none" })} total={9} />);
    expect(container.querySelector(".sf-col--win")).toBeNull();
    rerender(<SlideFrame frame={slide("cards", { cards: [{ title: "One", body: "first" }, { title: "Two", bullets: ["second"], accent: "F59E0B" }] })} total={9} />);
    expect(screen.getByText("second")).toBeInTheDocument();
    expect(container.querySelectorAll(".sf-card")[1]).toHaveClass("sf-card--accent");
  });

  it("fetches a slide's image with the caller's token and captions it", async () => {
    URL.createObjectURL = vi.fn(() => "blob:figure");
    URL.revokeObjectURL = vi.fn();
    const fetchMock = vi.fn(async () => new Response("png"));
    vi.stubGlobal("fetch", fetchMock);
    render(<SlideFrame frame={slide("image", { image: "/api/courses/files/c1/m1/assets/a.png", caption: "A figure" })} total={9} />);
    expect(await screen.findByRole("img", { name: "A figure" })).toHaveAttribute("src", "blob:figure");
    expect(fetchMock).toHaveBeenCalledWith("/api/courses/files/c1/m1/assets/a.png", expect.anything());
  });

  it("draws the title slide with the agenda and a divider with the part's topics", () => {
    const { rerender } = render(
      <SlideFrame
        frame={{ n: 1, kind: "title", title: "Probability", subtitle: "Module 2", tagline: "", byline: "", reference: "", agenda: [{ n: 1, title: "Chance", summary: "Coins" }], notes: "", narration: "" }}
        total={9}
      />,
    );
    expect(screen.getByRole("heading", { name: "Probability" })).toBeInTheDocument();
    expect(screen.getByText("Coins")).toBeInTheDocument();
    rerender(
      <SlideFrame
        frame={{ n: 2, kind: "divider", title: "Chance", summary: "Coins · Dice", part: { n: 1, title: "Chance", of: 4 }, notes: "", narration: "" }}
        total={9}
      />,
    );
    expect(screen.getByText("Part 1 of 4")).toBeInTheDocument();
    expect(screen.getByText("Dice")).toBeInTheDocument();
  });

  it("still shows the bullets of a layout it does not know", () => {
    render(<SlideFrame frame={slide("hologram", { bullets: ["kept"] })} total={9} />);
    expect(screen.getByText("kept")).toBeInTheDocument();
  });
});
