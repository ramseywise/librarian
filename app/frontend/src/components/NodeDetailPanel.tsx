import { useEffect, useState } from "react";
import type { WikiNodeData } from "../types";
import type { LessonOutline } from "../courses/types";
import { domainColor, tagColor } from "../theme/domains";

type ConceptLesson = LessonOutline & { course: string };

const TYPE_LABELS: Record<string, string> = {
  concept: "Concept", pattern: "Pattern", decision: "Decision",
  project: "Project", comparison: "Comparison", reference: "Reference",
};

interface Props {
  nodeId: string;
  data: WikiNodeData;
  highlighted: boolean;
  lastQuery: string;
  onClose: () => void;
  onTagClick?: (tag: string) => void;
  activeTags?: Set<string>;
  onOpenLesson?: (lessonId: string) => void;
}

export function NodeDetailPanel({ nodeId, data, highlighted, lastQuery, onClose, onTagClick, activeTags, onOpenLesson }: Props) {
  const lessons = useConceptLessons(nodeId);
  const color = domainColor(data.domain[0]);
  const fileName = data.path ? String(data.path).split("/").pop() : null;

  return (
    <div className="detail-panel">
      {/* Colour accent bar */}
      <div className="detail-accent" style={{ background: color }} />

      {/* Header */}
      <div className="detail-header">
        <div className="detail-heading">
          <div className="detail-domain" style={{ color }}>
            {(data.domain as string[]).join(" · ")}
            <span className="detail-type">
              {TYPE_LABELS[data.typeTag] ?? data.typeTag}
            </span>
            {data.private && (
              <span className="private-badge private-badge--detail" title="Lives in data/wiki/private/ — local only, never committed">
                private
              </span>
            )}
          </div>
          <div className="detail-title">
            {data.title}
          </div>
        </div>
        <button onClick={onClose} className="detail-close" aria-label="Close">✕</button>
      </div>

      {/* Highlighted badge */}
      {highlighted && lastQuery && (
        <div className="detail-section detail-section--tight">
          <span className="detail-badge" style={{ borderColor: color, color, background: color + "18" }}>
            Referenced while answering: "{lastQuery}"
          </span>
        </div>
      )}

      {/* Summary */}
      {data.summary && (
        <div className="detail-summary">
          {data.summary}
        </div>
      )}

      {/* Tags — all clickable to filter graph */}
      <div className="detail-section detail-tags">
        {(data.tags as string[]).map((tag) => {
          const chipColor = tagColor(tag);
          const isActive = activeTags?.has(tag);
          return (
            <button
              key={tag}
              onClick={onTagClick ? () => onTagClick(tag) : undefined}
              className="tag-chip"
              style={{
                background: isActive ? chipColor + "33" : chipColor + "18",
                border: `1px solid ${isActive ? chipColor : chipColor + "44"}`,
                color: isActive ? chipColor : chipColor + "bb",
                cursor: onTagClick ? "pointer" : "default",
                boxShadow: isActive ? `0 0 6px ${chipColor}55` : "none",
              }}
            >
              {tag}
            </button>
          );
        })}
      </div>

      {/* Course lessons that cover this concept */}
      {lessons.length > 0 && onOpenLesson && (
        <div className="detail-section detail-section--lessons">
          <div className="detail-subhead">
            Lessons
          </div>
          {lessons.slice(0, 6).map((l) => (
            <button key={l.id} onClick={() => onOpenLesson(l.id)} className="detail-lesson">
              <span className="detail-lesson-title">{l.title}</span>
              <span className="detail-lesson-course">{l.course}</span>
            </button>
          ))}
          {lessons.length > 6 && <div className="detail-more">+{lessons.length - 6} more</div>}
        </div>
      )}

      {/* Footer meta */}
      <div className="detail-footer">
        {fileName && (
          <span className="detail-meta detail-meta--file">
            {fileName}
          </span>
        )}
        {data.updated && (
          <span className="detail-meta">
            updated {data.updated}
          </span>
        )}
      </div>
    </div>
  );
}

function useConceptLessons(pageId: string): ConceptLesson[] {
  const [lessons, setLessons] = useState<ConceptLesson[]>([]);
  useEffect(() => {
    let cancelled = false;
    setLessons([]);
    fetch(`/api/courses/concept/${encodeURIComponent(pageId)}`)
      .then((r) => (r.ok ? r.json() : []))
      .then((ls) => !cancelled && setLessons(ls))
      .catch(() => {});
    return () => { cancelled = true; };
  }, [pageId]);
  return lessons;
}
