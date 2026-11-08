import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TagFilterPanel } from "../TagFilterPanel";
import type { Curriculum } from "../../types";

describe("TagFilterPanel", () => {
  it("says so while the curriculum loads", () => {
    render(<TagFilterPanel activeTags={new Set()} onChange={() => {}} />);
    expect(screen.getByText("Loading courses…")).toBeInTheDocument();
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
      <TagFilterPanel curriculum={curriculum} activeTags={new Set(active)} onChange={onChange} onBrief={onBrief} />,
    );
    return onChange;
  };
  const expand = () => fireEvent.click(screen.getByRole("button", { name: "Show modules in AI Engineering" }));

  it("lists courses and one row for the pages in none, not a chip per directory", () => {
    setup();
    expect(screen.getByRole("button", { name: "AI Engineering 2" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("button", { name: "Not in a course 1" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "patterns 1" })).toBeNull();
  });

  it("filters by course, by module and by pages in no course", () => {
    const onChange = setup();
    fireEvent.click(screen.getByRole("button", { name: "AI Engineering 2" }));
    expect(onChange).toHaveBeenLastCalledWith(new Set(["course:ai"]));
    fireEvent.click(screen.getByRole("button", { name: "Not in a course 1" }));
    expect(onChange).toHaveBeenLastCalledWith(new Set(["beyond:all"]));
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
