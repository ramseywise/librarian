import { describe, expect, it } from "vitest";
import { IDLE, elapsedAt, formatCountdown, timerReducer } from "../useDrillTimer";

describe("timerReducer", () => {
  it("banks elapsed time across start/pause and resets", () => {
    let s = timerReducer(IDLE, { type: "start", now: 1_000 });
    expect(s).toEqual({ elapsedMs: 0, startedAt: 1_000 });
    expect(timerReducer(s, { type: "start", now: 5_000 })).toBe(s); // already running
    expect(elapsedAt(s, 4_000)).toBe(3_000);
    s = timerReducer(s, { type: "pause", now: 11_000 });
    expect(s).toEqual({ elapsedMs: 10_000, startedAt: null });
    expect(timerReducer(s, { type: "pause", now: 99_000 })).toBe(s); // already paused
    expect(elapsedAt(s, 99_000)).toBe(10_000);
    s = timerReducer(s, { type: "start", now: 20_000 });
    expect(elapsedAt(s, 25_000)).toBe(15_000);
    expect(timerReducer(s, { type: "reset" })).toEqual(IDLE);
  });

  it("never counts backwards if the clock moves back", () => {
    expect(elapsedAt({ elapsedMs: 500, startedAt: 10_000 }, 9_000)).toBe(500);
  });
});

describe("formatCountdown", () => {
  it("counts down, hits 00:00 at the limit, then shows overtime", () => {
    expect(formatCountdown(20 * 60_000)).toBe("20:00");
    expect(formatCountdown(59_001)).toBe("01:00");
    expect(formatCountdown(0)).toBe("00:00");
    expect(formatCountdown(-999)).toBe("00:00");
    expect(formatCountdown(-65_000)).toBe("+01:05");
  });
});
