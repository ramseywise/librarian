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
}

interface TocEntry { id: string; text: string; level: number }

/** Drop a leading `# Title` when it just repeats the lesson title shown in the header. */
function stripDuplicateH1(body: string, title: string): string {
  const m = body.match(/^\s*#\s+(.+?)\s*\n/);
  if (!m) return body;
  const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "");
  return norm(m[1]) === norm(title) ? body.slice(m[0].length) : body;
}

export function LessonView({ lesson, courseTitle, done, onToggleDone, onOpen, onOpenConcept, onAsk }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const proseRef = useRef<HTMLDivElement>(null);
  const [toc, setToc] = useState<TocEntry[]>([]);
  const [activeHeading, setActiveHeading] = useState<string | null>(null);
  const body = stripDuplicateH1(lesson.body, lesson.title);

  // Build the on-page TOC from rendered headings, and track the one in view.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
    const root = proseRef.current;
    if (!root) return;
    const hs = Array.from(root.querySelectorAll<HTMLElement>("h2, h3"));
    setToc(hs.filter((h) => h.id).map((h) => ({ id: h.id, text: h.innerText, level: Number(h.tagName[1]) })));
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length) setActiveHeading(visible[0].target.id);
      },
      { root: scrollRef.current, rootMargin: "0px 0px -70% 0px" }
    );
    hs.forEach((h) => obs.observe(h));
    return () => obs.disconnect();
  }, [lesson.id]);

  const ask = () => onAsk(`I'm studying the lesson "${lesson.title}" (${courseTitle}). Explain its key ideas and how they connect to the rest of the wiki.`);

  return (
    <div style={{ display: "flex", height: "100%" }}>
      <div ref={scrollRef} className="course-scroll" style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
        <article style={{ maxWidth: 780, margin: "0 auto", padding: "28px 32px 60px" }}>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>
            <button onClick={() => onOpen(lesson.course)} style={crumbStyle}>{courseTitle}</button>
            {lesson.section && <> · {lesson.section}</>}
          </div>
          <h1 style={{ color: "#f4f4f4", fontSize: 30, lineHeight: 1.25, margin: "0 0 10px" }}>{lesson.title}</h1>
          {lesson.summary && <p style={{ color: "#999", fontSize: 15, margin: "0 0 24px", lineHeight: 1.6 }}>{lesson.summary}</p>}

          <div ref={proseRef} className="lesson-prose">
            <Markdown body={body} lessonId={lesson.id} onOpenLesson={onOpen} onOpenConcept={onOpenConcept} />
          </div>

          <div style={{ display: "flex", justifyContent: "center", margin: "36px 0 24px" }}>
            <button onClick={onToggleDone} style={{ ...doneBtnStyle, ...(done ? doneOnStyle : {}) }}>
              {done ? "✓ Completed" : "Mark as complete"}
            </button>
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

      <aside className="course-scroll" style={asideStyle}>
        {toc.length > 1 && (
          <>
            <div style={asideHeadStyle}>On this page</div>
            {toc.map((t) => (
              <a key={t.id} href={`#${t.id}`}
                onClick={(e) => { e.preventDefault(); document.getElementById(t.id)?.scrollIntoView({ behavior: "smooth" }); }}
                style={{
                  display: "block", fontSize: 12, lineHeight: 1.45, padding: "3px 0", paddingLeft: t.level === 3 ? 12 : 0,
                  color: activeHeading === t.id ? "#90caf9" : "#777", textDecoration: "none",
                }}>
                {t.text}
              </a>
            ))}
          </>
        )}

        {lesson.concepts.length > 0 && (
          <>
            <div style={{ ...asideHeadStyle, marginTop: toc.length > 1 ? 22 : 0 }}>Concepts in the graph</div>
            {lesson.concepts.map((c) => (
              <button key={c.id} onClick={() => onOpenConcept(c.id)} title={c.summary} style={conceptStyle}>
                <span style={{ color: "#ce93d8" }}>◆</span> {c.title}
                <span style={{ display: "block", color: "#555", fontSize: 10, marginLeft: 14 }}>{c.domain}</span>
              </button>
            ))}
          </>
        )}

        <div style={{ ...asideHeadStyle, marginTop: 22 }}>Study</div>
        <button onClick={onToggleDone} style={asideBtnStyle}>{done ? "✓ Completed" : "Mark complete"}</button>
        <button onClick={ask} style={asideBtnStyle}>Ask the librarian ↗</button>
      </aside>
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
const asideStyle: React.CSSProperties = {
  width: 230, flexShrink: 0, borderLeft: "1px solid #1c1c1c", padding: "28px 18px", overflowY: "auto",
};
const asideHeadStyle: React.CSSProperties = {
  fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 8, fontWeight: 600,
};
const conceptStyle: React.CSSProperties = {
  display: "block", width: "100%", textAlign: "left", background: "none", border: "none", padding: "4px 0",
  color: "#ccc", fontSize: 12, cursor: "pointer", fontFamily: "inherit", lineHeight: 1.4,
};
const asideBtnStyle: React.CSSProperties = {
  display: "block", width: "100%", textAlign: "left", background: "#161616", border: "1px solid #262626",
  borderRadius: 6, color: "#bbb", fontSize: 12, padding: "7px 10px", marginBottom: 6, cursor: "pointer", fontFamily: "inherit",
};
