import { useEffect, useRef, useState } from "react";
import type { Lesson } from "../../courses/types";
import { DrillTimer } from "./DrillTimer";
import { Markdown } from "./Markdown";
import { splitSolution } from "./markdownUtils";

interface Props {
  lesson: Lesson;
  courseTitle: string;
  done: boolean;
  onToggleDone: () => void;
  onOpen: (path: string) => void;
  onOpenConcept: (pageId: string) => void;
  onAsk: (question: string) => void;
  onToc: (toc: TocEntry[]) => void;
  onActiveHeading: (id: string | null) => void;
}

export interface TocEntry { id: string; text: string; level: number }

/** Drop a leading `# Title` when it just repeats the lesson title shown in the header. */
function stripDuplicateH1(body: string, title: string): string {
  const m = body.match(/^\s*#\s+(.+?)\s*\n/);
  if (!m) return body;
  const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "");
  return norm(m[1]) === norm(title) ? body.slice(m[0].length) : body;
}


export function DrillBadges({ drill }: { drill: NonNullable<Lesson["drill"]> }) {
  const tone = ["easy", "medium", "hard"].includes(drill.difficulty ?? "") ? drill.difficulty : "other";
  return (
    <span className="drill-badges">
      <span className="drill-track">{drill.track}</span>
      {drill.difficulty && <span className={`drill-difficulty drill-difficulty--${tone}`}>{drill.difficulty}</span>}
      {drill.timebox_min && <span>{drill.timebox_min} min</span>}
      {drill.tags?.map((t) => (
        <span key={t} title="Concept with no wiki page yet" className="drill-tag">#{t}</span>
      ))}
    </span>
  );
}

export function LessonView({ lesson, courseTitle, done, onToggleDone, onOpen, onOpenConcept, onAsk, onToc, onActiveHeading }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const proseRef = useRef<HTMLDivElement>(null);
  const body = stripDuplicateH1(lesson.body, lesson.title);
  const parts = lesson.kind === "drill" ? splitSolution(body) : null;
  const [showSolution, setShowSolution] = useState(false);
  useEffect(() => setShowSolution(false), [lesson.id]);
  const md = (text: string) => (
    <Markdown body={text} lessonId={lesson.id} onOpenLesson={onOpen} onOpenConcept={onOpenConcept} />
  );

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
  }, [lesson.id]);

  // Build the on-page TOC from rendered headings, and track the one in view. Re-run when
  // the drill solution is shown or hidden, since that adds or removes headings.
  useEffect(() => {
    const root = proseRef.current;
    if (!root) return;
    const hs = Array.from(root.querySelectorAll<HTMLElement>("h2, h3"));
    onToc(hs.filter((h) => h.id).map((h) => ({ id: h.id, text: h.innerText ?? h.textContent ?? "", level: Number(h.tagName[1]) })));
    onActiveHeading(null);
    if (typeof IntersectionObserver === "undefined") return;
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length) onActiveHeading(visible[0].target.id);
      },
      { root: scrollRef.current, rootMargin: "0px 0px -70% 0px" }
    );
    hs.forEach((h) => obs.observe(h));
    return () => obs.disconnect();
  }, [lesson.id, showSolution, onToc, onActiveHeading]);

  const ask = () => onAsk(`I'm studying the lesson "${lesson.title}" (${courseTitle}). Explain its key ideas and how they connect to the rest of the wiki.`);

  return (
    <div ref={scrollRef} className="course-scroll course-page">
        <article className="lesson">
          <div className="lesson-crumbs">
            <button onClick={() => onOpen(lesson.course)} className="link-btn lesson-crumb">{courseTitle}</button>
            {lesson.section && <> · {lesson.section}</>}
          </div>
          <h1 className="lesson-title">{lesson.title}</h1>
          {lesson.drill && (
            <div className="lesson-drill">
              <DrillBadges drill={lesson.drill} />
              {lesson.drill.timebox_min ? <DrillTimer lessonId={lesson.id} timeboxMin={lesson.drill.timebox_min} /> : null}
            </div>
          )}
          {lesson.summary && <p className="lesson-summary">{lesson.summary}</p>}

          <div ref={proseRef} className="lesson-prose">
            {parts ? (
              <>
                {md(parts[0])}
                <button onClick={() => setShowSolution((s) => !s)} aria-expanded={showSolution} className="round-btn lesson-solution-btn">
                  {showSolution ? "Hide solution" : "Show solution"}
                </button>
                {showSolution && md(parts[1])}
                {md(parts[2])}
              </>
            ) : (
              md(body)
            )}
          </div>

          {lesson.concepts.length > 0 && (
            <div className="lesson-concepts">
              <div className="section-label">Concepts in the graph</div>
              <div className="chip-row">
                {lesson.concepts.map((c) => (
                  <button key={c.id} onClick={() => onOpenConcept(c.id)} title={`${c.domain} · ${c.summary}`} className="concept-chip">
                    <span className="text-concept">◆</span> {c.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="lesson-actions">
            <button onClick={onToggleDone} className={`round-btn${done ? " round-btn--done" : ""}`}>
              {done ? "✓ Completed" : "Mark as complete"}
            </button>
            <button onClick={ask} className="round-btn">Ask the librarian ↗</button>
          </div>

          <div className="lesson-pager">
            {lesson.prev ? <PagerLink dir="prev" title={lesson.prev.title} onClick={() => onOpen(lesson.prev!.id)} /> : <span className="grow" />}
            {lesson.next ? <PagerLink dir="next" title={lesson.next.title} onClick={() => onOpen(lesson.next!.id)} /> : <span className="grow" />}
          </div>

          <div className="lesson-source">
            data/courses/{lesson.id}.md{lesson.source && <> · from {lesson.source}</>}
          </div>
        </article>
    </div>
  );
}

function PagerLink({ dir, title, onClick }: { dir: "prev" | "next"; title: string; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`pager-link pager-link--${dir}`}>
      <div className="pager-link-dir">{dir === "next" ? "Next →" : "← Previous"}</div>
      <div className="pager-link-title">{title}</div>
    </button>
  );
}
