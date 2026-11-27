import { useEffect, useState } from "react";
import type { LessonOutline } from "../components/courses/types";
import { conceptLessonsSchema } from "../schemas/courses";
import { apiFetch, parseJson } from "../utils/api";

export type ConceptLesson = LessonOutline & { course: string };

/** The course lessons that link a wiki page; empty until they arrive, or if none do. */
export function useConceptLessons(pageId: string | null): ConceptLesson[] {
  const [lessons, setLessons] = useState<ConceptLesson[]>([]);
  useEffect(() => {
    let cancelled = false;
    setLessons([]);
    if (!pageId) return;
    apiFetch(`/api/courses/concept/${encodeURIComponent(pageId)}`)
      .then((r) => (r.ok ? parseJson(r, conceptLessonsSchema) : []))
      .then((ls) => !cancelled && setLessons(ls))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [pageId]);
  return lessons;
}
