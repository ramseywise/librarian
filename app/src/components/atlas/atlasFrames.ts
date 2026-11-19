import type { Grouping } from "../../utils/mapRoute";
import { bandOf, bandRadius, type Ring, type RingGeometry, type RingInsets } from "../../utils/atlas";
import { resolveColor, type SpikeFrame } from "./atlasCanvas";

export function insetsFor(wide: boolean, grouping: Grouping): RingInsets {
  return wide
    ? // The sidebar is its own column now, not a panel over the canvas: nothing to reserve on the left.
      { left: 0, top: 76, bottom: 10, labelWidth: grouping === "domain" ? 138 : 104 }
    : { left: 0, top: 96, bottom: 150, labelWidth: 84 };
}

/** Shortest way round from one angle to another. */
export function towards(from: number, to: number, t: number): number {
  let d = (to - from) % (Math.PI * 2);
  if (d > Math.PI) d -= Math.PI * 2;
  if (d < -Math.PI) d += Math.PI * 2;
  return from + d * t;
}

export function spikeFrame(ring: Ring, g: RingGeometry, degree: Map<string, number>): SpikeFrame {
  const n = ring.spikes.length;
  const frame: SpikeFrame = {
    angle: new Float64Array(n),
    tip: new Float64Array(n),
    color: new Array<string>(n),
    state: new Uint8Array(n),
  };
  const colors = ring.sectors.map((s) => resolveColor(s.color));
  ring.spikes.forEach((s, i) => {
    frame.angle[i] = s.angle;
    frame.tip[i] = bandRadius(g, bandOf(degree.get(s.id) ?? 0));
    frame.color[i] = colors[s.sector];
  });
  return frame;
}

/** Same spikes with colours resolved again: a sector on a CSS variable follows the theme. */
export function spikeFrameWithStates(frame: SpikeFrame, ring: Ring): SpikeFrame {
  const colors = ring.sectors.map((s) => resolveColor(s.color));
  ring.spikes.forEach((s, i) => {
    frame.color[i] = colors[s.sector];
  });
  return frame;
}
