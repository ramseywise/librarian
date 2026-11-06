import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MapSearch } from "../MapSearch";
import type { SearchResult } from "../../utils/glossary";

const result: SearchResult = {
  lit: new Set(["fusion", "other"]),
  hits: [
    { kind: "term", id: "rrf", label: "Reciprocal rank fusion", detail: "Also: RRF", page: "fusion" },
    { kind: "page", id: "other", label: "Other Page", detail: "A summary", page: "other" },
    { kind: "term", id: "pageless", label: "No page", detail: "", page: null },
  ],
};

const setup = (r: SearchResult | null = result) => {
  const onChange = vi.fn();
  const onOpenPage = vi.fn();
  render(<MapSearch value="rrf" onChange={onChange} result={r} onOpenPage={onOpenPage} />);
  return { onChange, onOpenPage, input: screen.getByRole("combobox", { name: "Search the map" }) };
};

describe("MapSearch", () => {
  it("marks a glossary hit as a term", () => {
    const { input } = setup();
    fireEvent.focus(input);
    const first = screen.getAllByRole("option")[0];
    expect(first).toHaveTextContent("term");
    expect(first).toHaveTextContent("Reciprocal rank fusion");
  });

  it("opens the first hit on Enter, or the one the arrows reached", () => {
    const first = setup();
    fireEvent.keyDown(first.input, { key: "Enter" });
    expect(first.onOpenPage).toHaveBeenCalledWith("fusion");
  });

  it("steps through the hits with the arrows", () => {
    const { input, onOpenPage } = setup();
    fireEvent.keyDown(input, { key: "ArrowDown" });
    fireEvent.keyDown(input, { key: "ArrowDown" });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onOpenPage).toHaveBeenCalledWith("other");
  });

  it("does nothing for a term with no page", () => {
    const { input, onOpenPage } = setup();
    fireEvent.focus(input);
    fireEvent.click(screen.getAllByRole("option")[2]);
    expect(onOpenPage).not.toHaveBeenCalled();
  });

  it("clears on Escape without letting the press reach the map", () => {
    const { input, onChange } = setup();
    const outer = vi.fn();
    document.addEventListener("keydown", outer);
    fireEvent.keyDown(input, { key: "Escape" });
    document.removeEventListener("keydown", outer);
    expect(onChange).toHaveBeenCalledWith("");
    expect(outer).not.toHaveBeenCalled();
  });

  it("says when nothing matched", () => {
    const { input } = setup({ lit: new Set(), hits: [] });
    fireEvent.focus(input);
    expect(screen.getByText("No matches")).toBeInTheDocument();
  });
});
