import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Course, Lesson, LessonOutline, SearchHit } from "../../courses/types";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { useCourses } from "../../hooks/useCourses";
import { LessonView, type TocEntry } from "./LessonView";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
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
  const isLesson = !!course && route.includes("/");
  // Lesson routes set their own title once the lesson has loaded.
  useDocumentTitle(isLesson ? null : course ? pageTitle(course.title) : pageTitle("Courses"));

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
    return <Centered>No courses yet. Run <code>make import-courses</code> or add files under data/courses/.</Centered>;
  }

  if (!route || !course) {
    return <Catalog courses={courses} done={progress.done} last={progress.last} onOpen={open} />;
  }
  if (!route.includes("/")) {
    return <Overview course={course} done={progress.done} last={progress.last[course.id]} onOpen={open} />;
  }
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

function Catalog({ courses, done, last, onOpen }: {
  courses: Course[]; done: Set<string>; last: Record<string, string>; onOpen: (p: string) => void;
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
                <button key={c.id} onClick={() => onOpen(last[c.id] ?? c.id)} className="course-card">
                  <div className="course-card-title">{c.title}</div>
                  <div className="course-card-summary">{c.summary}</div>
                  <div className="course-card-meta">
                    {c.modules.length} modules · {c.lessonCount} lessons
                    {n > 0 && <span className="text-success"> · {n} done</span>}
                  </div>
                  <ProgressBar value={ids.length ? n / ids.length : 0} />
                  {last[c.id] && <div className="course-card-continue">Continue →</div>}
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
      fetch(`/api/courses/search?q=${encodeURIComponent(query.trim())}`, { signal: ctrl.signal })
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

function Overview({ course, done, last, onOpen }: {
  course: Course; done: Set<string>; last?: string; onOpen: (p: string) => void;
}) {
  const first = lessonsOf(course)[0];
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--overview">
        <button onClick={() => onOpen("")} className="link-btn">← All courses</button>
        <h1 className="course-page-title course-page-title--overview">{course.title}</h1>
        <p className="course-overview-summary">{course.summary}</p>
        {(last ?? first) && (
          <button onClick={() => onOpen(last ?? first.id)} className="btn-primary">
            {last ? "Continue where you left off" : "Start the course"} →
          </button>
        )}
        {course.modules.map((m, i) => (
          <section key={m.id} className="course-module">
            <div className="course-module-kicker">Module {i + 1}</div>
            <h2 className="course-module-title">{m.title}</h2>
            {m.summary && <p className="course-module-summary">{m.summary}</p>}
            <div className="course-module-list">
              {m.lessons.map((l) => (
                <button key={l.id} onClick={() => onOpen(l.id)} className="course-nav-item course-row">
                  <Check on={done.has(l.id)} />
                  <span className="course-row-title">{l.title}</span>
                  {l.section && <span className="course-row-section">{l.section}</span>}
                  {l.kind === "notebook" && <span className="kind-badge">notebook</span>}
                </button>
              ))}
            </div>
            <SourceList label="Readings" items={m.readings} />
            <SourceList label="Reference material (not imported)" items={m.references} />
          </section>
        ))}
      </div>
    </div>
  );
}

function SourceList({ label, items }: { label: string; items: { title: string; source: string; url?: string }[] }) {
  if (!items?.length) return null;
  return (
    <details className="course-sources">
      <summary>{label} ({items.length})</summary>
      <ul>
        {items.map((it) => (
          <li key={it.source}>
            {it.url ? <a href={it.url} target="_blank" rel="noreferrer">{it.title}</a>
              : <span title={it.source}>{it.title}</span>}
          </li>
        ))}
      </ul>
    </details>
  );
}

// ---------------------------------------------------------------------------
// Lesson layout: sidebar + lesson
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
  const { markVisited, toggleDone } = progress;
  const loaded = lesson?.id === lessonId ? lesson : null;
  // Narrow screens only: the sidebar is a drawer behind a toggle (CSS hides both otherwise).
  const [drawerOpen, setDrawerOpen] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);
  const drawerBtnRef = useRef<HTMLButtonElement>(null);
  const mainRef = useRef<HTMLDivElement>(null);

  // Picking a lesson from the drawer closes it.
  useEffect(() => setDrawerOpen(false), [lessonId]);

  useEffect(() => {
    if (!drawerOpen) return;
    drawerRef.current?.querySelector<HTMLElement>("button, input, a[href]")?.focus();
    // The drawer is modal (backdrop): keep Tab and screen readers out of the lesson
    // behind it. Widening past the drawer breakpoint turns it back into a sidebar, so
    // close it then rather than leave the lesson inert.
    const main = mainRef.current;
    if (main) main.inert = true;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      e.preventDefault();
      setDrawerOpen(false);
      if (main) main.inert = false; // before focusing the toggle inside it
      drawerBtnRef.current?.focus();
    };
    document.addEventListener("keydown", onKey);
    const wide = window.matchMedia?.("(min-width: 1100px)");
    const onWide = () => wide?.matches && setDrawerOpen(false);
    wide?.addEventListener("change", onWide);
    return () => {
      document.removeEventListener("keydown", onKey);
      if (main) main.inert = false;
      wide?.removeEventListener("change", onWide);
    };
  }, [drawerOpen]);
  useDocumentTitle(pageTitle(loaded?.title ?? "Loading…", course.title));

  useEffect(() => {
    let cancelled = false;
    setError(null);
    fetch(`/api/courses/lessons/${lessonId}`)
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
      <div id="course-sidebar" ref={drawerRef} className={`course-drawer${drawerOpen ? " is-open" : ""}`}>
        <Sidebar
          course={course}
          activeId={lessonId}
          done={progress.done}
          onOpen={onOpen}
          toc={lesson?.id === lessonId ? toc : []}
          activeHeading={activeHeading}
        />
      </div>
      {drawerOpen && <div className="course-drawer-backdrop" onClick={() => setDrawerOpen(false)} />}
      <div className="lesson-main" ref={mainRef}>
        <div className="course-drawer-bar">
          <button
            ref={drawerBtnRef}
            type="button"
            className="pill-btn"
            aria-expanded={drawerOpen}
            aria-controls="course-sidebar"
            onClick={() => setDrawerOpen((o) => !o)}
          >
            Lessons
          </button>
          <span className="course-drawer-bar-title">{course.title}</span>
        </div>
        <div className="lesson-main-body">
        {error ? <Centered>{error}</Centered>
          : !lesson || lesson.id !== lessonId ? <Centered>Loading…</Centered>
          : (
            <LessonView
              lesson={lesson}
              courseTitle={course.title}
              done={progress.done.has(lesson.id)}
              onToggleDone={() => toggleDone(lesson.id)}
              onOpen={onOpen}
              onOpenConcept={onOpenConcept}
              onAsk={onAsk}
              onToc={setToc}
              onActiveHeading={setActiveHeading}
            />
          )}
        </div>
      </div>
    </div>
  );
}

function Sidebar({ course, activeId, done, onOpen, toc, activeHeading }: {
  course: Course; activeId: string; done: Set<string>; onOpen: (p: string) => void;
  toc: TocEntry[]; activeHeading: string | null;
}) {
  const [tocOpen, setTocOpen] = useState(true);
  const [filter, setFilter] = useState("");
  const activeModule = course.modules.find((m) => m.lessons.some((l) => l.id === activeId))?.id;
  const [collapsed, setCollapsed] = useState<Set<string>>(
    () => new Set(course.modules.map((m) => m.id).filter((id) => id !== activeModule))
  );

  // Expand the module of the lesson being viewed (e.g. after prev/next across modules).
  useEffect(() => {
    if (!activeModule) return;
    setCollapsed((prev) => {
      if (!prev.has(activeModule)) return prev;
      const next = new Set(prev);
      next.delete(activeModule);
      return next;
    });
    document.getElementById(`nav-${activeId}`)?.scrollIntoView({ block: "nearest" });
  }, [activeModule, activeId]);

  const f = filter.trim().toLowerCase();
  const modules = useMemo(
    () => course.modules
      .map((m) => ({ ...m, lessons: f ? m.lessons.filter((l) => `${l.title} ${l.section}`.toLowerCase().includes(f)) : m.lessons }))
      .filter((m) => m.lessons.length),
    [course.modules, f]
  );

  const toggle = (id: string) => setCollapsed((prev) => {
    const next = new Set(prev);
    if (next.has(id)) next.delete(id); else next.add(id);
    return next;
  });

  return (
    <nav className="course-sidebar" aria-label="Lessons">
      <div className="course-sidebar-head">
        <button onClick={() => onOpen("")} className="link-btn">← All courses</button>
        <button onClick={() => onOpen(course.id)} className="link-btn course-sidebar-title">
          {course.title}
        </button>
        <SearchBox value={filter} onChange={setFilter} placeholder="Filter lessons…" small />
      </div>
      <div className="course-scroll course-sidebar-list">
        {modules.map((m) => {
          const open = !!f || !collapsed.has(m.id);
          const n = m.lessons.filter((l) => done.has(l.id)).length;
          return (
            <div key={m.id}>
              <button onClick={() => toggle(m.id)} className="course-nav-item course-module-head">
                <span className="course-module-caret">{open ? "▾" : "▸"}</span>
                <span className="grow">{m.title}</span>
                <span className="course-module-count">{n}/{m.lessons.length}</span>
              </button>
              {open && (
                <ModuleLessons
                  lessons={m.lessons} activeId={activeId} done={done} onOpen={onOpen}
                  toc={toc} activeHeading={activeHeading} tocOpen={tocOpen} onToggleToc={() => setTocOpen((o) => !o)}
                />
              )}
            </div>
          );
        })}
      </div>
    </nav>
  );
}

function ModuleLessons({ lessons, activeId, done, onOpen, toc, activeHeading, tocOpen, onToggleToc }: {
  lessons: LessonOutline[]; activeId: string; done: Set<string>; onOpen: (p: string) => void;
  toc: TocEntry[]; activeHeading: string | null; tocOpen: boolean; onToggleToc: () => void;
}) {
  let prevSection = "";
  return (
    <div className="course-lessons">
      {lessons.map((l) => {
        const header = l.section && l.section !== prevSection ? l.section : null;
        prevSection = l.section;
        const active = l.id === activeId;
        const hasToc = active && toc.length > 1;
        return (
          <div key={l.id}>
            {header && <div className="course-section-head">{header}</div>}
            <div className={`course-lesson-row${active ? " is-active" : ""}`}>
              <button
                id={`nav-${l.id}`}
                onClick={() => onOpen(l.id)}
                aria-current={active ? "page" : undefined}
                className="course-nav-item course-lesson-link"
              >
                <Check on={done.has(l.id)} small />
                <span className="grow">{l.title}</span>
              </button>
              {hasToc && (
                <button
                  onClick={onToggleToc}
                  aria-expanded={tocOpen}
                  aria-controls={`toc-${l.id}`}
                  aria-label={tocOpen ? "Hide page contents" : "Show page contents"}
                  title={tocOpen ? "Hide page contents" : "Show page contents"}
                  className="course-nav-item course-toc-toggle"
                >
                  {tocOpen ? "▾" : "▸"}
                </button>
              )}
            </div>
            {hasToc && tocOpen && (
              <div id={`toc-${l.id}`} className="course-toc">
                {toc.map((t) => (
                  <a key={t.id} href={`#${t.id}`}
                    onClick={(e) => { e.preventDefault(); document.getElementById(t.id)?.scrollIntoView({ behavior: "smooth" }); }}
                    className={`course-nav-item course-toc-link course-toc-link--h${t.level === 3 ? 3 : 2}${activeHeading === t.id ? " is-active" : ""}`}>
                    {t.text}
                  </a>
                ))}
              </div>
            )}
          </div>
        );
      })}
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

function SearchBox({ value, onChange, placeholder, small }: {
  value: string; onChange: (v: string) => void; placeholder: string; small?: boolean;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={`search-box${small ? " search-box--small" : ""}`}
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

export function Check({ on, small }: { on: boolean; small?: boolean }) {
  const s = small ? 12 : 14;
  return (
    <span className={`check${on ? " is-on" : ""}`} style={{ width: s, height: s, fontSize: s - 4 }}>{on ? "✓" : ""}</span>
  );
}
