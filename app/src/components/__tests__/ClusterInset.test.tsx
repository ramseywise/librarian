import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClusterInset } from "../ClusterInset";
import type { AtlasSector } from "../../utils/atlas";

const SECTORS: AtlasSector[] = [
  { id: "rag", label: "RAG", color: "#f00", pageIds: ["rrf", "chunking", "bm25"] },
  { id: "llm", label: "LLM", color: "#0f0", pageIds: ["attention"] },
  { id: "evals", label: "Evals", color: "#00f", pageIds: ["golden-set"] },
];

describe("ClusterInset", () => {
  it("lists the sectors the canvas reaches, most pages first, and opens one", () => {
    const onOpenSector = vi.fn();
    const onOpenAtlas = vi.fn();
    const { container } = render(
      <ClusterInset sectors={SECTORS} pageIds={["attention", "rrf", "bm25", "unknown"]} anchorId="rrf"
        onOpenSector={onOpenSector} onOpenAtlas={onOpenAtlas} />,
    );
    const rows = [...container.querySelectorAll<HTMLButtonElement>(".cluster-inset-row")];
    expect(rows.map((r) => r.textContent)).toEqual(["RAG2", "LLM1"]);
    expect(container.querySelectorAll(".cluster-inset-arc--lit")).toHaveLength(2);
    expect(container.querySelectorAll(".cluster-inset-tick")).toHaveLength(3);
    fireEvent.click(rows[1]);
    expect(onOpenSector).toHaveBeenCalledWith("llm");
    fireEvent.click(screen.getByRole("button", { name: "Back to the atlas" }));
    expect(onOpenAtlas).toHaveBeenCalled();
  });

  it("says how many pages are drawn as points behind the cards", () => {
    const { container } = render(
      <ClusterInset sectors={SECTORS} pageIds={["rrf"]} anchorId="rrf" onOpenSector={vi.fn()} onOpenAtlas={vi.fn()}
        around={{ near: 35, far: 901 }} />,
    );
    expect(container.querySelector(".cluster-inset-around")?.textContent).toMatch(/35 within 2 links\s*901 within 4/);
  });

  it("draws nothing when no page on the canvas is in a sector", () => {
    const { container } = render(
      <ClusterInset sectors={SECTORS} pageIds={[]} anchorId={null} onOpenSector={vi.fn()} onOpenAtlas={vi.fn()} />,
    );
    expect(container.firstChild).toBeNull();
  });
});
