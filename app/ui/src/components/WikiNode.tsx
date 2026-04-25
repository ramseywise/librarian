import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { Node } from "@xyflow/react";
import type { WikiNodeData } from "../types";

const DOMAIN_COLORS: Record<string, string> = {
  langgraph: "#4CAF50",
  rag: "#2196F3",
  adk: "#FF9800",
  mcp: "#9C27B0",
  memory: "#00BCD4",
  voice: "#F44336",
  eval: "#FFEB3B",
  infra: "#607D8B",
  llm: "#E91E63",
  "deep-agents": "#3F51B5",
  "context-management": "#009688",
};

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
  const primaryDomain = data.domain[0] ?? "infra";
  const color = DOMAIN_COLORS[primaryDomain] ?? "#607D8B";
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
        boxShadow: selected ? `0 0 14px ${color}88` : "none",
        opacity: data.dimmed ? 0.15 : 1,
        transition: "opacity 0.25s, box-shadow 0.2s",
        cursor: "pointer",
      }}
      title={data.summary}
    >
      <Handle type="target" position={Position.Top} style={{ background: color }} />
      <div style={{ fontSize: 10, color, fontWeight: 700, marginBottom: 3, textTransform: "uppercase", letterSpacing: "0.05em" }}>
        {data.domain[0] ?? data.typeTag}
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
