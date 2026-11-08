import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { NodeDetailPanel } from "../NodeDetailPanel";
import type { WikiNodeData } from "../../types";

const DATA: WikiNodeData = {
  title: "RRF Fusion",
  tags: ["rag", "pattern"],
  domain: ["rag"],
  typeTag: "pattern",
  summary: "Merge ranked lists by reciprocal rank.",
  updated: "2026-11-01",
  path: "data/wiki/rag/rrf-fusion.md",
  dimmed: false,
  highlighted: false,
};

function lessons(n: number) {
  const ls = Array.from({ length: n }, (_, i) => ({ id: `ai/rag/l${i}`, title: `Lesson ${i}`, course: "AI" }));
  const fetchMock = vi.fn<(url: string) => Promise<Response>>(async () => new Response(JSON.stringify(ls), { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => vi.unstubAllGlobals());

describe("NodeDetailPanel", () => {
  it("shows the page and filters by a clicked tag", () => {
    lessons(0);
    const onTagClick = vi.fn();
    const onClose = vi.fn();
    render(
      <NodeDetailPanel nodeId="rrf-fusion" data={DATA} highlighted={false} lastQuery="" onClose={onClose}
        onTagClick={onTagClick} activeTags={new Set(["rag"])} />,
    );
    expect(screen.getByText("RRF Fusion")).toBeInTheDocument();
    expect(screen.getByText("Merge ranked lists by reciprocal rank.")).toBeInTheDocument();
    expect(screen.getByText("rrf-fusion.md")).toBeInTheDocument();
    expect(screen.getByText("updated 2026-11-01")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "pattern" }));
    expect(onTagClick).toHaveBeenCalledWith("pattern");
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalled();
  });

  it("names the query it was cited for, only when highlighted", () => {
    lessons(0);
    const { rerender } = render(
      <NodeDetailPanel nodeId="rrf-fusion" data={DATA} highlighted lastQuery="what is rrf" onClose={vi.fn()} />,
    );
    expect(screen.getByText(/Referenced while answering: "what is rrf"/)).toBeInTheDocument();
    rerender(<NodeDetailPanel nodeId="rrf-fusion" data={DATA} highlighted={false} lastQuery="what is rrf" onClose={vi.fn()} />);
    expect(screen.queryByText(/Referenced while answering/)).toBeNull();
  });

  it("lists up to six lessons that teach the concept and opens one", async () => {
    const fetchMock = lessons(8);
    const onOpenLesson = vi.fn();
    render(
      <NodeDetailPanel nodeId="rrf-fusion" data={DATA} highlighted={false} lastQuery="" onClose={vi.fn()} onOpenLesson={onOpenLesson} />,
    );
    fireEvent.click(await screen.findByText("Lesson 2"));
    expect(onOpenLesson).toHaveBeenCalledWith("ai/rag/l2");
    expect(screen.queryByText("Lesson 6")).toBeNull();
    expect(screen.getByText("+2 more")).toBeInTheDocument();
    expect(fetchMock.mock.calls[0][0]).toBe("/api/courses/concept/rrf-fusion");
  });
});
