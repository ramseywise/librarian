import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Node } from "@xyflow/react";
import type { WikiNodeData } from "../../types";

const page = (id: string, domain: string): Node<WikiNodeData> => ({
  id,
  type: "wiki",
  position: { x: 0, y: 0 },
  data: {
    title: id.replace(/-/g, " "),
    tags: [domain, "concept"],
    domain: [domain],
    typeTag: "concept",
    summary: "",
    updated: "2026-11-01",
    path: `data/wiki/${domain}/${id}.md`,
    dimmed: false,
    highlighted: false,
  },
});

const DATA = {
  baseNodes: [page("rrf-fusion", "rag"), page("chunking", "rag"), page("react-loop", "patterns")],
  wikilinkEdges: [{ id: "e1", source: "rrf-fusion", target: "chunking", data: { type: "wikilink" } }],
  domains: ["patterns", "rag"],
  tagSharedEdges: [],
  semanticEdges: [],
  fetchSemanticEdges: vi.fn(),
  umapPositions: null,
  umapFailed: false,
  loadUmapPositions: vi.fn(async () => null),
  connected: true,
};

vi.mock("../../hooks/useWikiData", () => ({ useWikiData: () => DATA }));

class FakeResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

beforeEach(() => {
  vi.stubGlobal("ResizeObserver", FakeResizeObserver);
  vi.stubGlobal("matchMedia", (query: string) => ({ matches: false, media: query, addEventListener() {}, removeEventListener() {} }));
  vi.stubGlobal("fetch", vi.fn(async () => new Response("{}", { status: 404 })));
  window.location.hash = "";
});
afterEach(() => vi.unstubAllGlobals());

describe("WikiGraph", () => {
  it("opens on the atlas, one sector per domain", async () => {
    const { WikiGraph } = await import("../WikiGraph");
    render(<WikiGraph activeTags={new Set()} onActiveTagsChange={vi.fn()} />);
    expect(await screen.findByRole("application", { name: /^Atlas of 3 wiki pages in 2 sectors/ })).toBeInTheDocument();
    expect(screen.getByText(/3 of 3 pages/)).toBeInTheDocument();
  });

  it("draws every page as a node on the all-pages level", async () => {
    window.location.hash = "#/map/all";
    const { WikiGraph } = await import("../WikiGraph");
    const { container } = render(<WikiGraph activeTags={new Set()} onActiveTagsChange={vi.fn()} />);
    expect(container.querySelector(".react-flow")).not.toBeNull();
    expect(screen.queryByRole("application", { name: /^Atlas/ })).toBeNull();
    expect(screen.getByRole("button", { name: "Graph controls" })).toBeInTheDocument();
  });
});
