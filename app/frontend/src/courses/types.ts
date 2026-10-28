export interface LessonOutline {
  id: string;
  title: string;
  section: string;
  kind: "reading" | "notebook" | string;
  summary: string;
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

export interface SearchHit extends LessonOutline {
  course: string;
  snippet: string;
}
