import { fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Atlas } from "../Atlas";
import { AtlasList } from "../AtlasList";
import { layoutRing, sectorsOf, type AtlasPage } from "../../../utils/atlas";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const pages: AtlasPage[] = [
  ...Array.from({ length: 6 }, (_, i) => ({ id: `rag-${i}`, domain: "rag" })),
  ...Array.from({ length: 3 }, (_, i) => ({ id: `eval-${i}`, domain: "eval" })),
];
const degree = new Map([["rag-3", 20], ["rag-1", 5]]);
const sectors = sectorsOf(pages, degree, "wiki", []);
const info = new Map(pages.map((p) => [p.id, { title: `Title ${p.id}`, summary: `Summary ${p.id}` }]));

// jsdom has no layout, so give the stage a size and let the canvas calls fall through to null.
function setup(extra: Partial<React.ComponentProps<typeof Atlas>> = {}) {
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);
  // Reduced motion, so opening is immediate rather than after a camera move.
  vi.stubGlobal("matchMedia", (query: string) => ({ matches: true, media: query, addEventListener() {}, removeEventListener() {} }));
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({
    x: 0, y: 0, top: 0, left: 0, right: 1000, bottom: 800, width: 1000, height: 800, toJSON: () => ({}),
  });
  // The page card asks for its lessons; none here.
  vi.stubGlobal("fetch", vi.fn(async () => new Response("[]", { status: 200, headers: { "content-type": "application/json" } })));
  render(
    <Atlas
      sectors={sectors}
      grouping="wiki"
      info={info}
      degree={degree}
      totalLinks={12}
      matches={null}
      lit={null}
      taught={null}
      enterFrom={null}
      {...extra}
    />,
  );
  return { canvas: screen.getByRole("application") };
}

describe("Atlas", () => {
  it("describes itself to a screen reader", () => {
    const { canvas } = setup();
    expect(canvas).toHaveAttribute("aria-label", expect.stringContaining("9 wiki pages in 2 sectors"));
    expect(canvas).toHaveAttribute("tabindex", "0");
  });

  it("counts the wiki pages and links, and no glossary terms", () => {
    setup();
    expect(screen.getByText("wiki pages")).toBeInTheDocument();
    expect(screen.getByText("12 links")).toBeInTheDocument();
    expect(screen.queryByText(/glossary terms/)).toBeNull();
  });

  it("counts the matches when a filter or search is on", () => {
    setup({ matches: new Set(["rag-0", "eval-0"]) });
    expect(screen.getByText("2 of 9")).toBeInTheDocument();
    expect(screen.getByText("pages match")).toBeInTheDocument();
  });

  it("steps with the keyboard and keeps the page in place on Enter", () => {
    const { canvas } = setup();
    fireEvent.keyDown(canvas, { key: "ArrowRight" });
    const ring = layoutRing(sectors);
    expect(screen.getAllByText(`Title ${ring.spikes[0].id}`).length).toBeGreaterThan(0);
    expect(screen.queryByRole("button", { name: "Open" })).toBeNull();
    fireEvent.keyDown(canvas, { key: "Enter" });
    expect(screen.getAllByText(`Title ${ring.spikes[0].id}`).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Clear" })).toBeInTheDocument();
  });

  it("steps by sector, and Escape clears", () => {
    const { canvas } = setup();
    fireEvent.keyDown(canvas, { key: "ArrowDown" });
    expect(screen.getByText("6 pages")).toBeInTheDocument();
    fireEvent.keyDown(canvas, { key: "Escape" });
    expect(screen.queryByRole("button", { name: "Clear" })).toBeNull();
  });

  it("moves the card to a related page without leaving the atlas", () => {
    const related = vi.fn((id: string) => [
      { label: "Builds on", pages: [{ id: id === "rag-3" ? "eval-0" : "rag-3", title: `Title ${id === "rag-3" ? "eval-0" : "rag-3"}` }], more: 0 },
    ]);
    const { canvas } = setup({ related });
    fireEvent.keyDown(canvas, { key: "ArrowRight" });
    const ring = layoutRing(sectors);
    expect(ring.spikes[0].id).toBe("rag-3");
    fireEvent.click(screen.getAllByRole("button", { name: "Title eval-0" })[0]);
    expect(screen.getAllByText("Title eval-0").length).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: "Title rag-3" }).length).toBeGreaterThan(0);
    expect(canvas).toBeInTheDocument();
  });

  it("shows only the kept link groups, three pages each", () => {
    const list = (...ids: string[]) => ids.map((id) => ({ id, title: `Title ${id}` }));
    const related = vi.fn(() => [
      { label: "Understand first", pages: list("eval-1"), more: 0 },
      { label: "Builds on", pages: list("rag-0", "rag-1", "rag-2", "rag-4", "rag-5"), more: 2 },
      { label: "Alternatives", pages: list("eval-2"), more: 0 },
    ]);
    setup({ related });
    fireEvent.keyDown(screen.getByRole("application"), { key: "ArrowRight" });
    expect(screen.queryByText(/Understand first/)).toBeNull();
    expect(screen.queryByText(/Alternatives/)).toBeNull();
    expect(screen.getAllByText("builds on").length).toBe(3);
    expect(screen.queryByRole("button", { name: "Title rag-4" })).toBeNull();
    expect(screen.getByText("+4 more linked")).toBeInTheDocument();
  });

  it("links the note, its sources and its lessons in a new tab", async () => {
    const withPage = new Map(info);
    withPage.set("rag-3", {
      title: "Title rag-3",
      summary: "Summary rag-3",
      path: "rag/hybrid search.md",
      origins: [{ title: "A paper", links: [{ kind: "arxiv", href: "https://arxiv.org/abs/2610.02163" }, { kind: "pdf", href: "https://github.com/x/y.pdf" }] }],
      sourceCount: 3,
    } as never);
    setup({ info: withPage });
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify([
      { id: "ai-engineering/02-context/01-intro", title: "Intro", section: "s", kind: "reading", summary: "", course: "AI Engineering", flashcardCount: 4, quizCount: 2 },
    ]), { status: 200, headers: { "content-type": "application/json" } })));
    fireEvent.keyDown(screen.getByRole("application"), { key: "ArrowRight" });
    const note = screen.getAllByRole("link", { name: /Wiki note/ })[0];
    expect(note).toHaveAttribute("href", "https://github.com/ramseywise/librarian/blob/main/data/wiki/rag/hybrid%20search.md");
    expect(note).toHaveAttribute("target", "_blank");
    expect(note).toHaveAttribute("rel", "noopener noreferrer");
    expect(screen.getAllByRole("link", { name: "A paper (arXiv)" })[0]).toHaveAttribute("href", "https://arxiv.org/abs/2610.02163");
    expect(screen.getAllByRole("link", { name: "A paper (PDF)" })[0]).toHaveAttribute("target", "_blank");
    expect(screen.getAllByText(/\+2 more sources with no public link/).length).toBeGreaterThan(0);
    const lesson = (await screen.findAllByRole("link", { name: /Intro/ }))[0];
    expect(lesson).toHaveAttribute("href", "#/courses/ai-engineering/02-context/01-intro");
    expect(lesson).toHaveAttribute("target", "_blank");
    expect(screen.getAllByText(/6 practice items/).length).toBeGreaterThan(0);
  });

  it("lists similar pages by score, and the switches hide each kind of line", () => {
    const related = vi.fn(() => [{ label: "Leads to", pages: [{ id: "rag-0", title: "Title rag-0" }], more: 0 }]);
    const similar = vi.fn(() => [{ id: "eval-1", title: "Title eval-1", score: 0.612 }]);
    setup({ related, similar });
    fireEvent.keyDown(screen.getByRole("application"), { key: "ArrowRight" });
    expect(screen.getAllByText("sim 0.61").length).toBeGreaterThan(0);
    expect(screen.getAllByText("leads to").length).toBeGreaterThan(0);

    const wiki = screen.getByRole("button", { name: /wiki links/ });
    expect(wiki).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(wiki);
    expect(wiki).toHaveAttribute("aria-pressed", "false");
    expect(screen.queryByText("leads to")).toBeNull();
    expect(screen.getAllByText("sim 0.61").length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole("button", { name: /similar/ }));
    expect(screen.queryByText("sim 0.61")).toBeNull();
  });

  it("zooms in and resets from its buttons", () => {
    setup();
    const out = screen.getByRole("button", { name: "Zoom out" });
    expect(out).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Zoom in" }));
    expect(out).toBeEnabled();
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(out).toBeDisabled();
  });

  it("counts each sector's pages no lesson links yet, once the curriculum is in", () => {
    const taught = new Set(["rag-0", "rag-1", "eval-0", "eval-1", "eval-2"]);
    render(<AtlasList sectors={sectors} grouping="wiki" titleOf={(id) => id} matches={null} taught={taught} />);
    expect(screen.getByText("rag").closest("summary")).toHaveTextContent("rag 6 · 4 not yet in a lesson");
    expect(screen.getByText("eval").closest("summary")).not.toHaveTextContent("not yet in a lesson");
  });

  it("names the course gaps in the sector labels and the legend", () => {
    setup({ taught: new Set(["rag-0", "eval-0", "eval-1", "eval-2"]) });
    expect(screen.getByText("Faint: no lesson links the page yet")).toBeInTheDocument();
    const label = screen.getByRole("button", { name: /^rag/ });
    expect(label.querySelector("title")?.textContent).toBe("rag: 6 pages · 5 not yet in a lesson");
  });

  it("offers everything as plain links without the canvas", () => {
    render(<AtlasList sectors={sectors} grouping="wiki" titleOf={(id) => info.get(id)?.title ?? id} matches={null} taught={null} />);
    const sector = screen.getByText("eval").closest("details")!;
    sector.open = true;
    fireEvent(sector, new Event("toggle"));
    expect(within(sector).getByRole("link", { name: "Title eval-0" })).toHaveAttribute(
      "href",
      "#/map/wiki/eval/eval-0",
    );
    expect(within(sector).getByRole("link", { name: "Open this sector" })).toHaveAttribute("href", "#/map/wiki/eval");
  });
});
