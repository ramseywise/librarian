/**
 * Wire shapes of /api/courses/*. The routes return plain dicts built in `librarian.courses`
 * (queries, slides, study, progress); these schemas state what the client relies on, and the
 * TypeScript types are inferred from them. Objects ignore keys they do not name. Fields the
 * server omits when empty are optional, and the server's `null`s are explicit.
 */
import { z } from "zod";

/** Drill schema fields (learn-ai-engineering programming/drills/README.md), on lessons of kind "drill". */
export const drillMetaSchema = z.object({
  track: z.string(),
  topic: z.string().optional(),
  /** Usually "easy", "medium" or "hard"; any string is shown as written. */
  difficulty: z.string().optional(),
  timebox_min: z.number().optional(),
  /** Declared concepts with no wiki page yet: plain labels, not graph links. */
  tags: z.array(z.string()).optional(),
});

export const lessonOutlineSchema = z.object({
  id: z.string(),
  title: z.string(),
  section: z.string(),
  /** "reading", "notebook", "drill", or another kind. */
  kind: z.string(),
  summary: z.string(),
  drill: drillMetaSchema.optional(),
  /** Absent when the lesson has no flashcards. */
  flashcardCount: z.number().optional(),
  /** Multiple-choice questions; absent when the lesson has none. */
  quizCount: z.number().optional(),
  /** Worked problems; absent when the lesson has none. */
  problemCount: z.number().optional(),
  /** Present (true) only for a lesson under data/courses/private/: local, never published. */
  private: z.boolean().optional(),
});

export const sourceRefSchema = z.object({ title: z.string(), source: z.string(), url: z.string().optional() });

/** A lecture deck as the catalog lists it; `subtitle` tells apart decks that share a title. */
export const deckSchema = z.object({
  id: z.string(),
  title: z.string(),
  subtitle: z.string().optional(),
  /** The lecture that introduces a lecture series. */
  overview: z.boolean().optional(),
});

/** A wiki page as the topic page lists it. */
export const wikiPageRefSchema = z.object({ id: z.string(), title: z.string(), summary: z.string() });

export const courseModuleSchema = z.object({
  id: z.string(),
  title: z.string(),
  summary: z.string(),
  order: z.number(),
  /** "core" or "advanced", when the course README sorts its modules that way. */
  group: z.string().optional(),
  /** What you can do after the module, from the course README. Absent when it lists none. */
  objectives: z.array(z.string()).optional(),
  readings: z.array(sourceRefSchema),
  /** How many readings the module lists; the list itself is only present with the local private overlay. */
  readingsCount: z.number().optional(),
  references: z.array(sourceRefSchema),
  lessons: z.array(lessonOutlineSchema),
  /** Lecture decks (`#/slides/<id>`): the module's own deck first, then its lectures. */
  decks: z.array(deckSchema).optional(),
  flashcardCount: z.number().optional(),
  quizCount: z.number().optional(),
  problemCount: z.number().optional(),
  /** Public wiki pages the module's lessons cite, most-cited first, at most 12 (`wikiCount` is how many in all). */
  wiki: z.array(wikiPageRefSchema).optional(),
  wikiCount: z.number().optional(),
  /** True when only private lessons make up the module. */
  private: z.boolean().optional(),
});

export const courseSchema = z.object({
  id: z.string(),
  title: z.string(),
  summary: z.string(),
  order: z.number(),
  lessonCount: z.number(),
  modules: z.array(courseModuleSchema),
  /** The course's own pages (its guide and references), shown on the course page and not as a module. */
  guide: z.array(lessonOutlineSchema).optional(),
  /** What you can do by the end of the course. Absent when its README lists none. */
  outcomes: z.array(z.string()).optional(),
  /** The course's shared reading list; only the count without the local private overlay. */
  readings: z.array(sourceRefSchema).optional(),
  readingsCount: z.number().optional(),
  references: z.array(sourceRefSchema).optional(),
  /** True when only private modules make up the course. */
  private: z.boolean().optional(),
});

/** GET /api/courses. */
export const coursesSchema = z.array(courseSchema);

export const conceptRefSchema = z.object({ id: z.string(), title: z.string(), summary: z.string(), domain: z.string() });

/** A runnable practice example from a pillar's practice/manifest.yaml. `id` is its path under data/courses. */
export const labOutlineSchema = z.object({
  id: z.string(),
  title: z.string(),
  course: z.string(),
  module: z.string(),
  /** Relative to the module, starting with practice/. */
  path: z.string(),
  purpose: z.string(),
  pattern: z.string(),
  /** "python", "typescript", "jupyter", or another. */
  language: z.string(),
  runsOffline: z.boolean(),
  /** It has an entry script (`run`) / a `verified_by` this app can run (`check`). */
  hasRun: z.boolean(),
  hasCheck: z.boolean(),
});

export const labRowSchema = labOutlineSchema.extend({ notes: z.array(lessonOutlineSchema) });

/** GET /api/courses/labs. `canRun`: this server runs labs (a dev machine); false in a deployment. */
export const labsListSchema = z.object({ labs: z.array(labRowSchema), canRun: z.boolean() });

export const labFileSchema = z.object({
  /** Relative to the practice folder. */
  path: z.string(),
  text: z.string(),
});

/** GET /api/courses/labs/{id}. */
export const labDetailSchema = labOutlineSchema.extend({
  licence: z.string(),
  verifiedBy: z.string(),
  run: z.string().nullable(),
  check: z.string().nullable(),
  files: z.array(labFileSchema),
  notes: z.array(lessonOutlineSchema),
  canRun: z.boolean(),
});

/** GET /api/courses/lessons/{id}. */
export const lessonSchema = lessonOutlineSchema.extend({
  course: z.string(),
  module: z.string(),
  source: z.string(),
  body: z.string(),
  concepts: z.array(conceptRefSchema),
  /** Sibling `sources/` links the API can serve, keyed by href as written. Empty in a deployment. */
  sourceLinks: z.record(z.string(), z.string()).optional(),
  prev: lessonOutlineSchema.nullable(),
  next: lessonOutlineSchema.nullable(),
  /** Labs whose manifest entry backs this lesson, or whose file it names. */
  labs: z.array(labOutlineSchema).optional(),
});

/** GET /api/courses/concept/{page}: the lessons that cite a wiki page. */
export const conceptLessonsSchema = z.array(lessonOutlineSchema.extend({ course: z.string() }));

export const practiceDrillSchema = lessonOutlineSchema.extend({
  course: z.string(),
  drill: drillMetaSchema,
  concepts: z.array(conceptRefSchema),
  /** From the caller's drill attempts (app runs and an imported drill log); absent if none. */
  attempts: z.object({ count: z.number(), last: z.string(), score: z.string() }).optional(),
});
/** GET /api/courses/practice. */
export const practiceDrillsSchema = z.array(practiceDrillSchema);

const studyStatusSchema = z.enum(["new", "due", "later"]);

export const flashcardSchema = z.object({
  id: z.string(),
  /** `**bold**` and `code` inline markup, from the slide deck. */
  front: z.string(),
  back: z.string(),
  lesson: z.string().nullable(),
  lessonTitle: z.string().nullable(),
  /** The explanation behind `back`, shown on request. Same inline markup. */
  more: z.string().optional(),
  /** The card's own depth, and its lesson's tier (depth-rubric.md). Absent until tagged. */
  depth: z.enum(["intro", "core", "deep"]).optional(),
  tier: z.enum(["foundations", "practitioner", "specialist"]).optional(),
  /** What the answers rest on: a citation, or a `[text](https://...)` link. */
  sources: z.array(z.string()).optional(),
  /** Leitner box 1-5; null until first graded. Absent only on an API older than scheduling. */
  box: z.number().nullable().optional(),
  dueOn: z.string().nullable().optional(),
  status: studyStatusSchema.optional(),
});

/** GET /api/courses/flashcards/{id}. */
export const flashcardDeckSchema = z.object({
  /** Module (`<course>/<module>`) or lesson id. */
  id: z.string(),
  title: z.string(),
  course: z.string(),
  cards: z.array(flashcardSchema),
  /** Reviewed cards due today or overdue. */
  dueCount: z.number().optional(),
  /** Cards never graded. */
  newCount: z.number().optional(),
});

/** GET /api/courses/flashcards-due. */
export const flashcardsDueSummarySchema = z.object({
  today: z.string(),
  due: z.number(),
  new: z.number(),
  modules: z.array(z.object({ deck: z.string(), title: z.string(), due: z.number(), new: z.number() })),
});

export const slideEntrySchema = z.object({
  /** 1-based. */
  n: z.number(),
  title: z.string(),
  /** Plain text of the slide, always present. */
  text: z.string(),
  notes: z.string(),
  /** Image URL, or null when the slide has no rendering. */
  image: z.string().nullable(),
});

export const slideBeatSchema = z.enum(["problem", "fundamentals", "practice", "pitfalls", "wrap"]);

/** Where a slide sits: its part's number (null in a closing part), title, and how many numbered parts there are. */
export const slidePartSchema = z.object({ n: z.number().nullable(), title: z.string(), of: z.number() });

/** A deck's slide as data, drawn by `SlideFrame`. `body` holds the layout's own yaml keys, as written. */
export const slideFrameSchema = z.discriminatedUnion("kind", [
  z.object({
    n: z.number(),
    kind: z.literal("title"),
    title: z.string(),
    subtitle: z.string(),
    tagline: z.string(),
    byline: z.string(),
    reference: z.string(),
    agenda: z.array(z.object({ n: z.number(), title: z.string(), summary: z.string() })),
    notes: z.string(),
    narration: z.string(),
  }),
  z.object({
    n: z.number(),
    kind: z.literal("divider"),
    title: z.string(),
    summary: z.string(),
    part: slidePartSchema,
    notes: z.string(),
    narration: z.string(),
  }),
  z.object({
    n: z.number(),
    kind: z.literal("slide"),
    layout: z.string(),
    beat: slideBeatSchema.nullable(),
    level: z.string(),
    title: z.string(),
    kicker: z.string(),
    lead: z.string(),
    takeaway: z.string(),
    source: z.string(),
    part: slidePartSchema,
    body: z.record(z.string(), z.unknown()),
    notes: z.string(),
    narration: z.string(),
  }),
]);

/** GET /api/courses/slides/{id}. */
export const slideDeckSchema = z.object({
  id: z.string(),
  title: z.string(),
  course: z.string(),
  module: z.string(),
  /**
   * ready: images built; building: text shown while a build runs; text: this machine cannot
   * render images; failed: the last build failed (see `error`).
   */
  status: z.enum(["ready", "building", "text", "failed"]),
  /** A build is due and none is running: POST .../build starts it. */
  stale: z.boolean().optional(),
  images: z.boolean(),
  /** What rendering needs and the machine lacks. */
  needs: z.array(z.string()),
  error: z.string(),
  decks: z.array(z.object({ id: z.string(), title: z.string() })),
  slides: z.array(slideEntrySchema),
  /** The deck as data, read from the yaml: what the viewer draws. Absent or empty: fall back to `slides`. */
  frames: z.array(slideFrameSchema).optional(),
});

export const quizQuestionSchema = z.object({
  id: z.string(),
  prompt: z.string(),
  /** The answer is never sent; the server grades. Empty for a worked problem. */
  options: z.array(z.string()),
  /** `worked`: no options, the learner types a number. Absent means `choice`. */
  kind: z.enum(["choice", "worked"]).optional(),
  /** A worked problem with a hint to ask for; the hint itself is not sent ahead. */
  hasHint: z.boolean().optional(),
  lesson: z.string().nullable(),
  lessonTitle: z.string().nullable(),
  box: z.number().nullable().optional(),
  dueOn: z.string().nullable().optional(),
  status: studyStatusSchema.optional(),
});

/** GET /api/courses/quiz/{id}. */
export const quizSchema = z.object({
  id: z.string(),
  title: z.string(),
  course: z.string(),
  questions: z.array(quizQuestionSchema),
  dueCount: z.number().optional(),
  newCount: z.number().optional(),
});

/** POST /api/courses/quiz-results. */
export const quizAnswerResultSchema = z.object({
  correct: z.boolean(),
  answer: z.string(),
  explanation: z.string(),
  logged: z.boolean(),
});

/** POST /api/courses/quiz-reveal. */
export const quizRevealSchema = z.object({
  hint: z.string().optional(),
  answer: z.string().optional(),
  explanation: z.string().optional(),
  logged: z.boolean(),
});

const studyCountsSchema = z.object({ due: z.number(), new: z.number() });

/** GET /api/courses/study. */
export const studyHomeSchema = z.object({
  today: z.string(),
  due: z.number(),
  new: z.number(),
  modules: z.array(
    z.object({ module: z.string(), title: z.string(), cards: studyCountsSchema, questions: studyCountsSchema }),
  ),
  nextDrill: lessonOutlineSchema
    .extend({ course: z.string(), track: z.string().nullable(), reason: z.string() })
    .nullable(),
  lecture: z
    .object({ module: z.string(), title: z.string(), decks: z.array(z.object({ id: z.string(), title: z.string() })) })
    .nullable(),
});

const levelProgressSchema = z.object({ total: z.number(), right: z.number(), redo: z.number() });
/** GET /api/courses/study-progress: the caller's progress per module id (`<course>/<module>`) and level. */
export const studyProgressSchema = z.record(
  z.string(),
  z.object({ choice: levelProgressSchema.optional(), cards: levelProgressSchema.optional(), worked: levelProgressSchema.optional() }),
);

/** GET /api/courses/progress: only `lessons` is read; the totals are the server's own summary. */
export const serverProgressSchema = z.object({
  lessons: z.record(z.string(), z.object({ state: z.enum(["opened", "done"]), updatedAt: z.string() })),
});

/** GET /api/courses/search. */
export const searchHitSchema = lessonOutlineSchema.extend({ course: z.string(), snippet: z.string() });
export const searchHitsSchema = z.array(searchHitSchema);
