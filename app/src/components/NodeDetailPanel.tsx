import type { CSSProperties } from "react";
import "./card.css";
import type { WikiNodeData } from "../types";
import { useTheme } from "../hooks/useTheme";
import { domainColor, tagColor } from "../theme/domains";
import { ReportButton } from "./feedback/ReportButton";
import { useConceptLessons } from "../hooks/useConceptLessons";

const TYPE_LABELS: Record<string, string> = {
  concept: "Concept", pattern: "Pattern", decision: "Decision",
  project: "Project", comparison: "Comparison", reference: "Reference",
};

/** One way pages relate to this one ("Builds on", "Related", …) and the pages that do. */
export interface RelatedPages {
  label: string;
  pages: { id: string; title: string }[];
  more: number;
}

interface Props {
  nodeId: string;
  data: WikiNodeData;
  highlighted: boolean;
  lastQuery: string;
  onClose: () => void;
  onTagClick?: (tag: string) => void;
  activeTags?: Set<string>;
  onOpenLesson?: (lessonId: string) => void;
  /** The page's links, grouped by how they relate; each opens that page's level. */
  related?: RelatedPages[];
  /** Why the page is on this level: what ties it to the page the level is for. */
  why?: string[];
  onOpenPage?: (pageId: string) => void;
}

/** The open card of a page on the canvas: what it is, what it relates to, where it is taught. */
export function NodeDetailPanel({
  nodeId, data, highlighted, lastQuery, onClose, onTagClick, activeTags, onOpenLesson, related, why, onOpenPage,
}: Props) {
  const lessons = useConceptLessons(nodeId);
  const theme = useTheme();
  const color = domainColor(data.domain[0], theme);
  const fileName = data.path ? String(data.path).split("/").pop() : null;

  return (
    <div className="detail-panel" style={{ "--c": color } as CSSProperties}>
      {/* Colour accent bar */}
      <div className="detail-accent" />

      {/* Header */}
      <div className="detail-header">
        <div className="detail-heading">
          <div className="detail-domain">
            {(data.domain as string[]).join(" · ")}
            <span className="detail-type">
              {TYPE_LABELS[data.typeTag] ?? data.typeTag}
            </span>
          </div>
          <div className="detail-title">
            {data.title}
          </div>
        </div>
        <button onClick={onClose} className="detail-close" aria-label="Close">✕</button>
      </div>

      <div className="detail-body">
        {/* Highlighted badge */}
        {highlighted && lastQuery && (
          <div className="detail-section detail-section--tight">
            <span className="detail-badge">
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

        {why && why.length > 0 && <div className="detail-why">Here because: {why.join(" · ")}</div>}

        {/* What it relates to, by kind of link */}
        {related && related.length > 0 && (
          <div className="detail-section detail-related">
            {related.map((group) => (
              <div key={group.label} className="detail-related-group">
                <div className="detail-subhead">{group.label}</div>
                <div className="detail-related-pages">
                  {group.pages.map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      className="detail-related-page"
                      onClick={onOpenPage ? () => onOpenPage(p.id) : undefined}
                      title={`Focus on ${p.title}`}
                    >
                      {p.title}
                    </button>
                  ))}
                  {group.more > 0 && <span className="detail-more">+{group.more} more</span>}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tags — all clickable to filter graph */}
        <div className="detail-section detail-tags">
          {(data.tags as string[]).map((tag) => {
            const chipColor = tagColor(tag, theme);
            const isActive = activeTags?.has(tag);
            return (
              <button
                key={tag}
                onClick={onTagClick ? () => onTagClick(tag) : undefined}
                className="tag-chip"
                style={{
                  background: isActive ? chipColor + "33" : chipColor + "18",
                  border: `1px solid ${isActive ? chipColor : chipColor + "44"}`,
                  // At 73% a darkened light-theme colour would drop under 4.5:1.
                  color: isActive || theme === "light" ? chipColor : chipColor + "bb",
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

        <div className="detail-section">
          <ReportButton key={nodeId} kind="page" target={nodeId} />
        </div>
      </div>

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
