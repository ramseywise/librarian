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
}

export interface WikiEdgeData extends Record<string, unknown> {
  edgeType: EdgeType;
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
