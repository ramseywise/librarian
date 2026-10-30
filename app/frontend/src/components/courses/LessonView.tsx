import { useEffect, useRef, useState } from "react";
import type { Lesson } from "../../courses/types";
import { Markdown } from "./Markdown";

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

/** A drill's `<details>` solution block, split out so it stays hidden until asked for. */
const SOLUTION_RE = /<details>\s*(?:<summary>[\s\S]*?<\/summary>)?([\s\S]*?)<\/details>/;

function splitSolution(body: string): [string, string, string] | null {
  const m = body.match(SOLUTION_RE);
  if (!m || m.index === undefined) return null;
  return [body.slice(0, m.index), m[1], body.slice(m.index + m[0].length)];
}

export function DrillBadges({ drill }: { drill: NonNullable<Lesson["drill"]> }) {
  const tone = { easy: "#4CAF50", medium: "#FFB74D", hard: "#EF5350" }[drill.difficulty ?? ""] ?? "#888";
  return (
    <span style={{ display: "inline-flex", gap: 8, fontSize: 12, color: "#888" }}>
      <span style={{ color: "#90caf9" }}>{drill.track}</span>
      {drill.difficulty && <span style={{ color: tone }}>{drill.difficulty}</span>}
      {drill.timebox_min && <span>{drill.timebox_min} min</span>}
      {drill.tags?.map((t) => (
        <span key={t} title="Concept with no wiki page yet" style={{ color: "#666" }}>#{t}</span>
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

  // Build the on-page TOC from rendered headings, and track the one in view.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
    const root = proseRef.current;
    if (!root) return;
    const hs = Array.from(root.querySelectorAll<HTMLElement>("h2, h3"));
    onToc(hs.filter((h) => h.id).map((h) => ({ id: h.id, text: h.innerText, level: Number(h.tagName[1]) })));
    onActiveHeading(null);
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length) onActiveHeading(visible[0].target.id);
      },
      { root: scrollRef.current, rootMargin: "0px 0px -70% 0px" }
    );
    hs.forEach((h) => obs.observe(h));
    return () => obs.disconnect();
  }, [lesson.id, onToc, onActiveHeading]);

  const ask = () => onAsk(`I'm studying the lesson "${lesson.title}" (${courseTitle}). Explain its key ideas and how they connect to the rest of the wiki.`);

  return (
    <div ref={scrollRef} className="course-scroll" style={{ height: "100%", overflowY: "auto" }}>
        <article style={{ maxWidth: 780, margin: "0 auto", padding: "28px 32px 60px" }}>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>
            <button onClick={() => onOpen(lesson.course)} style={crumbStyle}>{courseTitle}</button>
            {lesson.section && <> · {lesson.section}</>}
          </div>
          <h1 style={{ color: "#f4f4f4", fontSize: 30, lineHeight: 1.25, margin: "0 0 10px" }}>{lesson.title}</h1>
          {lesson.drill && <div style={{ margin: "-2px 0 12px" }}><DrillBadges drill={lesson.drill} /></div>}
          {lesson.summary && <p style={{ color: "#999", fontSize: 15, margin: "0 0 24px", lineHeight: 1.6 }}>{lesson.summary}</p>}

          <div ref={proseRef} className="lesson-prose">
            {parts ? (
              <>
                {md(parts[0])}
                <button onClick={() => setShowSolution((s) => !s)} style={{ ...doneBtnStyle, margin: "0 0 1em" }}>
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
            <div style={{ marginTop: 36 }}>
              <div style={headStyle}>Concepts in the graph</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {lesson.concepts.map((c) => (
                  <button key={c.id} onClick={() => onOpenConcept(c.id)} title={`${c.domain} · ${c.summary}`} style={conceptStyle}>
                    <span style={{ color: "#ce93d8" }}>◆</span> {c.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "center", gap: 10, margin: "36px 0 24px" }}>
            <button onClick={onToggleDone} style={{ ...doneBtnStyle, ...(done ? doneOnStyle : {}) }}>
              {done ? "✓ Completed" : "Mark as complete"}
            </button>
            <button onClick={ask} style={doneBtnStyle}>Ask the librarian ↗</button>
          </div>

          <div style={{ display: "flex", gap: 12, borderTop: "1px solid #222", paddingTop: 20 }}>
            {lesson.prev ? <PagerLink dir="prev" title={lesson.prev.title} onClick={() => onOpen(lesson.prev!.id)} /> : <span style={{ flex: 1 }} />}
            {lesson.next ? <PagerLink dir="next" title={lesson.next.title} onClick={() => onOpen(lesson.next!.id)} /> : <span style={{ flex: 1 }} />}
          </div>

          <div style={{ fontSize: 11, color: "#444", marginTop: 24, fontFamily: "monospace" }}>
            data/courses/{lesson.id}.md{lesson.source && <> · from {lesson.source}</>}
          </div>
        </article>
    </div>
  );
}

function PagerLink({ dir, title, onClick }: { dir: "prev" | "next"; title: string; onClick: () => void }) {
  return (
    <button onClick={onClick} style={{ ...pagerStyle, textAlign: dir === "next" ? "right" : "left" }}>
      <div style={{ fontSize: 11, color: "#666" }}>{dir === "next" ? "Next →" : "← Previous"}</div>
      <div style={{ fontSize: 14, color: "#90caf9", marginTop: 2 }}>{title}</div>
    </button>
  );
}

const crumbStyle: React.CSSProperties = {
  background: "none", border: "none", padding: 0, color: "#888", cursor: "pointer", fontSize: 12, fontFamily: "inherit",
};
const doneBtnStyle: React.CSSProperties = {
  background: "transparent", border: "1px solid #333", borderRadius: 18, color: "#bbb", fontSize: 13,
  padding: "8px 20px", cursor: "pointer", fontFamily: "inherit",
};
const doneOnStyle: React.CSSProperties = { borderColor: "#4CAF50", color: "#4CAF50", background: "#4CAF5018" };
const pagerStyle: React.CSSProperties = {
  flex: 1, background: "#151515", border: "1px solid #242424", borderRadius: 8, padding: "12px 14px",
  cursor: "pointer", fontFamily: "inherit",
};
const headStyle: React.CSSProperties = {
  fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 8, fontWeight: 600,
};
const conceptStyle: React.CSSProperties = {
  background: "#161616", border: "1px solid #262626", borderRadius: 14, padding: "4px 10px",
  color: "#ccc", fontSize: 12, cursor: "pointer", fontFamily: "inherit",
};
