import { useCallback } from "react";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { useCourses } from "../../hooks/useCourses";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import { Centered } from "./courseBits";
import { Catalog } from "./Catalog";
import { Overview } from "./Overview";
import { ModulePage } from "./ModulePage";
import { LessonLayout } from "./LessonLayout";
import { ResourceNotice } from "../ResourceNotice";
import "./courses.css";

interface Props {
  /** Route path after `/courses` — "" (catalog), "<course>", or "<lesson id>". */
  route: string;
  navigate: (path: string) => void;
  onOpenConcept: (pageId: string) => void;
  onAsk: (question: string) => void;
}

export function CoursesView({ route, navigate, onOpenConcept, onAsk }: Props) {
  const { data: courses, error, retry } = useCourses();
  const progress = useCourseProgress();
  // Stable identity: it reaches the memoised lesson Markdown, which must not re-render
  // (and lose its TOC observers) on every progress change.
  const open = useCallback((path: string) => navigate(`/courses/${path}`), [navigate]);

  const courseId = route.split("/")[0];
  const course = courses?.find((c) => c.id === courseId);
  // A module's readme is the body of its page, so a link to the readme opens the page.
  const module = course?.modules.find((m) => route === `${course.id}/${m.id}` || route === `${course.id}/${m.id}/readme`);
  const isLesson = !!course && route.includes("/") && !module;
  // Lesson routes set their own title once the lesson has loaded.
  useDocumentTitle(isLesson ? null : module && course ? pageTitle(module.title, course.title) : course ? pageTitle(course.title) : pageTitle("Courses"));

  if (error) {
    return (
      <Centered>
        Could not load courses: {error}
        <div className="course-retry"><button onClick={retry} className="btn-primary">Retry</button></div>
      </Centered>
    );
  }
  if (!courses) return <Centered>Loading courses…</Centered>;
  if (!courses.length) {
    return <Centered>No courses yet. Add files under data/courses/.</Centered>;
  }

  const view =
    !route || !course ? (
      <Catalog courses={courses} done={progress.done} onOpen={open} />
    ) : !route.includes("/") ? (
      <Overview course={course} done={progress.done} last={progress.last[course.id]} onOpen={open} onOpenConcept={onOpenConcept} />
    ) : module ? (
      <ModulePage course={course} module={module} done={progress.done} onOpen={open} onOpenConcept={onOpenConcept} />
    ) : (
      <LessonLayout
        course={course}
        lessonId={route}
        progress={progress}
        onOpen={open}
        onOpenConcept={onOpenConcept}
        onAsk={onAsk}
      />
    );
  return (
    <>
      {progress.error && (
        <div className="course-notice">
          <ResourceNotice what="Your progress" error={progress.error} onRetry={progress.retry} />
        </div>
      )}
      {view}
    </>
  );
}
