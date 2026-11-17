import { useCallback, useEffect, useState } from "react";
import type { Course, CourseModule, Lesson, SearchHit } from "./types";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { useCourses, useLabs, useStudyProgress } from "../../hooks/useCourses";
import { Check } from "./Check";
import { LessonView, type TocEntry } from "./LessonView";
import { StudyLevels } from "./StudyLevels";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";
import { apiFetch } from "../../utils/api";
import { moduleFacet } from "../../utils/curriculum";
import { mapPath } from "../../utils/mapRoute";

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
  if (module) return <ModulePage course={course} module={module} done={progress.done} onOpen={open} onOpenConcept={onOpenConcept} />;
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

const GROUP_TITLES: Record<string, string> = { core: "Core modules", advanced: "Advanced topics" };

/** The course's modules as the groups its README sorts them into, in order. A course with no groups is one
 * unlabelled group. */
export function moduleGroups(modules: CourseModule[]): { key: string; title: string; modules: CourseModule[] }[] {
  const groups: { key: string; title: string; modules: CourseModule[] }[] = [];
  for (const m of modules) {
    const key = m.group ?? "";
    const last = groups[groups.length - 1];
    if (last && last.key === key) last.modules.push(m);
    else groups.push({ key, title: GROUP_TITLES[key] ?? "", modules: [m] });
  }
  return groups.length > 1 || groups[0]?.key ? groups.map((g) => ({ ...g, title: g.title || "More" })) : groups;
}

/** One course, and where to start it: what you will be able to do, then a card per module in reading order
 * (core before advanced when the course sorts them), then the course guide and its references. */
function Overview({ course, done, last, onOpen }: {
  course: Course; done: Set<string>; last?: string; onOpen: (p: string) => void;
}) {
  const { data: labsData } = useLabs();
  const first = lessonsOf(course)[0];
  const resume = last ?? first?.id;
  const guide = course.guide ?? [];
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--wide">
        <button onClick={() => onOpen("")} className="link-btn">← All courses</button>
        <h1 className="course-page-title course-page-title--overview">{course.title}</h1>
        <p className="course-overview-summary">{course.summary}</p>
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
                  </button>
                );
              })}
            </div>
          </section>
        ))}
        {(guide.length > 0 || !!course.readings?.length || !!course.readingsCount || !!course.references?.length) && (
          <>
            <h2 className="section-label course-module-label">Guide and references</h2>
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
            <SourceList label="Readings" items={course.readings ?? []} count={course.readingsCount} />
            <SourceList label="Reference material (not imported)" items={course.references ?? []} />
          </>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Module page: the topic page
// ---------------------------------------------------------------------------

/** One topic with everything it has, in the order it is used: test yourself (the three levels, with how far you
 * are), learn (the lecture decks, then the notes in reading order), hands-on (labs and drills), the wiki pages its
 * lessons cite, and its references. A part the module lacks says so. */
function ModulePage({ course, module: m, done, onOpen, onOpenConcept }: {
  course: Course; module: CourseModule; done: Set<string>; onOpen: (p: string) => void; onOpenConcept: (id: string) => void;
}) {
  const { data: labsData } = useLabs();
  const { data: studyProgress } = useStudyProgress();
  const id = `${course.id}/${m.id}`;
  const labs = (labsData?.labs ?? []).filter((l) => l.course === course.id && l.module === m.id);
  const notes = m.lessons.filter((l) => l.kind !== "drill");
  const drills = m.lessons.filter((l) => l.kind === "drill");
  const next = notes.find((l) => !done.has(l.id));
  const wiki = m.wiki ?? [];
  const moreWiki = Math.max((m.wikiCount ?? wiki.length) - wiki.length, 0);
  const graph = `#${mapPath({ level: "all", tags: [moduleFacet(course.id, m.id)] })}`;
  // A non-object (an unsigned or failed request) means no progress, not a broken page.
  const progress = studyProgress && !Array.isArray(studyProgress) ? studyProgress[id] : undefined;
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--overview">
        <button onClick={() => onOpen(course.id)} className="link-btn">← {course.title}</button>
        <h1 className="course-page-title course-page-title--overview">{m.title}</h1>
        {m.summary && <p className="course-overview-summary">{m.summary}</p>}

        {m.objectives?.length ? (
          <>
            <h2 className="section-label course-module-label">After this module you can</h2>
            <ol className="course-objectives">
              {m.objectives.map((o) => <li key={o}>{o}</li>)}
            </ol>
          </>
        ) : null}

        <h2 className="section-label course-module-label">Test yourself</h2>
        {(m.quizCount || m.flashcardCount || m.problemCount) ? (
          <StudyLevels id={id} quizCount={m.quizCount} flashcardCount={m.flashcardCount} problemCount={m.problemCount} progress={progress} />
        ) : <p className="course-none">No questions or flashcards yet.</p>}

        <h2 className="section-label course-module-label">Learn</h2>
        {m.decks?.length ? (
          <div className="course-module-list">
            {m.decks.map((d) => (
              <div key={d.id} className="course-row">
                <a href={`#/slides/${d.id}`} className="course-row-title">{d.title}</a>
                <span className="course-row-section">{d.subtitle || (d.id === id ? "The whole module" : "Lecture")}</span>
              </div>
            ))}
          </div>
        ) : <p className="course-none">No lecture deck yet.</p>}
        {notes.length > 0 && (
          <div className="course-module-list course-module-list--notes">
            {notes.map((l, i) => (
              <div key={l.id} className="course-row">
                <Check on={done.has(l.id)} />
                <span className="course-row-no">{i + 1}</span>
                <a href={`#/courses/${l.id}`} className="course-row-title">{l.title}</a>
                {l.quizCount ? <a href={`#/quiz/${l.id}?choice`} className="course-row-test">{l.quizCount} questions</a> : null}
                {l.flashcardCount ? <a href={`#/flashcards/${l.id}`} className="course-row-test">{l.flashcardCount} flashcards</a> : null}
                {l.problemCount ? <a href={`#/quiz/${l.id}?worked`} className="course-row-test">{l.problemCount} problems</a> : null}
                {l.kind === "notebook" && <span className="kind-badge">notebook</span>}
                {done.has(l.id) ? <span className="course-row-state">read</span> : l === next ? <span className="course-row-state course-row-state--next">next</span> : null}
              </div>
            ))}
          </div>
        )}

        <h2 className="section-label course-module-label">Hands-on</h2>
        {labs.length > 0 || drills.length > 0 ? (
          <div className="course-module-list">
            {labs.map((lab) => (
              <div key={lab.id} className="course-row course-row--stack">
                <a href={`#/labs/${lab.id}`} className="course-row-title">{lab.title}</a>
                <span className="course-row-section">{lab.purpose}</span>
              </div>
            ))}
            {drills.map((d) => (
              <div key={d.id} className="course-row">
                <a href={`#/courses/${d.id}`} className="course-row-title">{d.title}</a>
                <span className="course-row-section">Drill{d.drill?.difficulty ? ` · ${d.drill.difficulty}` : ""}</span>
              </div>
            ))}
          </div>
        ) : <p className="course-none">No labs or drills yet.</p>}

        <h2 className="section-label course-module-label">Wiki</h2>
        {wiki.length > 0 ? (
          <>
            <div className="course-module-list">
              {wiki.map((p) => (
                <div key={p.id} className="course-row course-row--stack">
                  <button onClick={() => onOpenConcept(p.id)} className="course-row-title course-wiki-title" title="Open on the graph">{p.title}</button>
                  {p.summary && <span className="course-row-section">{p.summary}</span>}
                </div>
              ))}
            </div>
            <p className="course-wiki-more">
              {moreWiki > 0 && <>{moreWiki} more cited by these lessons. </>}
              <a href={graph}>Show on the graph</a>
            </p>
          </>
        ) : <p className="course-none">No wiki pages cover this yet.</p>}

        {(m.references?.length > 0 || m.readings?.length > 0 || !!m.readingsCount) && (
          <>
            <h2 className="section-label course-module-label">References</h2>
            <SourceList label="Readings" items={m.readings} count={m.readingsCount} />
            <SourceList label="Reference material (not imported)" items={m.references} />
          </>
        )}
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
      <h3 className="course-sources-label">{label}</h3>
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
