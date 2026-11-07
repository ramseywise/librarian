/** Drill schema fields (learn-ai-engineering programming/drills/README.md), on lessons of kind "drill". */
export interface DrillMeta {
  track: string;
  topic?: string;
  difficulty?: "easy" | "medium" | "hard" | string;
  timebox_min?: number;
  /** Declared concepts with no wiki page yet — plain labels, not graph links. */
  tags?: string[];
}

export interface LessonOutline {
  id: string;
  title: string;
  section: string;
  kind: "reading" | "notebook" | "drill" | string;
  summary: string;
  drill?: DrillMeta;
  /** Absent when the lesson has no flashcards. */
  flashcardCount?: number;
  /** Present (true) only for a lesson under data/courses/private/: local, never published. */
  private?: boolean;
}

export interface SourceRef {
  title: string;
  source: string;
  url?: string;
}

export interface CourseModule {
  id: string;
  title: string;
  summary: string;
  order: number;
  readings: SourceRef[];
  /** How many readings the module lists; the list itself is only present with the local private overlay. */
  readingsCount?: number;
  references: SourceRef[];
  lessons: LessonOutline[];
  /** Absent when the module has no flashcards. */
  flashcardCount?: number;
  /** Absent when the module has no quiz. */
  quizCount?: number;
  /** True when only private lessons make up the module. */
  private?: boolean;
}

export interface Course {
  id: string;
  title: string;
  summary: string;
  order: number;
  lessonCount: number;
  modules: CourseModule[];
  /** True when only private modules make up the course. */
  private?: boolean;
}

export interface ConceptRef {
  id: string;
  title: string;
  summary: string;
  domain: string;
}

export interface Lesson extends LessonOutline {
  course: string;
  module: string;
  source: string;
  body: string;
  concepts: ConceptRef[];
  /** Sibling `sources/` links the API can serve, keyed by href as written. Empty in a deployment. */
  sourceLinks?: Record<string, string>;
  prev: LessonOutline | null;
  next: LessonOutline | null;
}

export interface PracticeDrill extends LessonOutline {
  course: string;
  drill: DrillMeta;
  concepts: ConceptRef[];
  /** From sisyphus drills/coding/drill-log.md, read live; absent if never logged. */
  attempts?: { count: number; last: string; score: string };
}

export interface SearchHit extends LessonOutline {
  course: string;
  snippet: string;
}

export interface Flashcard {
  id: string;
  /** `**bold**` and `code` inline markup, from the slide deck. */
  front: string;
  back: string;
  lesson: string | null;
  lessonTitle: string | null;
  /** Leitner box 1-5; null until first graded. Absent only on an API older than scheduling. */
  box?: number | null;
  dueOn?: string | null;
  status?: "new" | "due" | "later";
}

export interface FlashcardDeck {
  /** Module (`<course>/<module>`) or lesson id. */
  id: string;
  title: string;
  course: string;
  cards: Flashcard[];
  /** Reviewed cards due today or overdue. */
  dueCount?: number;
  /** Cards never graded. */
  newCount?: number;
}

export interface FlashcardsDueSummary {
  today: string;
  due: number;
  new: number;
  modules: { deck: string; title: string; due: number; new: number }[];
}

export interface SlideEntry {
  /** 1-based. */
  n: number;
  title: string;
  /** Plain text of the slide, always present. */
  text: string;
  notes: string;
  /** Image URL, or null when the slide has no rendering. */
  image: string | null;
}

export interface SlideDeck {
  id: string;
  title: string;
  course: string;
  module: string;
  /** ready: images built; building: text shown while a build runs; text: this machine cannot render
   * images; failed: the last build failed (see `error`). */
  status: "ready" | "building" | "text" | "failed";
  /** A build is due and none is running: POST .../build starts it. */
  stale?: boolean;
  images: boolean;
  /** What rendering needs and the machine lacks. */
  needs: string[];
  error: string;
  decks: { id: string; title: string }[];
  slides: SlideEntry[];
}

export interface QuizQuestion {
  id: string;
  prompt: string;
  /** The answer is never sent; the server grades. */
  options: string[];
  lesson: string | null;
  lessonTitle: string | null;
  box?: number | null;
  dueOn?: string | null;
  status?: "new" | "due" | "later";
}

export interface Quiz {
  id: string;
  title: string;
  course: string;
  questions: QuizQuestion[];
  dueCount?: number;
  newCount?: number;
}

export interface QuizAnswerResult {
  correct: boolean;
  answer: string;
  explanation: string;
  logged: boolean;
}

export interface StudyCounts {
  due: number;
  new: number;
}

export interface StudyHomeData {
  today: string;
  due: number;
  new: number;
  modules: { module: string; title: string; cards: StudyCounts; questions: StudyCounts }[];
  nextDrill: (LessonOutline & { course: string; track: string | null; reason: string }) | null;
  lecture: { module: string; title: string; decks: { id: string; title: string }[] } | null;
}
