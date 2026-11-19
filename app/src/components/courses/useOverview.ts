import { useEffect, useState } from "react";
import type { Lesson } from "./types";
import { lessonSchema } from "../../schemas/courses";
import { apiFetch, parseJson } from "../../utils/api";

/** The module's readme, which is the body of its page. Null while it loads and when the module has none. */
export function useOverview(lessonId: string | null): Lesson | null {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  useEffect(() => {
    if (!lessonId) return;
    let cancelled = false;
    apiFetch(`/api/courses/lessons/${lessonId}`)
      .then((r) => (r.ok ? parseJson(r, lessonSchema) : null))
      .then((l) => !cancelled && setLesson(l))
      .catch(() => undefined);
    return () => { cancelled = true; };
  }, [lessonId]);
  return lesson?.id === lessonId ? lesson : null;
}
