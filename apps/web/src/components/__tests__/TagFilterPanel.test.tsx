import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagFilterPanel } from "../TagFilterPanel";
import type { Curriculum } from "../../types";

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

describe("TagFilterPanel with the curriculum", () => {
  const curriculum: Curriculum = {
    courses: [
      {
        id: "ai",
        title: "AI Engineering",
        pageIds: ["a", "b"],
        modules: [
          { id: "rag", title: "RAG", firstLesson: "ai/rag/one", pageIds: ["a", "b"] },
          { id: "viz", title: "Visualisation", firstLesson: "ai/viz/one", pageIds: [] },
        ],
      },
    ],
    beyond: [{ domain: "patterns", pageIds: ["c"] }],
    primaryCourse: { a: "ai", b: "ai" },
    stale: false,
  };
  const setup = (active: string[] = [], onBrief?: (d: string) => void) => {
    const onChange = vi.fn();
    render(
      <TagFilterPanel domains={["rag"]} curriculum={curriculum} activeTags={new Set(active)} onChange={onChange} onBrief={onBrief} />,
    );
    return onChange;
  };
  const expand = () => fireEvent.click(screen.getByRole("button", { name: "Show modules in AI Engineering" }));

  it("replaces the directory chips with courses and beyond", () => {
    setup();
    expect(screen.queryByRole("button", { name: "rag" })).toBeNull();
    expect(screen.getByRole("button", { name: "AI Engineering 2" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("button", { name: "patterns 1" })).toBeInTheDocument();
  });

  it("filters by course, by module and by beyond directory", () => {
    const onChange = setup();
    fireEvent.click(screen.getByRole("button", { name: "AI Engineering 2" }));
    expect(onChange).toHaveBeenLastCalledWith(new Set(["course:ai"]));
    fireEvent.click(screen.getByRole("button", { name: "patterns 1" }));
    expect(onChange).toHaveBeenLastCalledWith(new Set(["beyond:patterns"]));
    expand();
    fireEvent.click(screen.getByRole("button", { name: "RAG 2" }));
    expect(onChange).toHaveBeenLastCalledWith(new Set(["module:ai/rag"]));
  });

  it("collapses modules until asked, and reports the state", () => {
    setup();
    expect(screen.queryByRole("button", { name: "RAG 2" })).toBeNull();
    const toggle = screen.getByRole("button", { name: "Show modules in AI Engineering" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(toggle);
    expect(screen.getByRole("button", { name: "Hide modules in AI Engineering" })).toHaveAttribute("aria-expanded", "true");
  });

  it("shows an empty module disabled, still linking its lessons, with no brief", () => {
    setup([], () => {});
    expand();
    expect(screen.getByRole("button", { name: "Visualisation 0" })).toBeDisabled();
    expect(screen.getByRole("link", { name: "Open lessons for Visualisation" })).toHaveAttribute("href", "#/courses/ai/viz/one");
    expect(screen.queryByRole("button", { name: "Brief me on Visualisation" })).toBeNull();
  });

  it("briefs a module by its course scope", () => {
    const onBrief = vi.fn();
    setup([], onBrief);
    expand();
    fireEvent.click(screen.getByRole("button", { name: "Brief me on RAG" }));
    expect(onBrief).toHaveBeenCalledWith("course/ai/rag");
  });

  it("shows a tag set from elsewhere so it can be cleared", () => {
    const onChange = setup(["rag", "course:ai"]);
    fireEvent.click(screen.getByRole("button", { name: "rag" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["course:ai"]));
  });
});
