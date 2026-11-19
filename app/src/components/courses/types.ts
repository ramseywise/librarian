/**
 * Course API types. They are inferred from the schemas in schemas/courses.ts, which is where
 * each payload's shape (and the route it comes from) is stated.
 */
import type { z } from "zod";
import type * as s from "../../schemas/courses";

export type DrillMeta = z.output<typeof s.drillMetaSchema>;
export type LessonOutline = z.output<typeof s.lessonOutlineSchema>;
export type SourceRef = z.output<typeof s.sourceRefSchema>;
export type Deck = z.output<typeof s.deckSchema>;
export type CourseModule = z.output<typeof s.courseModuleSchema>;
export type WikiPageRef = z.output<typeof s.wikiPageRefSchema>;
export type StudyProgress = z.output<typeof s.studyProgressSchema>;
export type LevelProgress = NonNullable<StudyProgress[string][keyof StudyProgress[string]]>;
export type Course = z.output<typeof s.courseSchema>;
export type ConceptRef = z.output<typeof s.conceptRefSchema>;
export type Lesson = z.output<typeof s.lessonSchema>;
export type LabOutline = z.output<typeof s.labOutlineSchema>;
export type LabRow = z.output<typeof s.labRowSchema>;
export type LabsList = z.output<typeof s.labsListSchema>;
export type LabFile = z.output<typeof s.labFileSchema>;
export type LabDetail = z.output<typeof s.labDetailSchema>;
export type PracticeDrill = z.output<typeof s.practiceDrillSchema>;
export type SearchHit = z.output<typeof s.searchHitSchema>;
export type Flashcard = z.output<typeof s.flashcardSchema>;
export type FlashcardDeck = z.output<typeof s.flashcardDeckSchema>;
export type FlashcardsDueSummary = z.output<typeof s.flashcardsDueSummarySchema>;
export type SlideEntry = z.output<typeof s.slideEntrySchema>;
export type SlideBeat = z.output<typeof s.slideBeatSchema>;
export type SlidePart = z.output<typeof s.slidePartSchema>;
export type SlideFrameData = z.output<typeof s.slideFrameSchema>;
export type SlideDeck = z.output<typeof s.slideDeckSchema>;
export type QuizQuestion = z.output<typeof s.quizQuestionSchema>;
export type Quiz = z.output<typeof s.quizSchema>;
export type QuizAnswerResult = z.output<typeof s.quizAnswerResultSchema>;
export type StudyHomeData = z.output<typeof s.studyHomeSchema>;
