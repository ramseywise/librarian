import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectChips } from "../EdgeTogglePanel";
import type { EdgeVisibility } from "../../types";

const vis: EdgeVisibility = { wikilink: true, semantic: false, module: true, term: false, "course-order": false, "tag-shared": false };

function setup(visibility = vis) {
  const onChange = vi.fn();
  const onLoadSemantic = vi.fn();
  render(<ConnectChips visibility={visibility} onChange={onChange} onLoadSemantic={onLoadSemantic} loadingSemanticEdges={false} />);
  return { onChange, onLoadSemantic };
}

describe("ConnectChips", () => {
  it("offers links against similarity, each chip on when any of its kinds is", () => {
    setup();
    expect(screen.getAllByRole("button").map((b) => b.textContent)).toEqual(["Links", "Similar"]);
    expect(screen.getByRole("button", { name: "Links" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Similar" })).toHaveAttribute("aria-pressed", "false");
    setup({ ...vis, term: true });
    expect(screen.getAllByRole("button", { name: "Similar" })[1]).toHaveAttribute("aria-pressed", "true");
  });

  it("switches a chip's kinds off together", () => {
    const { onChange } = setup({ ...vis, semantic: true, term: true });
    fireEvent.click(screen.getByRole("button", { name: "Similar" }));
    expect(onChange).toHaveBeenCalledWith({ ...vis, semantic: false, term: false });
  });

  it("loads the similarity edges when Similar goes on, and not when it goes off", () => {
    const { onChange, onLoadSemantic } = setup();
    fireEvent.click(screen.getByRole("button", { name: "Similar" }));
    expect(onLoadSemantic).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith({ ...vis, semantic: true, term: true });
    onLoadSemantic.mockClear();
    setup({ ...vis, semantic: true });
    fireEvent.click(screen.getAllByRole("button", { name: "Similar" })[1]);
    expect(onLoadSemantic).not.toHaveBeenCalled();
  });

  it("on the atlas, which draws no lines, is disabled and says where lines are drawn", () => {
    const onChange = vi.fn();
    render(
      <ConnectChips visibility={vis} onChange={onChange} onLoadSemantic={vi.fn()} loadingSemanticEdges={false} inactive="Open a sector to draw lines" />,
    );
    expect(screen.getByText("Open a sector to draw lines")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Links" }));
    expect(screen.getByRole("button", { name: "Links" })).toBeDisabled();
    expect(onChange).not.toHaveBeenCalled();
  });
});
