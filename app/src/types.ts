export type EdgeType = "wikilink" | "semantic" | "tag-shared" | "module";
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
  /** Drawn at 1.5x: chat-cited pages only, which are few. Not part of the layout box. */
  enlarged?: boolean;
  /** Main course, when a lesson links this page: overrides the directory colour and label. */
  groupColor?: string;
  groupLabel?: string;
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
  /** Pages taught in the same curriculum module. */
  module: boolean;
}

/**
 * One entry of GET /api/glossary. Only terms with a public mention are served. Terms are filters
 * (`term:<id>` lights the pages mentioning one) and search hits; they are not drawn on the map.
 */
export interface GlossaryTerm {
  id: string;
  label: string;
  aliases: string[];
  def: string;
  /** The live public page that explains it, if there is one. */
  page: string | null;
  mentions: number;
}

export interface Glossary {
  terms: GlossaryTerm[];
  /** Term id → public pages mentioning it (GET /api/glossary/mentions). */
  mentions: Record<string, string[]>;
}

export interface CurriculumModule {
  id: string;
  title: string;
  firstLesson: string | null;
  pageIds: string[];
}

export interface CurriculumCourse {
  id: string;
  title: string;
  pageIds: string[];
  modules: CurriculumModule[];
}

/**
 * GET /api/graph/curriculum: an overlay on the wiki, whose directories stay the canonical
 * domains. Every public page is in a course or in `beyond`.
 */
export interface Curriculum {
  courses: CurriculumCourse[];
  beyond: { domain: string; pageIds: string[] }[];
  primaryCourse: Record<string, string>;
  /** Served from an older snapshot while a rebuild runs. */
  stale: boolean;
}

/**
 * One sector of the atlas's area grouping: a few wiki directories read as one, at the grain of
 * the courses (an area id is a course id). Served with the graph payload from
 * `librarian.wiki.areas`; a directory in no area is drawn as its own sector.
 */
export interface Area {
  id: string;
  title: string;
  domains: string[];
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
  nodes: import("@xyflow/react").Node<WikiNodeData>[];
  edges: import("@xyflow/react").Edge<WikiEdgeData>[];
  domains: string[];
  areas: Area[];
}
