import type { SlideBeat, SlideFrameData } from "./types";

/** What each beat is called on the slide, and the class that gives it its hue (slides.css). */
export const BEATS: Record<SlideBeat, { label: string; cls: string }> = {
  problem: { label: "The idea", cls: "sf-b-idea" },
  fundamentals: { label: "The principle", cls: "sf-b-principle" },
  practice: { label: "The application", cls: "sf-b-applied" },
  pitfalls: { label: "Pitfall", cls: "sf-b-pitfall" },
  wrap: { label: "Keep", cls: "sf-b-keep" },
};
/** The class that carries a frame's hue: its beat's, yellow for a part divider, neutral otherwise. */
export function beatClass(frame: SlideFrameData): string {
  if (frame.kind === "divider") return BEATS.problem.cls;
  return frame.kind === "slide" && frame.beat ? BEATS[frame.beat].cls : "sf-b-none";
}
