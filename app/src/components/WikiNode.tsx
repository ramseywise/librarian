import { useContext } from "react";
import "./card.css";
import { Handle, Position, useStore, type NodeProps } from "@xyflow/react";
import type { Node } from "@xyflow/react";
import type { WikiNodeData } from "../types";
import { useTheme } from "../hooks/useTheme";
import { topicColor } from "../theme/domains";
import { NodeDetailPanel } from "./NodeDetailPanel";
import { NodeCardContext, type NodeCard } from "./nodeCard";

const TYPE_BORDER: Record<string, string> = {
  concept: "solid",
  pattern: "dashed",
  decision: "double",
  project: "solid",
  comparison: "dotted",
  reference: "dotted",
};

/** Zoomed out past this an open card is scaled back up, so it stays readable. */
const OPEN_MIN_ZOOM = 0.8;

export type WikiFlowNode = Node<WikiNodeData>;

export function WikiNode({ id, data, selected }: NodeProps<WikiFlowNode>) {
  const theme = useTheme();
  const card = useContext(NodeCardContext);
  const color = data.groupColor ?? topicColor(data.domain[0], data.topicIndex, data.topicCount, theme);
  const borderStyle = TYPE_BORDER[data.typeTag] ?? "solid";
  const open = !!data.expanded && card != null;
  const size = data.depth === undefined ? "" : ` wiki-node--d${Math.min(data.depth, 3)}`;

  return (
    <div
      className={`wiki-node${size}${open ? " wiki-node--open" : ""}`}
      style={{
        border: `2px ${borderStyle} ${color}`,
        boxShadow: data.highlighted
          ? `0 0 0 2px ${color}, 0 0 24px ${color}cc`
          : selected
          ? `0 0 14px ${color}88`
          : "none",
        opacity: data.dimmed && !selected && !open ? 0.12 : 1,
        // An open card is already the largest thing here, and a scale would blur its text.
        transform: data.enlarged && !open ? "scale(1.5)" : "scale(1)",
        zIndex: data.highlighted ? 10 : undefined,
      }}
      title={open ? undefined : data.summary}
    >
      {/* Top and bottom come first: an edge that names no handle takes the first of its kind. */}
      <Handle type="target" position={Position.Top} style={{ background: color }} />
      <Handle type="source" position={Position.Bottom} style={{ background: color }} />
      {/* Side handles, for the cluster layout's sideways edges. */}
      <Handle id="tl" type="target" position={Position.Left} className="wiki-node-side" />
      <Handle id="tr" type="target" position={Position.Right} className="wiki-node-side" />
      <Handle id="sl" type="source" position={Position.Left} className="wiki-node-side" />
      <Handle id="sr" type="source" position={Position.Right} className="wiki-node-side" />
      <div className="wiki-node-domain" style={{ color }}>
        {data.groupLabel ?? data.domain[0] ?? data.typeTag}
      </div>
      <div className="wiki-node-title">
        {data.title}
      </div>
      {data.summary && (
        <div className="wiki-node-summary">
          {data.summary.slice(0, 80)}{data.summary.length > 80 ? "…" : ""}
        </div>
      )}
      {open && <OpenCard id={id} data={data} card={card} />}
    </div>
  );
}

/**
 * The node grown into its full card, centred on where the node sits. It lies over the neighbours
 * rather than pushing them, so opening one never moves the map.
 */
function OpenCard({ id, data, card }: { id: string; data: WikiNodeData; card: NodeCard }) {
  const zoom = useStore((s) => s.transform[2]);
  const scale = Math.max(1, OPEN_MIN_ZOOM / zoom);
  return (
    // The wrapper only stops propagation; the controls inside are the interactive elements.
    // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
    <div
      // React Flow leaves drags, wheel and pans that start in here alone.
      className="wiki-node-open nodrag nowheel nopan"
      style={{ transform: `translate(-50%, -50%) scale(${scale})` }}
      // A click inside the card is not a click on the node: it must not toggle the focus.
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
    >
      <NodeDetailPanel
        nodeId={id}
        data={data}
        highlighted={card.cited.has(id)}
        lastQuery={card.lastQuery}
        onClose={card.onClose}
        onTagClick={card.onTagClick}
        activeTags={card.activeTags}
        onOpenLesson={card.onOpenLesson}
        related={card.related(id)}
        why={card.why?.(id)}
        onOpenPage={card.onOpenPage}
      />
    </div>
  );
}
