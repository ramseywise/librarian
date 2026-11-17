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
  /** Multiple-choice questions; absent when the lesson has none. */
  quizCount?: number;
  /** Worked problems; absent when the lesson has none. */
  problemCount?: number;
  /** Present (true) only for a lesson under data/courses/private/: local, never published. */
  private?: boolean;
}

export interface SourceRef {
  title: string;
  source: string;
  url?: string;
}

/** A lecture deck as the catalog lists it; `subtitle` tells apart decks that share a title. */
export interface Deck { id: string; title: string; subtitle?: string; /** The lecture that introduces a lecture series. */ overview?: boolean }

export interface CourseModule {
  id: string;
  title: string;
  summary: string;
  order: number;
  /** "core" or "advanced", when the course README sorts its modules that way. */
  group?: string;
  /** What you can do after the module, from the course README. Absent when it lists none. */
  objectives?: string[];
  readings: SourceRef[];
  /** How many readings the module lists; the list itself is only present with the local private overlay. */
  readingsCount?: number;
  references: SourceRef[];
  lessons: LessonOutline[];
  /** Lecture decks (`#/slides/<id>`): the module's own deck first, then its lectures. Absent when it has none. */
  decks?: Deck[];
  /** Absent when the module has no flashcards. */
  flashcardCount?: number;
  /** Multiple-choice questions; absent when the module has none. */
  quizCount?: number;
  /** Worked problems; absent when the module has none. */
  problemCount?: number;
  /** Public wiki pages the module's lessons cite, most-cited first, at most 12 (`wikiCount` is how many in all). */
  wiki?: WikiPageRef[];
  wikiCount?: number;
  /** True when only private lessons make up the module. */
  private?: boolean;
}

/** A wiki page as the topic page lists it. */
export interface WikiPageRef { id: string; title: string; summary: string }

/** One level of a module's study: items, those whose latest attempt was right, and those whose was not. */
export interface LevelProgress { total: number; right: number; redo: number }
/** The caller's progress per module id (`<course>/<module>`) and level; `GET /api/courses/study-progress`. */
export type StudyProgress = Record<string, Partial<Record<"choice" | "cards" | "worked", LevelProgress>>>;

export interface Course {
  id: string;
  title: string;
  summary: string;
  order: number;
  lessonCount: number;
  modules: CourseModule[];
  /** The course's own pages (its guide and references), shown on the course page and not as a module. */
  guide?: LessonOutline[];
  /** What you can do by the end of the course. Absent when its README lists none. */
  outcomes?: string[];
  /** The course's shared reading list; only the count without the local private overlay. */
  readings?: SourceRef[];
  readingsCount?: number;
  references?: SourceRef[];
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
  /** Labs whose manifest entry backs this lesson, or whose file it names. */
  labs?: LabOutline[];
}

/** A runnable practice example from a pillar's practice/manifest.yaml. `id` is its path under data/courses. */
export interface LabOutline {
  id: string;
  title: string;
  course: string;
  module: string;
  /** Relative to the module, starting with practice/. */
  path: string;
  purpose: string;
  pattern: string;
  language: "python" | "typescript" | "jupyter" | string;
  runsOffline: boolean;
  /** It has an entry script (`run`) / a `verified_by` this app can run (`check`). */
  hasRun: boolean;
  hasCheck: boolean;
}

export interface LabRow extends LabOutline {
  notes: LessonOutline[];
}

export interface LabsList {
  labs: LabRow[];
  /** This server runs labs (a dev machine with LIBRARIAN_DEV_RUN_LABS); false in a deployment. */
  canRun: boolean;
}

export interface LabFile {
  /** Relative to the practice folder. */
  path: string;
  text: string;
}

export interface LabDetail extends LabOutline {
  licence: string;
  verifiedBy: string;
  run: string | null;
  check: string | null;
  files: LabFile[];
  notes: LessonOutline[];
  canRun: boolean;
}

export interface PracticeDrill extends LessonOutline {
  course: string;
  drill: DrillMeta;
  concepts: ConceptRef[];
  /** From the caller's drill attempts (app runs and an imported drill log); absent if none. */
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

export type SlideBeat = "problem" | "fundamentals" | "practice" | "pitfalls" | "wrap";

/** Where a slide sits: its part's number (null in a closing part), title, and how many numbered parts there are. */
export interface SlidePart {
  n: number | null;
  title: string;
  of: number;
}

/** A deck's slide as data, drawn by `SlideFrame`. `body` holds the layout's own yaml keys, as written. */
export type SlideFrameData =
  | { n: number; kind: "title"; title: string; subtitle: string; tagline: string; byline: string; reference: string;
      agenda: { n: number; title: string; summary: string }[]; notes: string; narration: string }
  | { n: number; kind: "divider"; title: string; summary: string; part: SlidePart; notes: string; narration: string }
  | { n: number; kind: "slide"; layout: string; beat: SlideBeat | null; level: string; title: string; kicker: string;
      lead: string; takeaway: string; source: string; part: SlidePart; body: Record<string, unknown>;
      notes: string; narration: string };

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
  /** The deck as data, read from the yaml: what the viewer draws. Absent or empty: fall back to `slides`. */
  frames?: SlideFrameData[];
}

export interface QuizQuestion {
  id: string;
  prompt: string;
  /** The answer is never sent; the server grades. Empty for a worked problem. */
  options: string[];
  /** `worked`: no options, the learner types a number. Absent means `choice`. */
  kind?: "choice" | "worked";
  /** A worked problem with a hint to ask for; the hint itself is not sent ahead. */
  hasHint?: boolean;
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
