import { render, screen } from "@testing-library/react";
import { ReactFlowProvider, type NodeProps } from "@xyflow/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { WikiNode, type WikiFlowNode } from "../WikiNode";
import { NodeDetailPanel } from "../NodeDetailPanel";
import type { WikiNodeData } from "../../types";

const data = (priv: boolean): WikiNodeData => ({
  title: "Page", tags: ["rag", "concept"], domain: [priv ? "private" : "rag"], typeTag: "concept",
  summary: "s", updated: "2026-10-30", path: "rag/page.md", dimmed: false, highlighted: false, private: priv,
});

function renderNode(d: WikiNodeData) {
  const props = { id: "page", data: d, selected: false } as unknown as NodeProps<WikiFlowNode>;
  return render(<ReactFlowProvider><WikiNode {...props} /></ReactFlowProvider>);
}

// Decision D1: private pages stay visible locally, marked with a badge.
describe("private badge", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(new Response("[]"))));
  });
  afterEach(() => vi.unstubAllGlobals());

  it("shows on a private graph node only", () => {
    renderNode(data(true));
    expect(screen.getByText("private", { selector: "span" })).toBeInTheDocument();
  });

  it("is absent on a public graph node", () => {
    renderNode(data(false));
    expect(screen.queryByText("private")).toBeNull();
  });

  it("shows in the detail panel for a private page", () => {
    render(<NodeDetailPanel nodeId="page" data={data(true)} highlighted={false} lastQuery="" onClose={() => {}} />);
    expect(screen.getByText("private", { selector: "span" })).toBeInTheDocument();
  });
});
