import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GraphSidebar } from "../GraphSidebar";
import type { Area, Curriculum, Facets, Glossary } from "../../types";
import type { Grouping } from "../../utils/mapRoute";

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
      modules: [
        { id: "02-rag", title: "RAG", pageIds: ["a"], firstLesson: "generative-ai/02-rag/intro" },
        { id: "03-eval", title: "Evaluation", pageIds: [], firstLesson: null },
      ],
    },
    { id: "programming", title: "Programming", pageIds: ["p"], modules: [] },
  ],
  beyond: [{ domain: "loose", pageIds: ["c"] }],
  primaryCourse: { a: "generative-ai", p: "programming" },
  stale: false,
};
const areas: Area[] = [
  { id: "generative-ai", title: "Generative AI", domains: ["rag"] },
  { id: "programming", title: "Programming", domains: ["programming"] },
  { id: "data-science", title: "Data Science", domains: ["data-science"] },
];
const facets: Facets = new Map([
  ["dir:rag", new Set(["a", "b"])],
  ["dir:programming", new Set(["p"])],
  ["dir:data-science", new Set(["d"])],
  ["area:data-science", new Set(["d"])],
  ["dir:loose", new Set(["c"])],
  ["area:generative-ai", new Set(["a", "b"])],
  ["area:programming", new Set(["p"])],
  ["gap:generative-ai", new Set(["b"])],
  ["beyond:loose", new Set(["c"])],
  ["module:generative-ai/02-rag", new Set(["a"])],
  ["tag:rag", new Set(["a", "b"])],
  ["tag:pattern", new Set(["a"])],
  ["term:bm25", new Set(["a", "b"])],
  ["term:rrf", new Set(["a"])],
]);
const titles: Record<string, string> = { a: "Alpha Page", b: "Beta Page", c: "Loose Page", p: "Python Page" };

function renderSidebar(activeTags = new Set<string>(), onChange = vi.fn(), grouping: Grouping = "wiki", onGrouping = vi.fn(), onOpenPage = vi.fn()) {
  render(
    <GraphSidebar
      id="graph-controls"
      open={false}
      grouping={grouping}
      onGrouping={onGrouping}
      onBrief={vi.fn()}
      areas={areas}
      curriculum={curriculum}
      glossary={glossary}
      facets={facets}
      activeTags={activeTags}
      onChange={onChange}
      titleOf={(id) => titles[id] ?? id}
      onOpenPage={onOpenPage}
    />,
  );
  return { onChange, onOpenPage };
}

describe("GraphSidebar", () => {
  it("Wiki is three folding sections (directories, glossary, tags), no page types or list, and the switch reports Domain", () => {
    const onGrouping = vi.fn();
    renderSidebar(new Set(), vi.fn(), "wiki", onGrouping);
    expect(screen.getByRole("button", { name: "Wiki" })).toHaveAttribute("aria-pressed", "true");
    const dirs = screen.getByRole("group", { name: "Filter by directory" });
    expect(within(dirs).getByRole("button", { name: "rag 2" })).toBeInTheDocument();
    expect(within(dirs).getByRole("button", { name: "Brief me on rag" })).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Glossary terms" })).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Filter by tag" })).toBeInTheDocument();
    expect(screen.queryByText("Page type")).toBeNull();
    expect(screen.queryByText("More filters")).toBeNull();
    expect(screen.queryByText("Browse as a list")).toBeNull();
    expect(screen.queryByText("Wiki health")).toBeNull();
    expect(screen.queryByRole("group", { name: "Filter by domain" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Domain" }));
    expect(onGrouping).toHaveBeenCalledWith("domain");
  });

  it("Domain lists every course as its own row, in ring order, with loose directories after", () => {
    const { onChange } = renderSidebar(new Set(), vi.fn(), "domain");
    const tree = screen.getByRole("group", { name: "Filter by domain" });
    const rows = within(tree).getAllByRole("button", { pressed: false }).map((b) => b.textContent).filter((t) => /\d$/.test(t ?? ""));
    expect(rows).toEqual(["Generative AI 2", "Programming 1", "Data Science 1", "loose 1"]);
    expect(within(tree).queryByText(/Data & ML Foundations/)).toBeNull();
    expect(within(tree).queryByText("Not in a course")).toBeNull();
    fireEvent.click(within(tree).getByRole("button", { name: "Generative AI 2" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["area:generative-ai"]));
    expect(screen.queryByRole("group", { name: "Filter by directory" })).toBeNull();
    expect(screen.queryByRole("group", { name: "Filter by tag" })).toBeNull();
    expect(screen.queryByRole("group", { name: "Glossary terms" })).toBeNull();
  });

  it("opens a course to its modules and gap, a module to its pages, and a page row opens the page", () => {
    const { onChange, onOpenPage } = renderSidebar(new Set(), vi.fn(), "domain");
    fireEvent.click(screen.getByRole("button", { name: "Show modules in Generative AI" }));
    fireEvent.click(screen.getByRole("button", { name: "RAG 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["module:generative-ai/02-rag"]));
    expect(screen.getByRole("button", { name: "Evaluation 0" })).toBeDisabled();
    expect(screen.getByRole("link", { name: "Open lessons for RAG" })).toHaveAttribute("href", "#/courses/generative-ai/02-rag/intro");
    fireEvent.click(screen.getByRole("button", { name: "Not yet in a lesson 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["gap:generative-ai"]));
    fireEvent.click(screen.getByRole("button", { name: "Show pages in RAG" }));
    fireEvent.click(screen.getByRole("button", { name: "Alpha Page" }));
    expect(onOpenPage).toHaveBeenCalledWith("a");
    fireEvent.click(screen.getByRole("button", { name: "Show pages not yet in a lesson" }));
    expect(screen.getByRole("button", { name: "Beta Page" })).toBeInTheDocument();
  });

  it("a loose directory filters by `dir:` and its gap by `beyond:`", () => {
    const { onChange } = renderSidebar(new Set(), vi.fn(), "domain");
    fireEvent.click(screen.getByRole("button", { name: "loose 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["dir:loose"]));
    fireEvent.click(screen.getByRole("button", { name: "Show pages in loose" }));
    fireEvent.click(screen.getByRole("button", { name: "Not yet in a lesson 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["beyond:loose"]));
  });

  it("shows no gap row until the curriculum is in", () => {
    render(
      <GraphSidebar id="s" open={false} grouping="domain" onGrouping={vi.fn()} areas={areas} curriculum={null} glossary={null}
        facets={facets} activeTags={new Set()} onChange={vi.fn()} />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Show modules in Generative AI" }));
    expect(screen.queryByRole("button", { name: /Not yet in a lesson/ })).toBeNull();
    expect(screen.getByText("Loading courses…")).toBeInTheDocument();
  });

  it("a directory chip filters by `dir:`", () => {
    const { onChange } = renderSidebar();
    fireEvent.click(within(screen.getByRole("group", { name: "Filter by directory" })).getByRole("button", { name: "loose 1" }));
    expect(onChange).toHaveBeenCalledWith(new Set(["dir:loose"]));
  });

  it("lists the top topic tags, the rest behind more, and an active one always", () => {
    const many: Facets = new Map(
      Array.from({ length: 15 }, (_, i) => [`tag:t${i}`, new Set(Array.from({ length: 20 - i }, (_, j) => `p${j}`))]),
    );
    render(
      <GraphSidebar id="s" open={false} grouping="wiki" onGrouping={vi.fn()} areas={[]} curriculum={null} glossary={null}
        facets={many} activeTags={new Set(["tag:t14"])} onChange={vi.fn()} />,
    );
    const topic = screen.getByRole("group", { name: "Filter by tag" });
    expect(within(topic).queryByRole("button", { name: /^t13/ })).toBeNull();
    expect(within(topic).getByRole("button", { name: /^t14/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(within(topic).getByRole("button", { name: "+3 more" }));
    expect(within(topic).getByRole("button", { name: /^t13/ })).toBeInTheDocument();
  });

  it("lists topic tags only, never a page type, and a tag chip filters by `tag:`", () => {
    const { onChange } = renderSidebar();
    const topic = screen.getByRole("group", { name: "Filter by tag" });
    expect(within(topic).queryByRole("button", { name: /pattern/ })).toBeNull();
    fireEvent.click(within(topic).getByRole("button", { name: /rag/ }));
    expect(onChange).toHaveBeenCalledWith(new Set(["tag:rag"]));
  });

  it("lists mentioned glossary terms, narrows them by search, and filters by `term:`", () => {
    const { onChange } = renderSidebar();
    const terms = screen.getByRole("group", { name: "Glossary terms" });
    expect(within(terms).queryByRole("button", { name: /Unused/ })).toBeNull();
    fireEvent.change(screen.getByRole("searchbox", { name: "Search glossary terms" }), { target: { value: "fusion" } });
    expect(within(terms).queryByRole("button", { name: /BM25/ })).toBeNull();
    fireEvent.click(within(terms).getByRole("button", { name: /Reciprocal Rank Fusion/ }));
    expect(onChange).toHaveBeenCalledWith(new Set(["term:rrf"]));
  });

  it("an active term stays listed whatever the search, and Clear empties the filter", () => {
    const { onChange } = renderSidebar(new Set(["term:bm25"]));
    fireEvent.change(screen.getByRole("searchbox", { name: "Search glossary terms" }), { target: { value: "fusion" } });
    const terms = screen.getByRole("group", { name: "Glossary terms" });
    expect(within(terms).getByRole("button", { name: /BM25/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(screen.getByRole("button", { name: "Clear (1)" }));
    expect(onChange).toHaveBeenCalledWith(new Set());
  });
});
