import type { Course } from "./types";
import { useLabs } from "../../hooks/useCourses";
import { Markdown } from "./Markdown";
import { lessonsOf, moduleGroups, splitCourseReadme } from "./courseLogic";
import { useLearning } from "../../hooks/useLearning";
import { SourceList, ProgressBar, MasteryBar } from "./courseBits";
import { useOverview } from "./useOverview";

/** One course, opening on its readme: what the course is, what you will be able to do, then a card per module
 * in reading order (core before advanced when the course sorts them) with that group's syllabus under it, the
 * rest of the readme, and its references. */
export function Overview({ course, done, last, onOpen, onOpenConcept }: {
  course: Course; done: Set<string>; last?: string; onOpen: (p: string) => void; onOpenConcept: (id: string) => void;
}) {
  const { data: labsData } = useLabs();
  const { data: learning } = useLearning();
  const first = lessonsOf(course)[0];
  const resume = last ?? first?.id;
  const readme = (course.guide ?? []).find((l) => /\/readme$/.test(l.id));
  const overview = useOverview(readme?.id ?? null);
  const parts = overview ? splitCourseReadme(overview) : null;
  // The readme is the page, so only the references are still a link to follow.
  const guide = (course.guide ?? []).filter((l) => !parts || l !== readme);
  const hasReferences = guide.some((l) => /references$/.test(l.id));
  const prose = (body: string) => overview && !!body.trim() && (
    <div className="lesson-prose course-module-overview">
      <Markdown body={body} lessonId={overview.id} onOpenLesson={onOpen} onOpenConcept={onOpenConcept} sourceLinks={overview.sourceLinks} />
    </div>
  );
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--wide">
        <button onClick={() => onOpen("")} className="link-btn">← All courses</button>
        <h1 className="course-page-title course-page-title--overview">{course.title}</h1>
        {parts?.intro.trim() ? prose(parts.intro) : <p className="course-overview-summary">{course.summary}</p>}
        {course.outcomes?.length ? (
          <>
            <h2 className="section-label course-module-label">By the end you can</h2>
            <ol className="course-objectives">
              {course.outcomes.map((o) => <li key={o}>{o}</li>)}
            </ol>
          </>
        ) : null}
        {resume && (
          <button onClick={() => onOpen(resume)} className="btn-primary">
            {last ? "Continue where you left off" : "Start the course"} →
          </button>
        )}
        {moduleGroups(course.modules).map((g) => (
          <section key={g.key || "all"} aria-label={g.title || "Modules"}>
            {g.title && <h2 className="section-label course-module-label">{g.title}</h2>}
            <div className="course-grid">
              {g.modules.map((m) => {
                const labs = (labsData?.labs ?? []).filter((l) => l.course === course.id && l.module === m.id).length;
                const n = m.lessons.filter((l) => done.has(l.id)).length;
                const tests = [
                  m.quizCount && `${m.quizCount} questions`,
                  m.flashcardCount && `${m.flashcardCount} flashcards`,
                  m.problemCount && `${m.problemCount} problems`,
                ].filter(Boolean);
                return (
                  <button key={m.id} onClick={() => onOpen(`${course.id}/${m.id}`)} className="course-card">
                    <div className="course-card-title">{m.title}</div>
                    <div className="course-card-summary">{m.summary}</div>
                    <div className="course-card-meta">
                      {m.lessons.length} lessons{labs > 0 && ` · ${labs} labs`}
                      {n > 0 && <span className="text-success"> · {n} done</span>}
                    </div>
                    {tests.length > 0 && <div className="course-card-meta course-card-tests">Test yourself: {tests.join(" · ")}</div>}
                    <ProgressBar value={m.lessons.length ? n / m.lessons.length : 0} />
                    <MasteryBar mastery={learning?.modules[`${course.id}/${m.id}`]} />
                  </button>
                );
              })}
            </div>
            {parts && prose(parts.groups[g.key] ?? "")}
          </section>
        ))}
        {parts && prose(parts.rest)}
        {(guide.length > 0 || !!course.readings?.length || !!course.readingsCount || !!course.references?.length) && (
          <>
            <h2 className="section-label course-module-label">{parts ? "References" : "Guide and references"}</h2>
            {guide.length > 0 && (
              <div className="course-module-list">
                {guide.map((l) => (
                  <div key={l.id} className="course-row course-row--stack">
                    <a href={`#/courses/${l.id}`} className="course-row-title">{/references$/.test(l.id) ? "References" : "Course guide"}</a>
                    <span className="course-row-section">
                      {/references$/.test(l.id) ? "The books, papers and courses behind this course" : "How the course is built, what each module asks of you and its rules of thumb"}
                    </span>
                  </div>
                ))}
              </div>
            )}
            {/* The references page names each source with what it is for and a link that opens; the raw file list repeats it without either. */}
            {!hasReferences && <SourceList label="Readings" items={course.readings ?? []} count={course.readingsCount} />}
            <SourceList label="Reference material (not imported)" items={course.references ?? []} />
          </>
        )}
      </div>
    </div>
  );
}
