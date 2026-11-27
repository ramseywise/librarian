import { z } from "zod";
import { lessonOutlineSchema } from "./courses";

/** A concept's mastery as /api/learning reports it. `evidence` says whether a direct attempt backs it. */
export const masterySchema = z.object({
  strength: z.number(),
  recency: z.number(),
  lastSeen: z.string(),
  due: z.boolean(),
  evidence: z.enum(["direct", "weak"]),
  counts: z.record(z.string(), z.number()).optional(),
});

/** One module's bar. `strength` is null when none of its concepts has direct evidence ("no data", not 0%). */
export const moduleMasterySchema = z.object({
  strength: z.number().nullable(),
  concepts: z.number(),
  withEvidence: z.number(),
});

/** GET /api/learning/state. `catalogReady` is false while the server builds its catalog. */
export const learningStateSchema = z.object({
  concepts: z.record(z.string(), masterySchema),
  /** Keyed `<course>/<module>`. */
  modules: z.record(z.string(), moduleMasterySchema),
  lessonsDone: z.array(z.string()),
  catalogReady: z.boolean(),
});

const deckRefSchema = z.object({ id: z.string(), title: z.string() });
const pageRefSchema = z.object({ id: z.string(), title: z.string(), summary: z.string(), domain: z.string() });

/** GET /api/learning/next: one concept that is due, with what to open to review it. */
export const dueConceptSchema = z.object({
  concept: pageRefSchema,
  strength: z.number(),
  due: z.boolean(),
  reason: z.string(),
  lessons: z.array(lessonOutlineSchema),
  drills: z.array(lessonOutlineSchema),
  decks: z.array(deckRefSchema),
});
export const dueConceptsSchema = z.array(dueConceptSchema);

/** How a lesson relates to the page: a link in the lesson, a name mention, similar text, or a drill's unit. */
const spokeSchema = lessonOutlineSchema.extend({ course: z.string(), link: z.string().nullable().optional() });

/** GET /api/learning/concept/{id}: a public wiki page and what teaches or drills it. */
export const conceptHubSchema = pageRefSchema.extend({
  mastery: masterySchema.nullable(),
  lessons: z.array(spokeSchema),
  drills: z.array(spokeSchema),
  decks: z.array(deckRefSchema),
  catalogReady: z.boolean(),
});

/** POST /api/learning/events. */
export const learningEventResultSchema = z.object({ logged: z.boolean(), concepts: z.array(z.string()) });

export type Mastery = z.output<typeof masterySchema>;
export type LearningState = z.output<typeof learningStateSchema>;
export type DueConcept = z.output<typeof dueConceptSchema>;
export type ConceptHub = z.output<typeof conceptHubSchema>;
