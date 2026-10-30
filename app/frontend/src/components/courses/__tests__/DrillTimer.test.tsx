import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { DrillTimer } from "../DrillTimer";

afterEach(() => {
  cleanup();
  sessionStorage.clear();
});

const paused = (id: string, elapsedMs: number) =>
  sessionStorage.setItem(`librarian.timer.${id}`, JSON.stringify({ elapsedMs, startedAt: null }));

describe("DrillTimer label", () => {
  it("reads 'timebox reached' at exactly the limit, not a clipped clock", () => {
    paused("a", 20 * 60_000);
    render(<DrillTimer lessonId="a" timeboxMin={20} />);
    expect(screen.getByRole("timer")).toHaveAccessibleName("20-minute timebox reached");
  });

  it("reports overtime without the + sign", () => {
    paused("b", 20 * 60_000 + 65_000);
    render(<DrillTimer lessonId="b" timeboxMin={20} />);
    expect(screen.getByRole("timer")).toHaveAccessibleName("Over the 20-minute timebox by 01:05");
  });
});
