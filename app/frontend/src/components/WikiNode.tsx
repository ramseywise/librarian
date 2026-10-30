import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { Node } from "@xyflow/react";
import type { WikiNodeData } from "../types";
import { domainColor } from "../theme/domains";

const TYPE_BORDER: Record<string, string> = {
  concept: "solid",
  pattern: "dashed",
  decision: "double",
  project: "solid",
  comparison: "dotted",
  reference: "dotted",
};

export type WikiFlowNode = Node<WikiNodeData>;

export function WikiNode({ data, selected }: NodeProps<WikiFlowNode>) {
  const color = domainColor(data.domain[0]);
  const borderStyle = TYPE_BORDER[data.typeTag] ?? "solid";

  return (
    <div
      className="wiki-node"
      style={{
        border: `2px ${borderStyle} ${color}`,
        boxShadow: data.highlighted
          ? `0 0 0 2px ${color}, 0 0 24px ${color}cc`
          : selected
          ? `0 0 14px ${color}88`
          : "none",
        opacity: data.dimmed && !selected ? 0.12 : 1,
        transform: data.highlighted ? "scale(1.5)" : "scale(1)",
        zIndex: data.highlighted ? 10 : undefined,
      }}
      title={data.summary}
    >
      <Handle type="target" position={Position.Top} style={{ background: color }} />
      <div className="wiki-node-domain" style={{ color }}>
        {data.domain[0] ?? data.typeTag}
        {data.private && <span className="private-badge private-badge--node" title="Local-only page (data/wiki/private/)">private</span>}
      </div>
      <div className="wiki-node-title">
        {data.title}
      </div>
      {data.summary && (
        <div className="wiki-node-summary">
          {data.summary.slice(0, 80)}{data.summary.length > 80 ? "…" : ""}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: color }} />
    </div>
  );
}
