import { useCallback, useEffect, useState } from "react";
import type { Course, CourseModule, Deck, Lesson, LessonOutline, SearchHit, SlideDeck } from "./types";
import { SlideFrame } from "./SlideFrame";
import { courseColor } from "../../theme/domains";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { useCourses, useLabs, useStudyProgress } from "../../hooks/useCourses";
import { Check } from "./Check";
import { LessonView, stripDuplicateH1, type TocEntry } from "./LessonView";
import { Markdown } from "./Markdown";
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

  if (!route || !course) {
    return <Catalog courses={courses} done={progress.done} onOpen={open} />;
  }
  if (!route.includes("/")) {
    return <Overview course={course} done={progress.done} last={progress.last[course.id]} onOpen={open} onOpenConcept={onOpenConcept} />;
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

/** A course readme as its page shows it: the lead and "What it is" above the modules, each module group's own
 * section (its syllabus table) under that group's cards, and the rest below. The outcomes and the per-module
 * units are dropped, because the page lists the outcomes itself and each module's page holds its unit. */
function splitCourseReadme(lesson: Lesson): { intro: string; groups: Record<string, string>; rest: string } {
  const [lead, ...sections] = stripDuplicateH1(lesson.body, lesson.title).split(/^(?=## )/m);
  const groups: Record<string, string> = {};
  let intro = lead;
  let rest = "";
  for (const section of sections) {
    const heading = section.match(/^## (.*)/)?.[1].trim() ?? "";
    const body = section.replace(/^## .*\n/, "");
    const group = heading.match(/^(core|advanced)\b/i)?.[1].toLowerCase();
    if (group) groups[group] = body;
    else if (/^what it is$/i.test(heading)) intro += body;
    else if (!/^(course outcomes|units)$/i.test(heading)) rest += section;
  }
  return { intro, groups, rest };
}

/** One course, opening on its readme: what the course is, what you will be able to do, then a card per module
 * in reading order (core before advanced when the course sorts them) with that group's syllabus under it, the
 * rest of the readme, and its references. */
function Overview({ course, done, last, onOpen, onOpenConcept }: {
  course: Course; done: Set<string>; last?: string; onOpen: (p: string) => void; onOpenConcept: (id: string) => void;
}) {
  const { data: labsData } = useLabs();
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

// ---------------------------------------------------------------------------
// Module page: the topic page
// ---------------------------------------------------------------------------

/** The module's readme, which is the body of its page. Null while it loads and when the module has none. */
function useOverview(lessonId: string | null): Lesson | null {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  useEffect(() => {
    if (!lessonId) return;
    let cancelled = false;
    apiFetch(`/api/courses/lessons/${lessonId}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((l: Lesson | null) => !cancelled && setLesson(l))
      .catch(() => undefined);
    return () => { cancelled = true; };
  }, [lessonId]);
  return lesson?.id === lessonId ? lesson : null;
}

/** A readme as the page shows it: the lead above the lecture, the rest below it. The readme's own "Lecture"
 * and "Next" sections say what the page's lecture card and its closing "What's next" already say, so they are dropped. */
function splitOverview(lesson: Lesson): { lead: string; rest: string } {
  const body = stripDuplicateH1(lesson.body, lesson.title);
  const at = body.search(/^## /m);
  if (at < 0) return { lead: body, rest: "" };
  return { lead: body.slice(0, at), rest: body.slice(at).replace(/^## (Lecture|Next)\s*\n[\s\S]*?(?=^## |(?![\s\S]))/gm, "") };
}

/** The syllabus row a note is studied in ("1. Load"), read off the readme's table. */
function submoduleOf(body: string, noteId: string): string | null {
  const slug = noteId.split("/").pop() ?? "";
  const row = body.split("\n").find((line) => line.startsWith("| **") && new RegExp(`/${slug}(\\.md)?[)#]`).test(line));
  return row?.match(/^\| \*\*(.+?):?\*\*/)?.[1] ?? null;
}

/** A lecture as a card: its first slide as a preview, and one button that opens it. */
function DeckCard({ deck, course, whole }: { deck: Deck; course: string; whole: boolean }) {
  const [slides, setSlides] = useState<SlideDeck | null>(null);
  useEffect(() => {
    let cancelled = false;
    apiFetch(`/api/courses/slides/${deck.id}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d: SlideDeck | null) => !cancelled && setSlides(d))
      .catch(() => undefined);
    return () => { cancelled = true; };
  }, [deck.id]);
  const first = slides?.id === deck.id ? slides.frames?.[0] : undefined;
  const count = slides?.id === deck.id ? (slides.frames?.length || slides.slides.length) : 0;
  return (
    <div className="deck-card">
      <a href={`#/slides/${deck.id}`} className="deck-card-peek" aria-hidden="true" tabIndex={-1}>
        {first && <SlideFrame frame={first} total={count} courseColor={courseColor(course)} />}
      </a>
      <div className="deck-card-text">
        <span className="deck-card-kind">{whole ? "Overview lecture" : "Lecture"}{count ? ` · ${count} slides` : ""}</span>
        <span className="deck-card-title">{deck.title}</span>
        {deck.subtitle && <span className="deck-card-sub">{deck.subtitle}</span>}
        <a href={`#/slides/${deck.id}`} className="btn-primary deck-card-open" aria-label={deck.title}>Open the lecture</a>
      </div>
    </div>
  );
}

/** One topic, opening on its lecture and its readme (what the module teaches and its syllabus), then everything it
 * has in the order it is used: test yourself (the three levels, with how far you are), the notes in reading order,
 * hands-on (labs, practice files and drills), the wiki pages its lessons cite, its references, and the module
 * that follows. A part the module lacks says so. */
function ModulePage({ course, module: m, done, onOpen, onOpenConcept }: {
  course: Course; module: CourseModule; done: Set<string>; onOpen: (p: string) => void; onOpenConcept: (id: string) => void;
}) {
  const { data: labsData } = useLabs();
  const { data: studyProgress } = useStudyProgress();
  const id = `${course.id}/${m.id}`;
  const labs = (labsData?.labs ?? []).filter((l) => l.course === course.id && l.module === m.id);
  const readme = m.lessons.find((l) => l.id === `${id}/readme`);
  const overview = useOverview(readme?.id ?? null);
  const references = m.lessons.find((l) => l.id === `${id}/references`);
  const isPractice = (l: LessonOutline) => l.kind === "notebook" || l.id.startsWith(`${id}/practice/`);
  const notes = m.lessons.filter((l) => l.kind !== "drill" && l !== readme && l !== references && !isPractice(l));
  // A notebook or practice file a lab already opens is listed once, as the lab.
  const practice = m.lessons.filter((l) => isPractice(l)
    && !labs.some((lab) => lab.id.replace(/\.md$/, "") === l.id || l.id.startsWith(`${lab.id}/`)));
  const drills = m.lessons.filter((l) => l.kind === "drill");
  const following = course.modules[course.modules.indexOf(m) + 1];
  // A readme with a syllabus states the objectives row by row, so the module's own list would repeat it.
  const { lead, rest } = overview ? splitOverview(overview) : { lead: "", rest: "" };
  const prose = (body: string) => overview && (
    <Markdown body={body} lessonId={overview.id} onOpenLesson={onOpen} onOpenConcept={onOpenConcept} sourceLinks={overview.sourceLinks} />
  );
  const hasSyllabus = overview ? /^## Syllabus\s*$/m.test(overview.body) : !!readme;
  const next = notes.find((l) => !done.has(l.id));
  const step = overview && next ? submoduleOf(overview.body, next.id) : null;
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
        {lead.trim() ? <div className="lesson-prose course-module-lead">{prose(lead)}</div>
          : m.summary && <p className="course-overview-summary">{m.summary}</p>}

        <h2 className="section-label course-module-label">Lecture</h2>
        {m.decks?.length ? (
          <div className="deck-cards">
            {m.decks.map((d) => <DeckCard key={d.id} deck={d} course={course.id} whole={d.id === id} />)}
          </div>
        ) : <p className="course-none">No lecture deck yet.</p>}

        {m.objectives?.length && !hasSyllabus ? (
          <>
            <h2 className="section-label course-module-label">After this module you can</h2>
            <ol className="course-objectives">
              {m.objectives.map((o) => <li key={o}>{o}</li>)}
            </ol>
          </>
        ) : null}

        {rest.trim() && <div className="lesson-prose course-module-overview">{prose(rest)}</div>}

        <h2 className="section-label course-module-label">Test yourself</h2>
        {(m.quizCount || m.flashcardCount || m.problemCount) ? (
          <StudyLevels id={id} quizCount={m.quizCount} flashcardCount={m.flashcardCount} problemCount={m.problemCount} progress={progress} />
        ) : <p className="course-none">No questions or flashcards yet.</p>}

        <h2 className="section-label course-module-label">Notes</h2>
        {notes.length === 0 ? <p className="course-none">No notes yet.</p> : (
          <div className="course-module-list">
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

        {/* A syllabus links each step's labs and sources, so the page does not list them again. */}
        {!hasSyllabus && (
          <>
          <h2 className="section-label course-module-label">Hands-on</h2>
          {labs.length > 0 || practice.length > 0 || drills.length > 0 ? (
            <div className="course-module-list">
              {labs.map((lab) => (
                <div key={lab.id} className="course-row course-row--stack">
                  <a href={`#/labs/${lab.id}`} className="course-row-title">{lab.title}</a>
                  <span className="course-row-section">{lab.purpose}</span>
                </div>
              ))}
              {practice.map((l) => (
                <div key={l.id} className="course-row">
                  <a href={`#/courses/${l.id}`} className="course-row-title">{l.title}</a>
                  <span className="course-row-section">{l.kind === "notebook" ? "Notebook" : "Practice"}</span>
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

          {(!!references || m.references?.length > 0 || m.readings?.length > 0 || !!m.readingsCount) && (
            <>
              <h2 className="section-label course-module-label">References</h2>
              {references && (
                <div className="course-module-list">
                  <div className="course-row course-row--stack">
                    <a href={`#/courses/${references.id}`} className="course-row-title">References</a>
                    <span className="course-row-section">{references.summary || "The books, papers and courses behind this module"}</span>
                  </div>
                </div>
              )}
              <SourceList label="Readings" items={m.readings} count={m.readingsCount} />
              <SourceList label="Reference material (not imported)" items={m.references} />
            </>
          )}
          </>
        )}

        <h2 className="section-label course-module-label">What's next</h2>
        <div className="course-next">
          {next ? (
            <a href={`#/courses/${next.id}`} className="btn-primary course-next-go">
              {done.size && notes.some((l) => done.has(l.id)) ? "Continue" : "Start"}: {next.title}
            </a>
          ) : following ? (
            <a href={`#/courses/${course.id}/${following.id}`} className="btn-primary course-next-go">Next module: {following.title}</a>
          ) : null}
          {next && step && <span className="course-next-step">Submodule {step}</span>}
          {next && following && (
            <span className="course-next-after">Then: <a href={`#/courses/${course.id}/${following.id}`}>{following.title}</a></span>
          )}
        </div>
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
