import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { HealthStrip } from "../HealthStrip";

function stub(body: unknown, status = 200) {
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(body), { status })));
}

afterEach(() => vi.unstubAllGlobals());

const ROW = {
  date: "2026-11-05",
  pages: 987,
  hubs: [{ page: "x" }],
  metrics: {
    orphan_rate: { value: 0.01, status: "healthy" },
    average_degree: { value: 6.2, status: "watch" },
    main_component: { value: 0.5, status: "broken" },
    stale_rate: { value: 0.3, status: "report" },
    brand_new: { value: 1, status: "mystery" },
  },
};

describe("HealthStrip", () => {
  it("shows each metric with the status in the file", async () => {
    stub(ROW);
    render(<HealthStrip />);
    const strip = await screen.findByRole("region", { name: "Wiki health" });
    expect(strip).toHaveTextContent("2026-11-05");
    expect(strip).toHaveTextContent("orphans healthy");
    expect(strip).toHaveTextContent("links per page watch");
    expect(strip).toHaveTextContent("connected broken");
    expect(strip).toHaveTextContent("stale report");
  });

  it("never shows the page count", async () => {
    stub(ROW);
    render(<HealthStrip />);
    const strip = await screen.findByRole("region", { name: "Wiki health" });
    expect(strip.textContent).not.toContain("987");
    expect(strip.textContent?.toLowerCase()).not.toContain("pages");
  });

  it("an unknown status is shown as written, with no good or bad colour", async () => {
    stub(ROW);
    render(<HealthStrip />);
    const chip = (await screen.findByText("mystery")).parentElement;
    expect(chip).toHaveTextContent("brand new mystery");
    expect(chip?.className).toBe("health-chip ");
  });

  it("says so when there is no snapshot", async () => {
    stub({ date: null, metrics: {} });
    render(<HealthStrip />);
    expect(await screen.findByText("No wiki health snapshot yet")).toBeInTheDocument();
  });

  it("says so when the request fails, rather than looking healthy", async () => {
    stub({}, 500);
    render(<HealthStrip />);
    await waitFor(() => expect(screen.getByText("Wiki health unavailable")).toBeInTheDocument());
  });
});
