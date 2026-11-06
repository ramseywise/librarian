import { Handle, Position, useStore, type NodeProps } from "@xyflow/react";
import { MAX_TERM_SCALE } from "../utils/glossary";
import type { WikiFlowNode } from "./WikiNode";

/** On-screen font size to hold when the view is zoomed out, as map labels do. */
const LEGIBLE_PX = 11;
const BASE_PX = 20;
/** Steps rather than every zoom value, so a wheel gesture re-renders the pills rarely. */
const roundedZoom = (s: { transform: [number, number, number] }) => Math.round(s.transform[2] * 20) / 20;

/** A glossary term on the canvas: a pill, so it never reads as a page card. */
export function TermNode({ data }: NodeProps<WikiFlowNode>) {
  const zoom = useStore(roundedZoom);
  const scale = Math.min(MAX_TERM_SCALE, Math.max(1, LEGIBLE_PX / (BASE_PX * Math.max(zoom, 0.05))));
  return (
    <div
      className={`term-node${data.highlighted ? " is-focused" : ""}${data.dimmed ? " is-dimmed" : ""}`}
      title={data.summary}
      style={{ transform: `scale(${scale})` }}
    >
      <Handle type="target" position={Position.Top} className="term-node-handle" />
      <span className="term-node-label">{data.title}</span>
      <Handle type="source" position={Position.Bottom} className="term-node-handle" />
    </div>
  );
}
