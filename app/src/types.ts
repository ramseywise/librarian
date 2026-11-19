import type { Edge, Node } from "@xyflow/react";
import type { z } from "zod";
import type { Area, GlossaryTerm, WikiEdgeData, WikiNodeData, edgeTypeSchema } from "./schemas/graph";

// The wire shapes live in schemas/graph.ts; these are their inferred types, re-exported so the
// components keep one import site.
export type { Area, Curriculum, CurriculumCourse, CurriculumModule, GlossaryTerm, WikiEdgeData, WikiNodeData } from "./schemas/graph";

export type EdgeType = z.output<typeof edgeTypeSchema>;
export type LayoutMode = "dagre" | "umap-semantic";

export interface EdgeVisibility {
  wikilink: boolean;
  semantic: boolean;
  "tag-shared": boolean;
  /** Pages taught in the same curriculum module. */
  module: boolean;
  /** Pages mentioning the same (not too common) glossary term. */
  term: boolean;
  /** Pages in the order a module's notes teach them. */
  "course-order": boolean;
}

export interface Glossary {
  terms: GlossaryTerm[];
  /** Term id → public pages mentioning it (GET /api/glossary/mentions). */
  mentions: Record<string, string[]>;
}

/** Filter id (`course:<id>`, `module:<course>/<module>`, `beyond:<dir>`, `area:<id>`, `gap:<id>`, `dir:<dir>`, `tag:<tag>`, `term:<id>`) → its pages. */
export type Facets = Map<string, Set<string>>;

export interface SelectedNode {
  id: string;
  data: WikiNodeData;
}

/**
 * Graph payload — `graph_update` over /ws and GET /api/graph.
 * `edges` holds wikilink edges only; tag-shared edges are derived client-side
 * (utils/tagEdges.ts). `domains` is the server's disk-derived domain list (no `private`);
 * `areas` folds those directories into the ring's sectors (empty from an older server).
 */
export interface GraphPayload {
  nodes: Node<WikiNodeData>[];
  edges: Edge<WikiEdgeData>[];
  domains: string[];
  areas: Area[];
}
