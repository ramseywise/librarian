/** Sisyphus drill schema fields (drills/README.md), on lessons of kind "drill". */
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
  references: SourceRef[];
  lessons: LessonOutline[];
}

export interface Course {
  id: string;
  title: string;
  summary: string;
  order: number;
  lessonCount: number;
  modules: CourseModule[];
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
