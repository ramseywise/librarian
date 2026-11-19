import { useEffect, useState } from "react";
import type { Course, Lesson } from "./types";
import type { useCourseProgress } from "../../hooks/useCourseProgress";
import { LessonView, type TocEntry } from "./LessonView";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import { lessonSchema } from "../../schemas/courses";
import { apiFetch, parseJson } from "../../utils/api";
import { Centered } from "./courseBits";

export function LessonLayout({ course, lessonId, progress, onOpen, onOpenConcept, onAsk }: {
  course: Course;
  lessonId: string;
  progress: ReturnType<typeof useCourseProgress>;
  onOpen: (p: string) => void;
  onOpenConcept: (pageId: string) => void;
  onAsk: (q: string) => void;
}) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [toc, setToc] = useState<TocEntry[]>([]);
  const [activeHeading, setActiveHeading] = useState<string | null>(null);
  const { markVisited, markDone } = progress;
  const loaded = lesson?.id === lessonId ? lesson : null;
  useDocumentTitle(pageTitle(loaded?.title ?? "Loading…", course.title));

  useEffect(() => {
    let cancelled = false;
    setError(null);
    apiFetch(`/api/courses/lessons/${lessonId}`)
      .then((r) => (r.ok ? parseJson(r, lessonSchema) : Promise.reject(new Error(r.status === 404 ? "Lesson not found" : `HTTP ${r.status}`))))
      .then((l) => {
        if (cancelled) return;
        setLesson(l);
        markVisited(course.id, l.id);
      })
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => { cancelled = true; };
  }, [lessonId, course.id, markVisited]);

  return (
    <div className="lesson-layout">
      <div className="lesson-main">
        {error ? <Centered>{error}</Centered>
          : !loaded ? <Centered>Loading…</Centered>
          : (
            <LessonView
              lesson={loaded}
              courseTitle={course.title}
              decks={course.modules.find((m) => m.lessons.some((l) => l.id === lessonId))?.decks}
              done={progress.done.has(loaded.id)}
              onMarkDone={() => markDone(loaded.id)}
              onOpen={onOpen}
              onOpenConcept={onOpenConcept}
              onAsk={onAsk}
              onToc={setToc}
              onActiveHeading={setActiveHeading}
            />
          )}
      </div>
      {loaded && toc.length > 1 && (
        <nav className="lesson-toc" aria-label="On this page">
          <div className="section-label">On this page</div>
          {toc.map((t) => (
            <a key={t.id} href={`#${t.id}`}
              onClick={(e) => { e.preventDefault(); document.getElementById(t.id)?.scrollIntoView({ behavior: "smooth" }); }}
              aria-current={activeHeading === t.id ? "location" : undefined}
              className={`lesson-toc-link${t.level === 3 ? " lesson-toc-link--h3" : ""}`}>
              {t.text}
            </a>
          ))}
        </nav>
      )}
    </div>
  );
}
