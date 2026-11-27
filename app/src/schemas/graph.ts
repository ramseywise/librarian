/**
 * Wire shapes of the wiki graph: GET /api/graph, the /ws `graph_update` message, GET
 * /api/graph/atlas, /api/graph/curriculum, /api/glossary and /api/edges/semantic. The server
 * builds them as plain dicts (`librarian.wiki.parser`, `librarian.courses.curriculum`), so these
 * schemas are the contract the client holds it to. Objects ignore keys they do not name.
 */
import { z } from "zod";

export const edgeTypeSchema = z.enum(["wikilink", "semantic", "tag-shared", "module", "term", "course-order"]);

/** A page as the map draws it. `highlighted` and the optional flags are set client-side. */
export const originLinkSchema = z.object({ kind: z.enum(["arxiv", "pdf", "web"]), href: z.string() });
export const pageOriginSchema = z.object({ title: z.string(), links: z.array(originLinkSchema) });
export type PageOrigin = z.output<typeof pageOriginSchema>;

export const wikiNodeDataSchema = z.looseObject({
  title: z.string(),
  tags: z.array(z.string()),
  domain: z.array(z.string()),
  typeTag: z.string(),
  summary: z.string(),
  updated: z.string(),
  path: z.string(),
  dimmed: z.boolean(),
  /** Public links to where the page came from (arXiv, a course PDF, an article URL); raw paths never. */
  origins: z.array(pageOriginSchema).optional(),
  /** How many sources the page cites in all, linkable or not. */
  sourceCount: z.number().optional(),
  highlighted: z.boolean().default(false),
  /** Drawn at 1.5x: chat-cited pages only, which are few. Not part of the layout box. */
  enlarged: z.boolean().optional(),
  /** The selected page: its card is open on the canvas, over its neighbours. */
  expanded: z.boolean().optional(),
  /** Hops from the page a clustered level is about; cards shrink with it. Unset elsewhere. */
  depth: z.number().optional(),
  /** Main course, when a lesson links this page: overrides the directory colour and label. */
  groupColor: z.string().optional(),
  groupLabel: z.string().optional(),
  /** The page's topic within its directory (`_topics.yaml`), and its place in that list; set client-side. */
  topic: z.string().optional(),
  topicIndex: z.number().optional(),
  topicCount: z.number().optional(),
});
export type WikiNodeData = z.output<typeof wikiNodeDataSchema>;

export const wikiEdgeDataSchema = z.looseObject({
  edgeType: edgeTypeSchema,
  /** Typed See Also relationship (extends, supersedes, …) on wikilink edges. */
  relationship: z.string().optional(),
  score: z.number().optional(),
  sharedTags: z.array(z.string()).optional(),
});
export type WikiEdgeData = z.output<typeof wikiEdgeDataSchema>;

const xySchema = z.object({ x: z.number(), y: z.number() });

export const wikiNodeSchema = z.object({
  id: z.string(),
  type: z.string().optional(),
  position: xySchema,
  data: wikiNodeDataSchema,
});

export const wikiEdgeSchema = z.object({
  id: z.string(),
  source: z.string(),
  target: z.string(),
  data: wikiEdgeDataSchema.optional(),
});

/**
 * One sector of the atlas's area grouping: a few wiki directories read as one, at the grain of
 * the courses (an area id is a course id). A directory in no area is drawn as its own sector.
 */
export const areaSchema = z.object({ id: z.string(), title: z.string(), domains: z.array(z.string()) });
export type Area = z.output<typeof areaSchema>;

/**
 * `edges` holds wikilink edges only (anything else is dropped by the reader); `domains` and
 * `areas` are absent from an older server.
 */
export const graphPayloadSchema = z.object({
  nodes: z.array(wikiNodeSchema),
  edges: z.array(wikiEdgeSchema),
  domains: z.array(z.string()).optional(),
  areas: z.array(areaSchema).optional(),
  /** Directory → its topics in order (`_topics.yaml`). Absent from an older server. */
  topics: z.record(z.string(), z.array(z.string())).optional(),
});

/** Every message the socket carries. A message of any other `type` is rejected, not guessed at. */
export const graphSocketMessageSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("graph_update"), data: graphPayloadSchema }),
]);
export type GraphSocketMessage = z.output<typeof graphSocketMessageSchema>;

/** GET /api/graph/atlas: the pages without summaries, wikilinks as index pairs. */
export const atlasPayloadSchema = z.object({
  nodes: z.array(
    z.object({ id: z.string(), title: z.string(), domain: z.string(), typeTag: z.string(), tags: z.array(z.string()) }),
  ),
  links: z.array(z.union([z.tuple([z.number(), z.number()]), z.tuple([z.number(), z.number(), z.string()])])),
  domains: z.array(z.string()),
  /** Absent from an older server: the ring then has a sector per directory. */
  areas: z.array(areaSchema).optional(),
  topics: z.record(z.string(), z.array(z.string())).optional(),
});
export type AtlasPayload = z.output<typeof atlasPayloadSchema>;

/** GET /api/edges/semantic. */
export const semanticEdgesSchema = z.array(wikiEdgeSchema);

/** POST /api/layout/umap: page id → position. */
export const umapPositionsSchema = z.record(z.string(), xySchema);

/**
 * One entry of GET /api/glossary. Only terms with a public mention are served. Terms are filters
 * (`term:<id>` lights the pages mentioning one) and search hits; they are not drawn on the map.
 */
export const glossaryTermSchema = z.object({
  id: z.string(),
  label: z.string(),
  aliases: z.array(z.string()),
  def: z.string(),
  /** The live public page that explains it, if there is one. */
  page: z.string().nullable(),
  mentions: z.number(),
});
export type GlossaryTerm = z.output<typeof glossaryTermSchema>;

export const glossaryTermsSchema = z.object({ terms: z.array(glossaryTermSchema) });
/** Term id → public pages mentioning it (GET /api/glossary/mentions). */
export const glossaryMentionsSchema = z.record(z.string(), z.array(z.string()));

/** A note (lesson) of a module, in reading order, with the wiki pages it links. */
export const curriculumNoteSchema = z.object({
  id: z.string(),
  title: z.string(),
  tier: z.string().optional(),
  pageIds: z.array(z.string()),
});
export const curriculumModuleSchema = z.object({
  id: z.string(),
  title: z.string(),
  firstLesson: z.string().nullable(),
  pageIds: z.array(z.string()),
  /** Absent from an older server. */
  notes: z.array(curriculumNoteSchema).default([]),
});
export const curriculumCourseSchema = z.object({
  id: z.string(),
  title: z.string(),
  pageIds: z.array(z.string()),
  modules: z.array(curriculumModuleSchema),
});

/**
 * GET /api/graph/curriculum: an overlay on the wiki, whose directories stay the canonical
 * domains. Every public page is in a course or in `beyond`.
 */
export const curriculumSchema = z.object({
  courses: z.array(curriculumCourseSchema),
  beyond: z.array(z.object({ domain: z.string(), pageIds: z.array(z.string()) })),
  primaryCourse: z.record(z.string(), z.string()),
  /** Lowest tier among the notes linking a page; untiered pages are absent. */
  pageTier: z.record(z.string(), z.enum(["foundations", "practitioner", "specialist"])).optional(),
  /** Served from an older snapshot while a rebuild runs. */
  stale: z.boolean(),
});
export type Curriculum = z.output<typeof curriculumSchema>;
export type CurriculumCourse = z.output<typeof curriculumCourseSchema>;
export type CurriculumModule = z.output<typeof curriculumModuleSchema>;
export type CurriculumNote = z.output<typeof curriculumNoteSchema>;
