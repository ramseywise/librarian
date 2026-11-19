import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { HopField } from "../HopField";
import type { Field } from "../../utils/hopField";

vi.mock("@xyflow/react", () => ({ ViewportPortal: ({ children }: { children: ReactNode }) => <>{children}</> }));

const field = {
  sectors: [{ id: "rag", label: "RAG", color: "#08f" }],
  dots: [
    { id: "card", x: 0, y: 0, sector: 0, hop: 1, card: true, via: "open", from: { x: 1, y: 1 } },
    { id: "near", x: 5, y: 5, sector: 0, hop: 2, card: false, via: "card", from: { x: 0, y: 0 } },
    { id: "far", x: 9, y: 9, sector: 0, card: false, via: "" },
  ],
  arcs: [],
  labels: [],
  circle: { x: 0, y: 0, inner: 1, outer: 2 },
  frame: { x: 0, y: 0, w: 10, h: 10 },
  near: 1,
  far: 0,
  beyond: 1,
} as unknown as Field;

const draw = (showLinks?: boolean) =>
  render(<HopField field={field} titleOf={(id) => id} onOpenPage={vi.fn()} focus={null} onPickSector={vi.fn()} showLinks={showLinks} />)
    .container;

describe("HopField", () => {
  it("draws the link from a page in reach back towards the cards", () => {
    const c = draw();
    expect(c.querySelectorAll("line.hop-line--card")).toHaveLength(1);
    expect(c.querySelectorAll("line.hop-line:not(.hop-line--card)")).toHaveLength(1);
  });

  it("with Links off keeps the points and each card's tie, but no links", () => {
    const c = draw(false);
    expect(c.querySelectorAll("circle.hop-dot")).toHaveLength(3);
    expect(c.querySelectorAll("line.hop-line--card")).toHaveLength(1);
    expect(c.querySelectorAll("line.hop-line:not(.hop-line--card)")).toHaveLength(0);
  });
});
