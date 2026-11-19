import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FiltersPanel, TagFilterPanel } from "../TagFilterPanel";
import type { Area, Curriculum, Facets, Glossary } from "../../types";

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
          { id: "rag", title: "RAG", firstLesson: "ai/rag/one", pageIds: ["a", "b"], notes: [] },
          { id: "viz", title: "Visualisation", firstLesson: "ai/viz/one", pageIds: [], notes: [] },
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

describe("FiltersPanel", () => {
  const term = (id: string, label: string) => ({ id, label, aliases: [], def: "", page: null, mentions: 1 });
  const glossary: Glossary = {
    terms: [term("bm25", "BM25"), term("rrf", "Reciprocal Rank Fusion"), term("unused", "Unused")],
    mentions: { bm25: ["a", "b"], rrf: ["a"] },
  };
  const curriculum: Curriculum = {
    courses: [
      {
        id: "generative-ai",
        title: "Generative AI",
        pageIds: ["a"],
        modules: [{ id: "02-rag", title: "RAG", pageIds: ["a"], firstLesson: "generative-ai/02-rag/intro", notes: [] }],
      },
    ],
    beyond: [{ domain: "loose", pageIds: ["c"] }],
    primaryCourse: { a: "generative-ai" },
    stale: false,
  };
  const areas: Area[] = [
    { id: "generative-ai", title: "Generative AI", domains: ["rag"] },
    { id: "programming", title: "Programming", domains: ["programming"] },
  ];
  const facets: Facets = new Map([
    ["dir:rag", new Set(["a", "b"])],
    ["dir:programming", new Set(["p"])],
    ["dir:loose", new Set(["c"])],
    ["gap:generative-ai", new Set(["b"])],
    ["gap:programming", new Set()],
    ["beyond:loose", new Set(["c"])],
    ["beyond:all", new Set(["c"])],
    ["beyond:rag", new Set(["b"])],
    ["module:generative-ai/02-rag", new Set(["a"])],
    ["tag:rag", new Set(["a", "b"])],
    ["tag:pattern", new Set(["a"])],
    ["term:bm25", new Set(["a", "b"])],
    ["term:rrf", new Set(["a"])],
  ]);

  function setup(activeTags = new Set<string>(), over: Partial<Parameters<typeof FiltersPanel>[0]> = {}) {
    const onChange = vi.fn();
    const onBrief = vi.fn();
    render(
      <FiltersPanel
        areas={areas}
        curriculum={curriculum}
        glossary={glossary}
        facets={facets}
        activeTags={activeTags}
        onChange={onChange}
        onBrief={onBrief}
        {...over}
      />,
    );
    return { onChange, onBrief };
  }

  const wiki = { grouping: "wiki" as const };

  it("Modules lists the modules only; Wiki lists the wiki topics only, with no drop-downs", () => {
    setup();
    expect(screen.getByRole("group", { name: "Filter by module" })).toBeInTheDocument();
    expect(screen.queryByRole("group", { name: "Wiki topics" })).toBeNull();
    cleanup();
    setup(new Set(), wiki);
    expect(screen.getByRole("group", { name: "Wiki topics" })).toBeInTheDocument();
    expect(screen.queryByRole("group", { name: "Filter by module" })).toBeNull();
    expect(document.querySelector("details")).toBeNull();
    expect(screen.queryByRole("button", { name: /^Show / })).toBeNull();
  });

  it("lists the directories first, largest first, each with a brief, and filters by `dir:`", () => {
    const { onBrief, onChange } = setup(new Set(), wiki);
    const topics = screen.getByRole("group", { name: "Wiki topics" });
    const names = within(topics)
      .getAllByRole("button", { name: /^\w+ \d+$/ })
      .map((b) => b.getAttribute("aria-label") ?? b.textContent);
    expect(names.slice(0, 3)).toEqual(["rag 2", "loose 1", "programming 1"]);
    fireEvent.click(within(topics).getByRole("button", { name: "Brief me on rag" }));
    expect(onBrief).toHaveBeenCalledWith("rag");
    fireEvent.click(within(topics).getByRole("button", { name: "loose 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["dir:loose"]));
  });

  it("merges topic tags and glossary terms after the directories, never a page type or a directory twice", () => {
    const { onChange } = setup(new Set(), wiki);
    const topics = screen.getByRole("group", { name: "Wiki topics" });
    // tag:rag is the rag directory; pattern is a page type; rrf is on one page only.
    expect(within(topics).getAllByRole("button", { name: /^rag/ })).toHaveLength(1);
    expect(within(topics).queryByRole("button", { name: /pattern/ })).toBeNull();
    expect(within(topics).queryByRole("button", { name: /Reciprocal/ })).toBeNull();
    fireEvent.click(within(topics).getByRole("button", { name: "BM25 2" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["term:bm25"]));
  });

  it("lists the top topics, the rest behind more, and an active one always", () => {
    const many: Facets = new Map(
      Array.from({ length: 19 }, (_, i) => [`tag:t${i}`, new Set(Array.from({ length: 30 - i }, (_, j) => `p${j}`))]),
    );
    setup(new Set(["tag:t18"]), { ...wiki, facets: many, areas: [], curriculum: null, glossary: null });
    const topics = screen.getByRole("group", { name: "Wiki topics" });
    expect(within(topics).queryByRole("button", { name: /^t17/ })).toBeNull();
    expect(within(topics).getByRole("button", { name: /^t18/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(within(topics).getByRole("button", { name: "+3 more" }));
    expect(within(topics).getByRole("button", { name: /^t17/ })).toBeInTheDocument();
  });

  it("lists each course's modules as chips after its name, then its pages no lesson links, then the pages in no course", () => {
    const { onChange, onBrief } = setup();
    const course = screen.getByRole("group", { name: "Generative AI" });
    expect(within(course).getAllByRole("button").map((b) => b.textContent)).toEqual([
      "Generative AI",
      "RAG 1",
      "↗",
      "not yet in a lesson 1",
    ]);
    fireEvent.click(within(course).getByRole("button", { name: "RAG 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["module:generative-ai/02-rag"]));
    fireEvent.click(within(course).getByRole("button", { name: "Brief me on RAG" }));
    expect(onBrief).toHaveBeenCalledWith("course/generative-ai/02-rag");
    fireEvent.click(within(course).getByRole("button", { name: "Generative AI" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["course:generative-ai"]));
    fireEvent.click(within(course).getByRole("button", { name: "not yet in a lesson 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["gap:generative-ai"]));
    fireEvent.click(screen.getByRole("button", { name: "Not in a course 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["beyond:all"]));
  });

  it("says so while the courses load", () => {
    setup(new Set(), { curriculum: null });
    expect(screen.getByText("Loading courses…")).toBeInTheDocument();
  });

  it("keeps a filter set in the other view as a chip, and Clear empties the filter", () => {
    const { onChange } = setup(new Set(["term:bm25"]));
    const active = screen.getByRole("group", { name: "Active filters" });
    expect(within(active).getByRole("button", { name: /BM25/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(screen.getByRole("button", { name: "Clear" }));
    expect(onChange).toHaveBeenCalledWith(new Set());
  });

  it("Clear is off with no filter active", () => {
    setup();
    expect(screen.getByRole("button", { name: "Clear" })).toBeDisabled();
  });

  it("shows a module set by a link pressed among the chips, so it can be switched off there", () => {
    const { onChange } = setup(new Set(["module:generative-ai/02-rag"]));
    expect(screen.queryByRole("group", { name: "Active filters" })).toBeNull();
    const chip = screen.getByRole("button", { name: "RAG 1" });
    expect(chip).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(chip);
    expect(onChange).toHaveBeenCalledWith(new Set());
  });

  it("still names an area set by a link, which no section lists", () => {
    setup(new Set(["area:programming"]));
    expect(within(screen.getByRole("group", { name: "Active filters" })).getByRole("button", { name: "Programming" })).toBeInTheDocument();
  });

  it("keeps a note set by a link as a chip, since Modules lists no notes", () => {
    setup(new Set(["note:generative-ai/02-rag/notes/01-bm25"]));
    expect(within(screen.getByRole("group", { name: "Active filters" })).getByRole("button", { name: "01-bm25" })).toBeInTheDocument();
  });
});
