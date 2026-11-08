import { fireEvent, render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import { describe, expect, it, vi } from "vitest";
import { MapBar } from "../MapBar";

const base: ComponentProps<typeof MapBar> = {
  view: { level: "atlas", grouping: "domain" },
  revealedExtra: 0,
  onResetRevealed: () => {},
  nextCap: null,
  onExpand: () => {},
  refocus: null,
};

describe("MapBar", () => {
  it("draws nothing on the atlas: the switch and search are in the sidebar", () => {
    const { container } = render(<MapBar {...base} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the breadcrumb, the count and the way out at page level", () => {
    const onExpand = vi.fn();
    render(
      <MapBar
        {...base}
        view={{ level: "page", grouping: "course", sector: "data-science", page: "p", cap: 60 }}
        sectorLabel="Data Science"
        pageTitle="A Page"
        shown={60}
        total={900}
        hops={2}
        nextCap={120}
        onExpand={onExpand}
      />,
    );
    const crumbs = screen.getByRole("navigation", { name: "Map level" });
    expect(crumbs).toHaveTextContent("Atlas/Data Science/A Page");
    expect(screen.getByRole("link", { name: "Atlas" })).toHaveAttribute("href", "#/map/course");
    expect(screen.getByRole("link", { name: "Data Science" })).toHaveAttribute("href", "#/map/course/data-science");
    expect(screen.getByRole("link", { name: /Back/ })).toHaveAttribute("href", "#/map/course/data-science");
    expect(screen.getByText("showing 60 of 900 · 2 hops")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Show 120" }));
    expect(onExpand).toHaveBeenCalled();
  });

  it("names the current level without a link, and offers no expansion at the end", () => {
    render(
      <MapBar {...base} view={{ level: "sector", grouping: "domain", sector: "rag", cap: 150 }} shown={34} total={34} />,
    );
    expect(screen.getByText("rag")).toHaveAttribute("aria-current", "page");
    expect(screen.getByText("showing 34 of 34")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Show/ })).toBeNull();
  });

  it("returns from All nodes to the atlas", () => {
    render(<MapBar {...base} view={{ level: "all", tags: [] }} shown={112} total={112} />);
    expect(screen.getByText("All nodes")).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: /Back/ })).toHaveAttribute("href", "#/map/domain");
  });
});
