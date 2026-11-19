import { describe, expect, it } from "vitest";
import { bandOf, bandRadius, type AtlasSector, type Ring, type RingGeometry } from "../../../utils/atlas";
import { insetsFor, spikeFrame, spikeFrameWithStates, towards } from "../atlasFrames";

describe("towards", () => {
  it("moves a fraction of the way", () => {
    expect(towards(0, 1, 0)).toBe(0);
    expect(towards(0, 1, 1)).toBeCloseTo(1);
    expect(towards(0, 1, 0.5)).toBeCloseTo(0.5);
  });

  it("takes the short way round the circle", () => {
    const tau = Math.PI * 2;
    // 350 degrees to 10 degrees is 20 degrees forward, not 340 back.
    const a = (350 / 360) * tau;
    const b = (10 / 360) * tau;
    expect(towards(a, b, 1)).toBeCloseTo(a + (20 / 360) * tau);
    expect(towards(b, a, 1)).toBeCloseTo(b - (20 / 360) * tau);
  });
});

describe("insetsFor", () => {
  it("reserves nothing on the left, and widens the labels for domains", () => {
    expect(insetsFor(true, "wiki")).toEqual({ left: 0, top: 76, bottom: 10, labelWidth: 104 });
    expect(insetsFor(true, "domain").labelWidth).toBe(138);
  });
  it("leaves room for the controls under a narrow screen", () => {
    expect(insetsFor(false, "wiki")).toEqual({ left: 0, top: 96, bottom: 150, labelWidth: 84 });
  });
});

describe("spikeFrame", () => {
  const sectors = [{ color: "#111" }, { color: "#222" }] as unknown as AtlasSector[];
  const ring = {
    sectors,
    spikes: [
      { id: "a", angle: 0.1, sector: 0 },
      { id: "b", angle: 0.2, sector: 1 },
      { id: "c", angle: 0.3, sector: 1 },
    ],
  } as unknown as Ring;
  const g = { inner: 10, outer: 110 } as RingGeometry;

  it("puts each spike at its angle, its sector's colour, and a tip set by its degree", () => {
    const degree = new Map([["a", 0], ["b", 20]]);
    const f = spikeFrame(ring, g, degree);
    expect([...f.angle]).toEqual([0.1, 0.2, 0.3]);
    expect(f.color).toEqual(["#111", "#222", "#222"]);
    expect(f.tip[0]).toBe(bandRadius(g, bandOf(0)));
    expect(f.tip[1]).toBe(bandRadius(g, bandOf(20)));
    expect(f.tip[2]).toBe(bandRadius(g, 0)); // no degree: the lowest band
    expect(f.tip[1]).toBeGreaterThan(f.tip[0]);
    expect([...f.state]).toEqual([0, 0, 0]);
  });

  it("recolours the same frame in place", () => {
    const f = spikeFrame(ring, g, new Map());
    const again = spikeFrameWithStates(f, { ...ring, sectors: [{ color: "#333" }, { color: "#444" }] } as unknown as Ring);
    expect(again).toBe(f);
    expect(f.color).toEqual(["#333", "#444", "#444"]);
  });
});
