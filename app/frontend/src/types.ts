export type EdgeType = "wikilink" | "semantic" | "tag-shared";
export type LayoutMode = "dagre" | "umap-semantic";

export interface WikiNodeData extends Record<string, unknown> {
  title: string;
  tags: string[];
  domain: string[];
  typeTag: string;
  summary: string;
  updated: string;
  path: string;
  dimmed: boolean;
  highlighted: boolean;
  /** Page lives in data/wiki/private/ — shown locally, never committed (plan D1). */
  private?: boolean;
}

export interface WikiEdgeData extends Record<string, unknown> {
  edgeType: EdgeType;
  /** Typed See Also relationship (extends, supersedes, …) on wikilink edges. */
  relationship?: string;
  score?: number;
  sharedTags?: string[];
}

export interface EdgeVisibility {
  wikilink: boolean;
  semantic: boolean;
  "tag-shared": boolean;
}

export interface SelectedNode {
  id: string;
  data: WikiNodeData;
}

/**
 * Graph payload — `graph_update` over /ws and GET /api/graph.
 * `edges` holds wikilink edges only; tag-shared edges are derived client-side
 * (utils/tagEdges.ts). `domains` is the server's disk-derived domain list (no `private`).
 */
export interface GraphPayload {
  nodes: import("@xyflow/react").Node<WikiNodeData>[];
  edges: import("@xyflow/react").Edge<WikiEdgeData>[];
  domains: string[];
}
