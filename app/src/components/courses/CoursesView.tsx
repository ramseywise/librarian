import { useCallback, useEffect, useState } from "react";
import type { Course, CourseModule, Lesson, SearchHit } from "./types";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { useCourses, useLabs } from "../../hooks/useCourses";
import { Check } from "./Check";
import { LessonView, type TocEntry } from "./LessonView";
import { StudyLevels } from "./StudyLevels";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";
import { apiFetch } from "../../utils/api";

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
  const module = course?.modules.find((m) => route === `${course.id}/${m.id}`);
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

  if (!route || !course) {
    return <Catalog courses={courses} done={progress.done} onOpen={open} />;
  }
  if (!route.includes("/")) {
    return <Overview course={course} done={progress.done} last={progress.last[course.id]} onOpen={open} />;
  }
  if (module) return <ModulePage course={course} module={module} done={progress.done} onOpen={open} />;
  return (
    <LessonLayout
      course={course}
      lessonId={route}
      progress={progress}
      onOpen={open}
      onOpenConcept={onOpenConcept}
      onAsk={onAsk}
    />
  );
}

// ---------------------------------------------------------------------------
// Catalog
// ---------------------------------------------------------------------------

const lessonsOf = (c: Course) => c.modules.flatMap((m) => m.lessons);

function Catalog({ courses, done, onOpen }: {
  courses: Course[]; done: Set<string>; onOpen: (p: string) => void;
}) {
  const [query, setQuery] = useState("");
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--wide">
        <h1 className="course-page-title">Courses</h1>
        <p className="course-page-lede">
          Coursework across the AI engineering curriculum. Lessons link into the wiki graph.
        </p>
        <SearchBox value={query} onChange={setQuery} placeholder="Search all lessons…" />
        {query.trim().length >= 2 ? (
          <SearchResults query={query} onOpen={onOpen} />
        ) : (
          <div className="course-grid">
            {courses.map((c) => {
              const ids = lessonsOf(c).map((l) => l.id);
              const n = ids.filter((id) => done.has(id)).length;
              return (
                <button key={c.id} onClick={() => onOpen(c.id)} className="course-card">
                  <div className="course-card-title">{c.title}</div>
                  <div className="course-card-summary">{c.summary}</div>
                  <div className="course-card-meta">
                    {c.modules.length} modules · {c.lessonCount} lessons
                    {n > 0 && <span className="text-success"> · {n} done</span>}
                  </div>
                  <ProgressBar value={ids.length ? n / ids.length : 0} />
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function SearchResults({ query, onOpen }: { query: string; onOpen: (p: string) => void }) {
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  useEffect(() => {
    const ctrl = new AbortController();
    const t = setTimeout(() => {
      apiFetch(`/api/courses/search?q=${encodeURIComponent(query.trim())}`, { signal: ctrl.signal })
        .then((r) => r.json())
        .then(setHits)
        .catch(() => {});
    }, 200);
    return () => { clearTimeout(t); ctrl.abort(); };
  }, [query]);

  if (!hits) return <div className="course-status">Searching…</div>;
  if (!hits.length) return <div className="course-status">No lessons match.</div>;
  return (
    <div className="course-hits">
      {hits.map((h) => (
        <button key={h.id} onClick={() => onOpen(h.id)} className="course-nav-item course-hit">
          <div className="course-hit-where">{h.course} · {h.section}</div>
          <div className="course-hit-title">{h.title}</div>
          <div className="course-hit-snippet">{h.snippet}</div>
        </button>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Course overview
// ---------------------------------------------------------------------------

/** One course: a card per module with what it holds. A card opens the module's page. */
function Overview({ course, done, last, onOpen }: {
  course: Course; done: Set<string>; last?: string; onOpen: (p: string) => void;
}) {
  const { data: labsData } = useLabs();
  const first = lessonsOf(course)[0];
  const resume = last ?? first?.id;
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--wide">
        <button onClick={() => onOpen("")} className="link-btn">← All courses</button>
        <h1 className="course-page-title course-page-title--overview">{course.title}</h1>
        <p className="course-overview-summary">{course.summary}</p>
        {resume && (
          <button onClick={() => onOpen(resume)} className="btn-primary">
            {last ? "Continue where you left off" : "Start the course"} →
          </button>
        )}
        <div className="course-grid">
          {course.modules.map((m, i) => {
            const labs = (labsData?.labs ?? []).filter((l) => l.course === course.id && l.module === m.id).length;
            const n = m.lessons.filter((l) => done.has(l.id)).length;
            const tests = [
              m.quizCount && `${m.quizCount} questions`,
              m.flashcardCount && `${m.flashcardCount} flashcards`,
              m.problemCount && `${m.problemCount} problems`,
            ].filter(Boolean);
            return (
              <button key={m.id} onClick={() => onOpen(`${course.id}/${m.id}`)} className="course-card">
                <div className="course-module-kicker">Module {i + 1}</div>
                <div className="course-card-title">{m.title}</div>
                <div className="course-card-summary">{m.summary}</div>
                <div className="course-card-meta">
                  {m.lessons.length} lessons{labs > 0 && ` · ${labs} labs`}
                  {n > 0 && <span className="text-success"> · {n} done</span>}
                </div>
                {tests.length > 0 && <div className="course-card-meta course-card-tests">Test yourself: {tests.join(" · ")}</div>}
                <ProgressBar value={m.lessons.length ? n / m.lessons.length : 0} />
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Module page
// ---------------------------------------------------------------------------

/** One module with everything it has, all in view and in the order it is used: lectures (the decks), lessons,
 * study (the three levels) and labs, then the readings. A part the module lacks says so. */
function ModulePage({ course, module: m, done, onOpen }: {
  course: Course; module: CourseModule; done: Set<string>; onOpen: (p: string) => void;
}) {
  const { data: labsData } = useLabs();
  const labs = (labsData?.labs ?? []).filter((l) => l.course === course.id && l.module === m.id);
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--overview">
        <button onClick={() => onOpen(course.id)} className="link-btn">← {course.title}</button>
        <h1 className="course-page-title course-page-title--overview">{m.title}</h1>
        {m.summary && <p className="course-overview-summary">{m.summary}</p>}
        <h2 className="section-label course-module-label">Lectures</h2>
        {m.decks?.length ? (
          <div className="course-module-list">
            {m.decks.map((d) => (
              <div key={d.id} className="course-row">
                <a href={`#/slides/${d.id}`} className="course-row-title">▶ {d.title}</a>
                <span className="course-row-section">{d.subtitle || (d.id === `${course.id}/${m.id}` ? "The whole module" : "Lecture")}</span>
              </div>
            ))}
          </div>
        ) : <p className="course-none">No lecture deck yet.</p>}
        <h2 className="section-label course-module-label">Lessons</h2>
        <div className="course-module-list">
          {m.lessons.map((l) => (
            <div key={l.id} className="course-row">
              <Check on={done.has(l.id)} />
              <a href={`#/courses/${l.id}`} className="course-row-title">{l.title}</a>
              {l.quizCount ? <a href={`#/quiz/${l.id}?choice`} className="course-row-test">{l.quizCount} questions</a> : null}
              {l.flashcardCount ? <a href={`#/flashcards/${l.id}`} className="course-row-test">{l.flashcardCount} flashcards</a> : null}
              {l.problemCount ? <a href={`#/quiz/${l.id}?worked`} className="course-row-test">{l.problemCount} problems</a> : null}
              {l.section && <span className="course-row-section">{l.section}</span>}
              {l.kind === "notebook" && <span className="kind-badge">notebook</span>}
            </div>
          ))}
        </div>
        <h2 className="section-label course-module-label">Study</h2>
        {(m.quizCount || m.flashcardCount || m.problemCount) ? (
          <StudyLevels id={`${course.id}/${m.id}`} quizCount={m.quizCount} flashcardCount={m.flashcardCount} problemCount={m.problemCount} />
        ) : <p className="course-none">No questions or flashcards yet.</p>}
        <h2 className="section-label course-module-label">Labs</h2>
        {labs.length > 0 ? (
          <div className="course-module-list">
            {labs.map((lab) => (
              <div key={lab.id} className="course-row course-row--stack">
                <a href={`#/labs/${lab.id}`} className="course-row-title">{lab.title}</a>
                <span className="course-row-section">{lab.purpose}</span>
              </div>
            ))}
          </div>
        ) : <p className="course-none">No labs yet.</p>}
        <SourceList label="Readings" items={m.readings} count={m.readingsCount} />
        <SourceList label="Reference material (not imported)" items={m.references} />
      </div>
    </div>
  );
}

function SourceList({ label, items, count }: {
  label: string; items: { title: string; source: string; url?: string }[]; count?: number;
}) {
  // Without the local private overlay only the count is public.
  if (!items?.length) {
    return count ? <p className="course-sources">{label}: {count} (the list is kept locally)</p> : null;
  }
  return (
    <div className="course-sources">
      <h2 className="section-label course-module-label">{label}</h2>
      <ul>
        {items.map((it) => (
          <li key={it.source}>
            {it.url ? <a href={it.url} target="_blank" rel="noreferrer">{it.title}</a>
              : <span title={it.source}>{it.title}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Lesson layout: lesson + page contents
// ---------------------------------------------------------------------------

function LessonLayout({ course, lessonId, progress, onOpen, onOpenConcept, onAsk }: {
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
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status === 404 ? "Lesson not found" : `HTTP ${r.status}`))))
      .then((l: Lesson) => {
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

// ---------------------------------------------------------------------------
// Bits
// ---------------------------------------------------------------------------

function Centered({ children }: { children: React.ReactNode }) {
  return (
    <div className="course-centered">
      <div>{children}</div>
    </div>
  );
}

function SearchBox({ value, onChange, placeholder }: {
  value: string; onChange: (v: string) => void; placeholder: string;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      data-view-search
      className="search-box"
    />
  );
}

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="progress-bar">
      <div className="progress-bar-fill" style={{ width: `${Math.round(value * 100)}%` }} />
    </div>
  );
}
