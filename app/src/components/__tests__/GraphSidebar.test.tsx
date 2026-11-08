import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GraphSidebar } from "../GraphSidebar";
import type { Facets, Glossary } from "../../types";

const term = (id: string, label: string) => ({ id, label, aliases: [], def: "", page: null, mentions: 1 });
const glossary: Glossary = {
  terms: [term("bm25", "BM25"), term("rrf", "Reciprocal Rank Fusion"), term("unused", "Unused")],
  mentions: { bm25: ["a", "b"], rrf: ["a"] },
};
const facets: Facets = new Map([
  ["tag:rag", new Set(["a", "b"])],
  ["tag:pattern", new Set(["a"])],
  ["term:bm25", new Set(["a", "b"])],
  ["term:rrf", new Set(["a"])],
]);

function renderSidebar(activeTags = new Set<string>(), onChange = vi.fn()) {
  render(
    <GraphSidebar
      id="graph-controls"
      open={false}
      domains={["rag"]}
      curriculum={null}
      glossary={glossary}
      facets={facets}
      activeTags={activeTags}
      onChange={onChange}
    />,
  );
  return onChange;
}

describe("GraphSidebar", () => {
  it("lists the top topic tags, the rest behind more, and an active one always", () => {
    const many: Facets = new Map(
      Array.from({ length: 15 }, (_, i) => [`tag:t${i}`, new Set(Array.from({ length: 20 - i }, (_, j) => `p${j}`))]),
    );
    render(
      <GraphSidebar id="s" open={false} domains={[]} curriculum={null} glossary={null}
        facets={many} activeTags={new Set(["tag:t14"])} onChange={vi.fn()} />,
    );
    const topic = screen.getByRole("group", { name: "Topic tags" });
    expect(within(topic).queryByRole("button", { name: /^t13/ })).toBeNull();
    expect(within(topic).getByRole("button", { name: /^t14/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(within(topic).getByRole("button", { name: "+3 more" }));
    expect(within(topic).getByRole("button", { name: /^t13/ })).toBeInTheDocument();
  });


  it("splits topic and type tags, and a tag chip filters by `tag:`", () => {
    const onChange = renderSidebar();
    const topic = screen.getByRole("group", { name: "Topic tags" });
    const type = screen.getByRole("group", { name: "Type tags" });
    expect(within(type).getByRole("button", { name: /pattern/ })).toBeInTheDocument();
    fireEvent.click(within(topic).getByRole("button", { name: /rag/ }));
    expect(onChange).toHaveBeenCalledWith(new Set(["tag:rag"]));
  });

  it("lists mentioned glossary terms, narrows them by search, and filters by `term:`", () => {
    const onChange = renderSidebar();
    const terms = screen.getByRole("group", { name: "Glossary terms" });
    expect(within(terms).queryByRole("button", { name: /Unused/ })).toBeNull();
    fireEvent.change(screen.getByRole("searchbox", { name: "Search glossary terms" }), { target: { value: "fusion" } });
    expect(within(terms).queryByRole("button", { name: /BM25/ })).toBeNull();
    fireEvent.click(within(terms).getByRole("button", { name: /Reciprocal Rank Fusion/ }));
    expect(onChange).toHaveBeenCalledWith(new Set(["term:rrf"]));
  });

  it("an active term stays listed whatever the search, and Clear empties the filter", () => {
    const onChange = renderSidebar(new Set(["term:bm25"]));
    fireEvent.change(screen.getByRole("searchbox", { name: "Search glossary terms" }), { target: { value: "fusion" } });
    const terms = screen.getByRole("group", { name: "Glossary terms" });
    expect(within(terms).getByRole("button", { name: /BM25/ })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(screen.getByRole("button", { name: "Clear (1)" }));
    expect(onChange).toHaveBeenCalledWith(new Set());
  });
});
