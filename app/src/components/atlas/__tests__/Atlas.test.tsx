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
const sectors = sectorsOf(pages, degree, "domain", null);
const info = new Map(pages.map((p) => [p.id, { title: `Title ${p.id}`, summary: `Summary ${p.id}` }]));

// jsdom has no layout, so give the stage a size and let the canvas calls fall through to null.
function setup(extra: Partial<React.ComponentProps<typeof Atlas>> = {}) {
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);
  // Reduced motion, so opening is immediate rather than after a camera move.
  vi.stubGlobal("matchMedia", (query: string) => ({ matches: true, media: query, addEventListener() {}, removeEventListener() {} }));
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({
    x: 0, y: 0, top: 0, left: 0, right: 1000, bottom: 800, width: 1000, height: 800, toJSON: () => ({}),
  });
  const onOpenSector = vi.fn();
  const onOpenPage = vi.fn();
  render(
    <Atlas
      sectors={sectors}
      grouping="domain"
      info={info}
      degree={degree}
      totalLinks={12}
      termCount={4}
      matches={null}
      lit={null}
      enterFrom={null}
      onOpenSector={onOpenSector}
      onOpenPage={onOpenPage}
      {...extra}
    />,
  );
  return { onOpenSector, onOpenPage, canvas: screen.getByRole("application") };
}

describe("Atlas", () => {
  it("describes itself to a screen reader", () => {
    const { canvas } = setup();
    expect(canvas).toHaveAttribute("aria-label", expect.stringContaining("9 wiki pages in 2 sectors"));
    expect(canvas).toHaveAttribute("tabindex", "0");
  });

  it("counts the wiki, with terms as a number and no more", () => {
    setup();
    expect(screen.getByText("wiki pages")).toBeInTheDocument();
    expect(screen.getByText(/4 glossary terms/)).toBeInTheDocument();
  });

  it("counts the matches when a filter or search is on", () => {
    setup({ matches: new Set(["rag-0", "eval-0"]) });
    expect(screen.getByText("2 of 9")).toBeInTheDocument();
    expect(screen.getByText("pages match")).toBeInTheDocument();
  });

  it("steps with the keyboard and opens the page on Enter", () => {
    const { canvas, onOpenPage } = setup();
    fireEvent.keyDown(canvas, { key: "ArrowRight" });
    expect(screen.getByRole("button", { name: "Open" })).toBeInTheDocument();
    const ring = layoutRing(sectors);
    expect(screen.getByText(`Title ${ring.spikes[0].id}`)).toBeInTheDocument();
    fireEvent.keyDown(canvas, { key: "Enter" });
    expect(onOpenPage).toHaveBeenCalledWith("rag", ring.spikes[0].id);
  });

  it("steps by sector and opens the sector on Enter", () => {
    const { canvas, onOpenSector } = setup();
    fireEvent.keyDown(canvas, { key: "ArrowDown" });
    expect(screen.getByText("6 pages")).toBeInTheDocument();
    fireEvent.keyDown(canvas, { key: "Enter" });
    expect(onOpenSector).toHaveBeenCalledWith("rag");
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

  it("offers everything as plain links without the canvas", () => {
    render(<AtlasList sectors={sectors} grouping="domain" titleOf={(id) => info.get(id)?.title ?? id} matches={null} />);
    const sector = screen.getByText("eval").closest("details")!;
    sector.open = true;
    fireEvent(sector, new Event("toggle"));
    expect(within(sector).getByRole("link", { name: "Title eval-0" })).toHaveAttribute(
      "href",
      "#/map/domain/eval/eval-0",
    );
    expect(within(sector).getByRole("link", { name: "Open this sector" })).toHaveAttribute("href", "#/map/domain/eval");
  });
});
