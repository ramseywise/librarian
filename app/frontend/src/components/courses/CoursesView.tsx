import { useEffect, useMemo, useState } from "react";
import type { Course, Lesson, LessonOutline, SearchHit } from "../../courses/types";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { LessonView, type TocEntry } from "./LessonView";

interface Props {
  /** Route path after `/courses` — "" (catalog), "<course>", or "<lesson id>". */
  route: string;
  navigate: (path: string) => void;
  onOpenConcept: (pageId: string) => void;
  onAsk: (question: string) => void;
}

export function CoursesView({ route, navigate, onOpenConcept, onAsk }: Props) {
  const [courses, setCourses] = useState<Course[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const progress = useCourseProgress();

  useEffect(() => {
    fetch("/api/courses")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setCourses)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <Centered>Could not load courses: {error}</Centered>;
  if (!courses) return <Centered>Loading courses…</Centered>;
  if (!courses.length) {
    return <Centered>No courses yet. Run <code>make import-courses</code> or add files under data/courses/.</Centered>;
  }

  const courseId = route.split("/")[0];
  const course = courses.find((c) => c.id === courseId);
  const open = (path: string) => navigate(`/courses/${path}`);

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
    <div className="course-scroll" style={{ height: "100%", overflowY: "auto" }}>
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "40px 24px 60px" }}>
        <h1 style={{ color: "#f0f0f0", fontSize: 28, margin: "0 0 6px" }}>Courses</h1>
        <p style={{ color: "#888", margin: "0 0 20px", fontSize: 14 }}>
          Coursework across the AI engineering curriculum. Lessons link into the wiki graph.
        </p>
        <SearchBox value={query} onChange={setQuery} placeholder="Search all lessons…" />
        {query.trim().length >= 2 ? (
          <SearchResults query={query} onOpen={onOpen} />
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 14, marginTop: 20 }}>
            {courses.map((c) => {
              const ids = lessonsOf(c).map((l) => l.id);
              const n = ids.filter((id) => done.has(id)).length;
              return (
                <button key={c.id} onClick={() => onOpen(last[c.id] ?? c.id)} style={cardStyle}>
                  <div style={{ fontSize: 17, fontWeight: 600, color: "#f0f0f0", marginBottom: 6 }}>{c.title}</div>
                  <div style={{ fontSize: 13, color: "#999", lineHeight: 1.5, flex: 1 }}>{c.summary}</div>
                  <div style={{ fontSize: 11, color: "#666", marginTop: 14 }}>
                    {c.modules.length} modules · {c.lessonCount} lessons
                    {n > 0 && <span style={{ color: "#4CAF50" }}> · {n} done</span>}
                  </div>
                  <ProgressBar value={ids.length ? n / ids.length : 0} />
                  {last[c.id] && <div style={{ fontSize: 11, color: "#64b5f6", marginTop: 8 }}>Continue →</div>}
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

  if (!hits) return <div style={{ color: "#666", fontSize: 13, marginTop: 16 }}>Searching…</div>;
  if (!hits.length) return <div style={{ color: "#666", fontSize: 13, marginTop: 16 }}>No lessons match.</div>;
  return (
    <div style={{ marginTop: 12 }}>
      {hits.map((h) => (
        <button key={h.id} onClick={() => onOpen(h.id)} className="course-nav-item" style={hitStyle}>
          <div style={{ fontSize: 11, color: "#666" }}>{h.course} · {h.section}</div>
          <div style={{ fontSize: 14, color: "#e0e0e0", fontWeight: 500, margin: "2px 0" }}>{h.title}</div>
          <div style={{ fontSize: 12, color: "#888", lineHeight: 1.5 }}>{h.snippet}</div>
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
    <div className="course-scroll" style={{ height: "100%", overflowY: "auto" }}>
      <div style={{ maxWidth: 860, margin: "0 auto", padding: "32px 24px 60px" }}>
        <button onClick={() => onOpen("")} style={linkBtnStyle}>← All courses</button>
        <h1 style={{ color: "#f0f0f0", fontSize: 28, margin: "12px 0 6px" }}>{course.title}</h1>
        <p style={{ color: "#999", margin: "0 0 18px", fontSize: 14, lineHeight: 1.6 }}>{course.summary}</p>
        {(last ?? first) && (
          <button onClick={() => onOpen(last ?? first.id)} style={primaryBtnStyle}>
            {last ? "Continue where you left off" : "Start the course"} →
          </button>
        )}
        {course.modules.map((m, i) => (
          <section key={m.id} style={{ marginTop: 28 }}>
            <div style={{ fontSize: 11, color: "#666", textTransform: "uppercase", letterSpacing: "0.07em" }}>Module {i + 1}</div>
            <h2 style={{ color: "#e8e8e8", fontSize: 19, margin: "4px 0 4px" }}>{m.title}</h2>
            {m.summary && <p style={{ color: "#888", fontSize: 13, margin: "0 0 8px" }}>{m.summary}</p>}
            <div style={{ border: "1px solid #222", borderRadius: 8, overflow: "hidden" }}>
              {m.lessons.map((l) => (
                <button key={l.id} onClick={() => onOpen(l.id)} className="course-nav-item" style={rowStyle}>
                  <Check on={done.has(l.id)} />
                  <span style={{ flex: 1, color: "#d0d0d0" }}>{l.title}</span>
                  {l.section && <span style={{ color: "#555", fontSize: 11 }}>{l.section}</span>}
                  {l.kind === "notebook" && <span style={kindStyle}>notebook</span>}
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
    <details style={{ marginTop: 8, fontSize: 12, color: "#777" }}>
      <summary style={{ cursor: "pointer" }}>{label} ({items.length})</summary>
      <ul style={{ margin: "6px 0 0", paddingLeft: 18, lineHeight: 1.6 }}>
        {items.map((it) => (
          <li key={it.source}>
            {it.url ? <a href={it.url} target="_blank" rel="noreferrer" style={{ color: "#64b5f6" }}>{it.title}</a>
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
  const { markVisited } = progress;

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
    <div style={{ display: "flex", height: "100%", overflow: "hidden" }}>
      <Sidebar
        course={course}
        activeId={lessonId}
        done={progress.done}
        onOpen={onOpen}
        toc={lesson?.id === lessonId ? toc : []}
        activeHeading={activeHeading}
      />
      <div style={{ flex: 1, minWidth: 0, overflow: "hidden" }}>
        {error ? <Centered>{error}</Centered>
          : !lesson || lesson.id !== lessonId ? <Centered>Loading…</Centered>
          : (
            <LessonView
              lesson={lesson}
              courseTitle={course.title}
              done={progress.done.has(lesson.id)}
              onToggleDone={() => progress.toggleDone(lesson.id)}
              onOpen={onOpen}
              onOpenConcept={onOpenConcept}
              onAsk={onAsk}
              onToc={setToc}
              onActiveHeading={setActiveHeading}
            />
          )}
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
    <nav style={sidebarStyle}>
      <div style={{ padding: "14px 14px 10px", borderBottom: "1px solid #1e1e1e" }}>
        <button onClick={() => onOpen("")} style={linkBtnStyle}>← All courses</button>
        <button onClick={() => onOpen(course.id)} style={{ ...linkBtnStyle, display: "block", color: "#f0f0f0", fontSize: 15, fontWeight: 600, margin: "8px 0 10px" }}>
          {course.title}
        </button>
        <SearchBox value={filter} onChange={setFilter} placeholder="Filter lessons…" small />
      </div>
      <div className="course-scroll" style={{ flex: 1, overflowY: "auto", padding: "6px 0 20px" }}>
        {modules.map((m) => {
          const open = !!f || !collapsed.has(m.id);
          const n = m.lessons.filter((l) => done.has(l.id)).length;
          return (
            <div key={m.id}>
              <button onClick={() => toggle(m.id)} className="course-nav-item" style={moduleHeadStyle}>
                <span style={{ color: "#555", width: 10 }}>{open ? "▾" : "▸"}</span>
                <span style={{ flex: 1 }}>{m.title}</span>
                <span style={{ color: "#555", fontSize: 10 }}>{n}/{m.lessons.length}</span>
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
    <div style={{ paddingBottom: 4 }}>
      {lessons.map((l) => {
        const header = l.section && l.section !== prevSection ? l.section : null;
        prevSection = l.section;
        const active = l.id === activeId;
        const hasToc = active && toc.length > 1;
        return (
          <div key={l.id}>
            {header && <div style={sectionHeadStyle}>{header}</div>}
            <button
              id={`nav-${l.id}`}
              onClick={() => onOpen(l.id)}
              className="course-nav-item"
              style={{
                ...navItemStyle,
                background: active ? "#1f2a36" : "none",
                color: active ? "#90caf9" : "#aaa",
                borderLeft: `2px solid ${active ? "#2196F3" : "transparent"}`,
              }}
            >
              <Check on={done.has(l.id)} small />
              <span style={{ flex: 1 }}>{l.title}</span>
              {hasToc && (
                <span
                  role="button"
                  title={tocOpen ? "Hide page contents" : "Show page contents"}
                  onClick={(e) => { e.stopPropagation(); onToggleToc(); }}
                  style={{ color: "#777", padding: "0 2px" }}
                >
                  {tocOpen ? "▾" : "▸"}
                </span>
              )}
            </button>
            {hasToc && tocOpen && (
              <div style={{ padding: "2px 0 6px" }}>
                {toc.map((t) => (
                  <a key={t.id} href={`#${t.id}`}
                    onClick={(e) => { e.preventDefault(); document.getElementById(t.id)?.scrollIntoView({ behavior: "smooth" }); }}
                    className="course-nav-item"
                    style={{
                      display: "block", fontSize: 11.5, lineHeight: 1.4, padding: "3px 14px 3px",
                      paddingLeft: t.level === 3 ? 60 : 48, textDecoration: "none",
                      color: activeHeading === t.id ? "#90caf9" : "#777",
                    }}>
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
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "#777", fontSize: 14, padding: 24, textAlign: "center" }}>
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
      style={{
        width: "100%", boxSizing: "border-box", background: "#111", border: "1px solid #2a2a2a",
        borderRadius: 6, color: "#e0e0e0", fontSize: small ? 12 : 14, padding: small ? "6px 9px" : "10px 12px",
        outline: "none", fontFamily: "inherit",
      }}
    />
  );
}

function ProgressBar({ value }: { value: number }) {
  return (
    <div style={{ height: 3, background: "#222", borderRadius: 2, marginTop: 8, overflow: "hidden" }}>
      <div style={{ width: `${Math.round(value * 100)}%`, height: "100%", background: "#4CAF50" }} />
    </div>
  );
}

export function Check({ on, small }: { on: boolean; small?: boolean }) {
  const s = small ? 12 : 14;
  return (
    <span style={{
      width: s, height: s, flexShrink: 0, borderRadius: "50%", display: "inline-flex", alignItems: "center", justifyContent: "center",
      border: `1px solid ${on ? "#4CAF50" : "#3a3a3a"}`, background: on ? "#4CAF5033" : "transparent",
      color: "#4CAF50", fontSize: s - 4, lineHeight: 1,
    }}>{on ? "✓" : ""}</span>
  );
}

const cardStyle: React.CSSProperties = {
  textAlign: "left", background: "#161616", border: "1px solid #242424", borderRadius: 10,
  padding: 18, cursor: "pointer", display: "flex", flexDirection: "column", fontFamily: "inherit", minHeight: 160,
};
const hitStyle: React.CSSProperties = {
  display: "block", width: "100%", textAlign: "left", background: "none", border: "none",
  borderBottom: "1px solid #1e1e1e", padding: "10px 8px", cursor: "pointer", fontFamily: "inherit",
};
const linkBtnStyle: React.CSSProperties = {
  background: "none", border: "none", padding: 0, color: "#777", fontSize: 12, cursor: "pointer", fontFamily: "inherit", textAlign: "left",
};
const primaryBtnStyle: React.CSSProperties = {
  background: "#2196F3", border: "none", borderRadius: 6, color: "#fff", fontSize: 13, fontWeight: 600,
  padding: "9px 16px", cursor: "pointer", fontFamily: "inherit",
};
const rowStyle: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 10, width: "100%", textAlign: "left", background: "none",
  border: "none", borderBottom: "1px solid #1c1c1c", padding: "9px 12px", fontSize: 13, cursor: "pointer", fontFamily: "inherit",
};
const kindStyle: React.CSSProperties = {
  fontSize: 10, color: "#FF9800", border: "1px solid #FF980055", borderRadius: 8, padding: "1px 6px",
};
const sidebarStyle: React.CSSProperties = {
  width: 290, flexShrink: 0, borderRight: "1px solid #222", background: "#121212", display: "flex", flexDirection: "column",
};
const moduleHeadStyle: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 6, width: "100%", textAlign: "left", background: "none", border: "none",
  padding: "8px 14px", color: "#ddd", fontSize: 12.5, fontWeight: 600, cursor: "pointer", fontFamily: "inherit",
};
const sectionHeadStyle: React.CSSProperties = {
  fontSize: 10, color: "#555", textTransform: "uppercase", letterSpacing: "0.06em", padding: "8px 14px 2px 32px",
};
const navItemStyle: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: 8, width: "100%", textAlign: "left", border: "none",
  padding: "5px 14px 5px 28px", fontSize: 12.5, lineHeight: 1.4, cursor: "pointer", fontFamily: "inherit", background: "none",
};
