import { cleanup, render } from "@testing-library/react";
import axe from "axe-core";
import type { ComponentProps, ReactElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AppNav } from "../AppNav";
import { ErrorBoundary } from "../ErrorBoundary";
import { MapBar } from "../MapBar";
import { ResourceNotice } from "../ResourceNotice";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

/** Rules axe can judge in jsdom; colour contrast needs real layout and styles, so it is skipped. */
async function violations(ui: ReactElement): Promise<string[]> {
  const { container } = render(ui);
  const result = await axe.run(container, { rules: { "color-contrast": { enabled: false } } });
  return result.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(" ")).join(", ")}`);
}

const barProps: ComponentProps<typeof MapBar> = {
  view: { level: "atlas", grouping: "wiki" },
  revealedExtra: 0,
  onResetRevealed: () => {},
  nextCap: null,
  onExpand: () => {},
  refocus: null,
  onGrouping: () => {},
};

function Bomb(): never {
  throw new Error("chunk failed");
}

describe("accessibility (axe)", () => {
  it("ResourceNotice", async () => {
    expect(await violations(<ResourceNotice what="The glossary" error="HTTP 500" onRetry={() => {}} />)).toEqual([]);
  });

  it("ErrorBoundary fallback", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    expect(await violations(<ErrorBoundary what="This page"><Bomb /></ErrorBoundary>)).toEqual([]);
  });

  it("MapBar", async () => {
    expect(await violations(<MapBar {...barProps} search={<input aria-label="Search the map" />} />)).toEqual([]);
  });

  it("AppNav", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("[]", { status: 200 })));
    expect(await violations(<AppNav id="nav" route="/" open={false} />)).toEqual([]);
  });
});
