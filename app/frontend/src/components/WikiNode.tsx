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
      style={{
        background: "#1a1a1a",
        border: `2px ${borderStyle} ${color}`,
        borderRadius: 8,
        padding: "8px 12px",
        minWidth: 160,
        maxWidth: 200,
        boxShadow: data.highlighted
          ? `0 0 0 2px ${color}, 0 0 24px ${color}cc`
          : selected
          ? `0 0 14px ${color}88`
          : "none",
        opacity: data.dimmed && !selected ? 0.12 : 1,
        transform: data.highlighted ? "scale(1.5)" : "scale(1)",
        transformOrigin: "center",
        transition: "opacity 0.25s, box-shadow 0.2s, transform 0.2s",
        cursor: "pointer",
        position: "relative",
        zIndex: data.highlighted ? 10 : undefined,
      }}
      title={data.summary}
    >
      <Handle type="target" position={Position.Top} style={{ background: color }} />
      <div style={{ fontSize: 10, color, fontWeight: 700, marginBottom: 3, textTransform: "uppercase", letterSpacing: "0.05em" }}>
        {data.domain[0] ?? data.typeTag}
        {data.private && <span style={privateBadgeStyle} title="Local-only page (data/wiki/private/)">private</span>}
      </div>
      <div style={{ fontSize: 13, color: "#e8e8e8", lineHeight: 1.35, fontWeight: 500 }}>
        {data.title}
      </div>
      {data.summary && (
        <div style={{ fontSize: 10, color: "#888", marginTop: 4, lineHeight: 1.3 }}>
          {data.summary.slice(0, 80)}{data.summary.length > 80 ? "…" : ""}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: color }} />
    </div>
  );
}

const privateBadgeStyle: React.CSSProperties = {
  marginLeft: 6,
  padding: "0 4px",
  border: "1px solid #9E9E9E",
  borderRadius: 3,
  color: "#bbb",
  fontSize: 9,
  fontWeight: 600,
  letterSpacing: "0.04em",
};
