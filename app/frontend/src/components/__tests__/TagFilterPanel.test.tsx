import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagFilterPanel } from "../TagFilterPanel";

describe("TagFilterPanel", () => {
  it("renders one chip per payload domain, never private", () => {
    render(<TagFilterPanel domains={["context", "loop", "private", "rag"]} activeTags={new Set()} onChange={() => {}} />);
    for (const d of ["context", "loop", "rag"]) expect(screen.getByRole("button", { name: d })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "private" })).toBeNull();
  });

  it("filter and brief are sibling buttons, not nested", () => {
    const onChange = vi.fn();
    const onBrief = vi.fn();
    render(<TagFilterPanel domains={["rag"]} activeTags={new Set(["rag"])} onChange={onChange} onBrief={onBrief} />);
    const filter = screen.getByRole("button", { name: "rag" });
    const brief = screen.getByRole("button", { name: "Brief me on rag" });
    expect(filter).toHaveAttribute("aria-pressed", "true");
    expect(filter.contains(brief) || brief.contains(filter)).toBe(false);
    expect(document.querySelector("button button")).toBeNull();

    fireEvent.click(brief);
    expect(onBrief).toHaveBeenCalledWith("rag");
    expect(onChange).not.toHaveBeenCalled();

    fireEvent.click(filter);
    expect(onChange).toHaveBeenCalledWith(new Set());
  });
});
