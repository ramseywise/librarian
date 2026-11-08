import { useState } from "react";
import { useTheme } from "../hooks/useTheme";
import { courseColor, domainColor } from "../theme/domains";
import type { Curriculum, CurriculumCourse } from "../types";
import { courseFacet, isFacetId, moduleFacet, OUTSIDE_COURSES } from "../utils/curriculum";

interface Props {
  /** Curriculum facet; null until it loads. */
  curriculum?: Curriculum | null;
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
  onBrief?: (domain: string) => void;
}

interface ChipProps {
  id: string;
  label: string;
  count?: number;
  color: string;
  active: boolean;
  onToggle: (id: string) => void;
  /** Scope for the ↗ brief; no button without it. */
  briefScope?: string;
  onBrief?: (domain: string) => void;
}

export function Chip({ id, label, count, color, active, onToggle, briefScope, onBrief }: ChipProps) {
  const canBrief = onBrief && briefScope;
  return (
    <div
      role="group"
      aria-label={label}
      className="chip-group"
      style={{
        background: active ? color + "22" : "transparent",
        border: `1px solid ${active ? color : "var(--border-strong)"}`,
      }}
    >
      <button
        type="button"
        aria-pressed={active}
        onClick={() => onToggle(id)}
        className={`chip-part${canBrief ? " chip-part--with-brief" : ""}`}
        style={{ color: active ? color : "var(--text-ghost)" }}
      >
        {label}
        {count != null && " "}
        {count != null && <span className="cur-count">{count}</span>}
      </button>
      {canBrief && (
        <button
          type="button"
          aria-label={`Brief me on ${label}`}
          title={`Brief me on ${label}`}
          onClick={() => onBrief(briefScope)}
          className="chip-part chip-brief"
          style={{ color: active ? color : "var(--text-muted)", background: color + "33" }}
        >
          ↗
        </button>
      )}
    </div>
  );
}

interface CourseRowProps {
  course: CurriculumCourse;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
  onBrief?: (domain: string) => void;
}

function CourseRow({ course, activeTags, onToggle, onBrief }: CourseRowProps) {
  const [open, setOpen] = useState(false);
  useTheme();
  const color = courseColor(course.id);
  const id = courseFacet(course.id);
  const active = activeTags.has(id);
  return (
    <li>
      <div className="cur-row">
        <button
          type="button"
          className="cur-toggle"
          aria-expanded={open}
          aria-label={`${open ? "Hide" : "Show"} modules in ${course.title}`}
          onClick={() => setOpen((o) => !o)}
        >
          {open ? "▾" : "▸"}
        </button>
        <button
          type="button"
          className="cur-filter"
          aria-pressed={active}
          disabled={course.pageIds.length === 0}
          style={active ? { color, borderColor: color } : undefined}
          onClick={() => onToggle(id)}
        >
          <span className="cur-dot" style={{ background: color }} aria-hidden="true" />
          <span className="cur-name">{course.title}</span>{" "}
          <span className="cur-count">{course.pageIds.length}</span>
        </button>
      </div>
      {open && (
        <ul className="cur-modules">
          {course.modules.map((m) => {
            const mid = moduleFacet(course.id, m.id);
            const mActive = activeTags.has(mid);
            const empty = m.pageIds.length === 0;
            return (
              <li key={m.id} className="cur-row" title={empty ? "No wiki pages cover this yet" : undefined}>
                <button
                  type="button"
                  className="cur-filter"
                  aria-pressed={mActive}
                  disabled={empty}
                  style={mActive ? { color, borderColor: color } : undefined}
                  onClick={() => onToggle(mid)}
                >
                  <span className="cur-name">{m.title}</span>{" "}
                  <span className="cur-count">{m.pageIds.length}</span>
                </button>
                {m.firstLesson && (
                  <a
                    className="cur-action"
                    href={`#/courses/${m.firstLesson}`}
                    aria-label={`Open lessons for ${m.title}`}
                    title={`Open lessons for ${m.title}`}
                  >
                    ▤
                  </a>
                )}
                {onBrief && !empty && (
                  <button
                    type="button"
                    className="cur-action"
                    aria-label={`Brief me on ${m.title}`}
                    title={`Brief me on ${m.title}`}
                    onClick={() => onBrief(`course/${course.id}/${m.id}`)}
                  >
                    ↗
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </li>
  );
}

/** The course view of the map sidebar: courses, their modules, and the pages in none. */
export function TagFilterPanel({ curriculum, activeTags, onChange, onBrief }: Props) {
  useTheme(); // Colours below are read at render, so a theme switch has to render this again.
  function toggle(tag: string) {
    const next = new Set(activeTags);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    onChange(next);
  }

  if (!curriculum) return <p className="side-empty">Loading courses…</p>;

  // Ids no section lists (an old link's bare tag): shown so they can be cleared one by one.
  const plainTags = [...activeTags].filter((t) => !isFacetId(t)).sort();
  const outside = curriculum.beyond.reduce((n, b) => n + b.pageIds.length, 0);
  const outsideActive = activeTags.has(OUTSIDE_COURSES);

  return (
    <div className="side-curriculum" role="group" aria-label="Filter by curriculum">
      {plainTags.length > 0 && (
        <div className="cur-chips">
          {plainTags.map((tag) => (
            <Chip key={tag} id={tag} label={tag} color={domainColor(tag)} active onToggle={toggle} />
          ))}
        </div>
      )}
      <ul className="cur-tree">
        {curriculum.courses.map((c) => (
          <CourseRow key={c.id} course={c} activeTags={activeTags} onToggle={toggle} onBrief={onBrief} />
        ))}
        {outside > 0 && (
          <li className="cur-row cur-outside" title="Pages no lesson links yet: mostly build findings in patterns/">
            <button
              type="button"
              className="cur-filter"
              aria-pressed={outsideActive}
              style={outsideActive ? { color: "var(--text)", borderColor: "var(--text-dim)" } : undefined}
              onClick={() => toggle(OUTSIDE_COURSES)}
            >
              <span className="cur-dot" style={{ background: "var(--text-dim)" }} aria-hidden="true" />
              <span className="cur-name">Not in a course</span> <span className="cur-count">{outside}</span>
            </button>
          </li>
        )}
      </ul>
    </div>
  );
}
