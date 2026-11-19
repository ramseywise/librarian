import { fireEvent, render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import { describe, expect, it, vi } from "vitest";
import { MapBar } from "../MapBar";

const base: ComponentProps<typeof MapBar> = {
  view: { level: "atlas", grouping: "wiki" },
  revealedExtra: 0,
  onResetRevealed: () => {},
  nextCap: null,
  onExpand: () => {},
  refocus: null,
  onGrouping: () => {},
};

describe("MapBar", () => {
  it("has the switch, search and filters on the atlas, and no crumbs, count or Map popover", () => {
    const onGrouping = vi.fn();
    render(
      <MapBar {...base} onGrouping={onGrouping} search={<input aria-label="Search the map" />} filters={<p>the filters</p>} />,
    );
    expect(screen.getByRole("button", { name: "Wiki" })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(screen.getByRole("button", { name: "Modules" }));
    expect(onGrouping).toHaveBeenCalledWith("domain");
    expect(screen.getByLabelText("Search the map")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Filters" })).toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Map level" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Map" })).toBeNull();
  });

  it("opens Filters with the active count on its button, and Escape closes just the popover", () => {
    const onKey = vi.fn();
    document.addEventListener("keydown", onKey);
    render(<MapBar {...base} filters={<p>the filters</p>} activeCount={2} />);
    expect(screen.queryByText("the filters")).toBeNull();
    const button = screen.getByRole("button", { name: "Filters (2)" });
    fireEvent.click(button);
    expect(button).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("group", { name: "Filters" })).toHaveTextContent("the filters");
    fireEvent.keyDown(button, { key: "Escape" });
    expect(screen.queryByText("the filters")).toBeNull();
    expect(onKey.mock.calls[0][0].defaultPrevented).toBe(true);
    document.removeEventListener("keydown", onKey);
  });

  it("closes a popover on a click outside it", () => {
    render(<MapBar {...base} filters={<p>the filters</p>} />);
    fireEvent.click(screen.getByRole("button", { name: "Filters" }));
    fireEvent.mouseDown(document.body);
    expect(screen.queryByText("the filters")).toBeNull();
  });

  it("under the chat lists the filters, pins the connections below them, and has no layout", () => {
    const sector = { level: "sector", grouping: "wiki", sector: "rag", cap: 15 } as const;
    render(
      <MapBar
        {...base}
        controlsOnly
        view={sector}
        filters={<p>the filters</p>}
        connections={<p>the connections</p>}
        map={<p>the layout</p>}
      />,
    );
    expect(screen.getByRole("region", { name: "Filters" })).toHaveTextContent("the filters");
    // Outside the scrolling filters, so they stay in view however long the list is.
    const pinned = screen.getByText("the connections").closest(".map-dock-connect");
    expect(pinned).not.toBeNull();
    expect(pinned!.closest(".map-dock-scroll")).toBeNull();
    expect(screen.queryByRole("button", { name: "Filters" })).toBeNull();
    expect(screen.queryByRole("link", { name: "‹ Back" })).toBeNull();
    // Layout stays off the dock: arrangement and minimap keep their defaults there.
    expect(screen.queryByRole("button", { name: "Layout" })).toBeNull();
    expect(screen.queryByText("the layout")).toBeNull();
  });

  it("offers the Map popover on focused levels only when it has controls", () => {
    const sector = { level: "sector", grouping: "wiki", sector: "rag", cap: 15 } as const;
    const { rerender } = render(<MapBar {...base} view={sector} />);
    expect(screen.queryByRole("button", { name: "Map" })).toBeNull();
    rerender(<MapBar {...base} view={sector} map={<p>connections</p>} />);
    fireEvent.click(screen.getByRole("button", { name: "Map" }));
    expect(screen.getByText("connections")).toBeInTheDocument();
  });

  it("briefs on the sector from its crumb, and the switch goes to the other atlas", () => {
    const onBriefSector = vi.fn();
    const onGrouping = vi.fn();
    render(
      <MapBar
        {...base}
        view={{ level: "sector", grouping: "domain", sector: "generative-ai", cap: 15 }}
        sectorLabel="Generative AI"
        onBriefSector={onBriefSector}
        onGrouping={onGrouping}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Brief me on Generative AI" }));
    expect(onBriefSector).toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Wiki" }));
    expect(onGrouping).toHaveBeenCalledWith("wiki");
  });

  it("shows the breadcrumb, the count and the way out at page level", () => {
    const onExpand = vi.fn();
    render(
      <MapBar
        {...base}
        view={{ level: "page", grouping: "domain", sector: "data-science", page: "p", cap: 60 }}
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
    expect(screen.getByRole("link", { name: "Atlas" })).toHaveAttribute("href", "#/map/domain");
    expect(screen.getByRole("link", { name: "Data Science" })).toHaveAttribute("href", "#/map/domain/data-science");
    expect(screen.getByRole("link", { name: /Back/ })).toHaveAttribute("href", "#/map/domain/data-science");
    expect(screen.getByText("showing 60 of 900 · 2 hops")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Show 120" }));
    expect(onExpand).toHaveBeenCalled();
  });

  it("names the current level without a link, and offers no expansion at the end", () => {
    render(
      <MapBar {...base} view={{ level: "sector", grouping: "wiki", sector: "rag", cap: 150 }} shown={34} total={34} />,
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
