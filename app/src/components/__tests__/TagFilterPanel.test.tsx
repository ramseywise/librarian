import { fireEvent, render, screen, within } from "@testing-library/react";
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
        modules: [{ id: "02-rag", title: "RAG", pageIds: ["a"], firstLesson: "generative-ai/02-rag/intro" }],
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

  it("lists the wiki directories with their page counts and a brief each", () => {
    const { onBrief } = setup();
    const dirs = screen.getByRole("group", { name: "Filter by directory" });
    expect(within(dirs).getByRole("button", { name: "rag 2" })).toBeInTheDocument();
    fireEvent.click(within(dirs).getByRole("button", { name: "Brief me on rag" }));
    expect(onBrief).toHaveBeenCalledWith("rag");
    expect(screen.queryByText("Page type")).toBeNull();
    expect(screen.queryByRole("group", { name: "Filter by domain" })).toBeNull();
  });

  it("a directory chip filters by `dir:`", () => {
    const { onChange } = setup();
    fireEvent.click(within(screen.getByRole("group", { name: "Filter by directory" })).getByRole("button", { name: "loose 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["dir:loose"]));
  });

  it("offers the pages no lesson links per course area and per loose directory, never an empty one", () => {
    const { onChange } = setup();
    const gaps = screen.getByRole("group", { name: "Not yet in a lesson" });
    expect(within(gaps).queryByRole("button", { name: /^Programming/ })).toBeNull();
    // A directory the area covers is its area's gap, not a row of its own.
    expect(within(gaps).queryByRole("button", { name: /^rag/ })).toBeNull();
    fireEvent.click(within(gaps).getByRole("button", { name: "Generative AI 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["gap:generative-ai"]));
    fireEvent.click(within(gaps).getByRole("button", { name: "loose 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["beyond:loose"]));
  });

  it("has no gap section until the curriculum is in", () => {
    setup(new Set(), { curriculum: null });
    expect(screen.queryByText("Not yet in a lesson")).toBeNull();
  });

  it("lists the top topic tags, the rest behind more, and an active one always", () => {
    const many: Facets = new Map(
      Array.from({ length: 15 }, (_, i) => [`tag:t${i}`, new Set(Array.from({ length: 20 - i }, (_, j) => `p${j}`))]),
    );
    setup(new Set(["tag:t14"]), { facets: many, areas: [], curriculum: null, glossary: null });
    const topic = screen.getByRole("group", { name: "Filter by tag" });
    expect(within(topic).queryByRole("button", { name: /^t13/ })).toBeNull();
    expect(within(topic).getByRole("button", { name: /^t14/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(within(topic).getByRole("button", { name: "+3 more" }));
    expect(within(topic).getByRole("button", { name: /^t13/ })).toBeInTheDocument();
  });

  it("lists topic tags only, never a page type, and a tag chip filters by `tag:`", () => {
    const { onChange } = setup();
    const topic = screen.getByRole("group", { name: "Filter by tag" });
    expect(within(topic).queryByRole("button", { name: /pattern/ })).toBeNull();
    fireEvent.click(within(topic).getByRole("button", { name: /rag/ }));
    expect(onChange).toHaveBeenCalledWith(new Set(["tag:rag"]));
  });

  it("lists mentioned glossary terms, narrows them by search, and filters by `term:`", () => {
    const { onChange } = setup();
    const terms = screen.getByRole("group", { name: "Glossary terms" });
    expect(within(terms).queryByRole("button", { name: /Unused/ })).toBeNull();
    fireEvent.change(screen.getByRole("searchbox", { name: "Search glossary terms" }), { target: { value: "fusion" } });
    expect(within(terms).queryByRole("button", { name: /BM25/ })).toBeNull();
    fireEvent.click(within(terms).getByRole("button", { name: /Reciprocal Rank Fusion/ }));
    expect(onChange).toHaveBeenCalledWith(new Set(["term:rrf"]));
  });

  it("an active term stays listed whatever the search, and Clear empties the filter", () => {
    const { onChange } = setup(new Set(["term:bm25"]));
    fireEvent.change(screen.getByRole("searchbox", { name: "Search glossary terms" }), { target: { value: "fusion" } });
    const terms = screen.getByRole("group", { name: "Glossary terms" });
    expect(within(terms).getByRole("button", { name: /BM25/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(screen.getByRole("button", { name: "Clear" }));
    expect(onChange).toHaveBeenCalledWith(new Set());
  });

  it("Clear is off with no filter active", () => {
    setup();
    expect(screen.getByRole("button", { name: "Clear" })).toBeDisabled();
  });

  it("lists a module set by a link in the open course tree, so it can be switched off there", () => {
    const { onChange } = setup(new Set(["module:generative-ai/02-rag"]));
    expect(screen.queryByRole("group", { name: "Active filters" })).toBeNull();
    const tree = screen.getByRole("group", { name: "Filter by curriculum" });
    const row = within(tree).getByRole("button", { name: /^RAG/ });
    expect(row).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(row);
    expect(onChange).toHaveBeenCalledWith(new Set());
  });

  it("orders the sections broadest first: course, domain, term, tag, then gaps", () => {
    setup();
    const titles = [...document.querySelectorAll(".side-section > summary")].map((s) => s.textContent);
    expect(titles).toEqual(["Course › module", "Domain", "Glossary term", "Tag", "Not yet in a lesson"]);
  });

  it("still names an area set by a link, which no section lists", () => {
    setup(new Set(["area:programming"]));
    expect(within(screen.getByRole("group", { name: "Active filters" })).getByRole("button", { name: "Programming" })).toBeInTheDocument();
  });
});
