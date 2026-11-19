import { useMemo, useState, type CSSProperties } from "react";
import "./filter.css";
import { useTheme } from "../hooks/useTheme";
import { courseColor, domainColor, tagColor } from "../theme/domains";
import type { Area, Curriculum, CurriculumCourse, CurriculumModule, Facets, Glossary } from "../types";
import { courseFacet, gapFacet, isFacetId, moduleFacet, noteFacet, OUTSIDE_COURSES, termFacet } from "../utils/curriculum";
import type { Grouping } from "../utils/mapRoute";

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
      className={`chip-group${active ? " chip-group--active" : ""}`}
      style={{ "--c": color } as CSSProperties}
    >
      <button
        type="button"
        aria-pressed={active}
        onClick={() => onToggle(id)}
        className={`chip-part${canBrief ? " chip-part--with-brief" : ""}`}
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

interface ModuleRowProps {
  course: CurriculumCourse;
  module: CurriculumModule;
  color: string;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
  onBrief?: (domain: string) => void;
}

/** A module and, opened, its notes in reading order; each note filters the map to the pages it links. */
function ModuleRow({ course, module: m, color, activeTags, onToggle, onBrief }: ModuleRowProps) {
  const notes = m.notes.filter((n) => n.pageIds.length > 0);
  const [open, setOpen] = useState(() => notes.some((n) => activeTags.has(noteFacet(n.id))));
  const mid = moduleFacet(course.id, m.id);
  const mActive = activeTags.has(mid);
  const empty = m.pageIds.length === 0;
  const canOpen = notes.length > 0;
  return (
    <li>
      <div className="cur-row" title={empty ? "No wiki pages cover this yet" : undefined}>
        {canOpen ? (
          <button
            type="button"
            className="cur-toggle"
            aria-expanded={open}
            aria-label={`${open ? "Hide" : "Show"} notes in ${m.title}`}
            onClick={() => setOpen((o) => !o)}
          >
            {open ? "▾" : "▸"}
          </button>
        ) : (
          <span className="cur-toggle" aria-hidden="true" />
        )}
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
      </div>
      {open && (
        <div className="cur-notes">
          {notes.length > 0 && (
            <ul className="cur-modules" aria-label={`Notes in ${m.title}`}>
              {notes.map((n) => {
                const nid = noteFacet(n.id);
                const nActive = activeTags.has(nid);
                return (
                  <li key={n.id} className="cur-row">
                    <button
                      type="button"
                      className="cur-filter cur-note"
                      aria-pressed={nActive}
                      style={nActive ? { color, borderColor: color } : undefined}
                      onClick={() => onToggle(nid)}
                    >
                      <span className="cur-name">{n.title}</span>
                      {n.tier && <span className="cur-tier">{n.tier}</span>}{" "}
                      <span className="cur-count">{n.pageIds.length}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </li>
  );
}

function CourseRow({ course, activeTags, onToggle, onBrief }: CourseRowProps) {
  // Open on the course whose module or note is filtered, so the active row is in sight.
  const [open, setOpen] = useState(() =>
    [...activeTags].some((t) => t.startsWith(`module:${course.id}/`) || t.startsWith(`note:${course.id}/`)),
  );
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
          {course.modules.map((m) => (
            <ModuleRow
              key={m.id}
              course={course}
              module={m}
              color={color}
              activeTags={activeTags}
              onToggle={onToggle}
              onBrief={onBrief}
            />
          ))}
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
          <li className="cur-row cur-outside" title="Pages no lesson links yet">
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

/** Type tags (CLAUDE.md, "Type Tags") say what kind of page it is, not what it is about, so they are not filters here. */
const TYPE_TAGS = new Set(["concept", "pattern", "decision", "project", "comparison", "reference", "conflict", "tombstone"]);
/** Topics listed after the directories before "more": the ones on most pages. */
const TOPIC_LIMIT = 16;

interface Topic {
  /** The facet it filters by: `dir:`, `tag:` or `term:`. */
  id: string;
  label: string;
  count: number;
  color: string;
  /** Directories have a brief; tags and terms do not. */
  brief?: string;
}

/**
 * Wiki topics: the directories (the Wiki ring's sectors) first, largest first, then topic tags and
 * glossary terms as one list by page count. A tag or term named like a directory is the directory,
 * and one on fewer than two pages filters nothing worth a chip.
 */
export function wikiTopics(facets: Facets, glossary: Glossary | null, theme?: ReturnType<typeof useTheme>): { dirs: Topic[]; rest: Topic[] } {
  const dirs: Topic[] = [];
  const seen = new Set<string>();
  for (const [id, pages] of facets) {
    if (!id.startsWith("dir:")) continue;
    const dir = id.slice(4);
    seen.add(dir);
    dirs.push({ id, label: dir, count: pages.size, color: domainColor(dir, theme), brief: dir });
  }
  dirs.sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
  const rest: Topic[] = [];
  for (const [id, pages] of facets) {
    if (!id.startsWith("tag:")) continue;
    const tag = id.slice(4);
    if (TYPE_TAGS.has(tag) || seen.has(tag) || pages.size < 2) continue;
    seen.add(tag);
    rest.push({ id, label: tag, count: pages.size, color: tagColor(tag, theme) });
  }
  for (const t of glossary?.terms ?? []) {
    const count = glossary?.mentions[t.id]?.length ?? 0;
    if (seen.has(t.id) || count < 2) continue;
    seen.add(t.id);
    rest.push({ id: termFacet(t.id), label: t.label, count, color: "var(--concept)" });
  }
  rest.sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
  return { dirs, rest };
}

function TopicFilters({ facets, glossary, activeTags, onToggle, onBrief }: {
  facets: Facets;
  glossary: Glossary | null;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
  onBrief?: (domain: string) => void;
}) {
  const theme = useTheme();
  const [all, setAll] = useState(false);
  const { dirs, rest } = useMemo(() => wikiTopics(facets, glossary, theme), [facets, glossary, theme]);
  const shown = all ? rest : rest.filter((t, i) => i < TOPIC_LIMIT || activeTags.has(t.id));
  return (
    <div className="cur-chips" role="group" aria-label="Wiki topics">
      {[...dirs, ...shown].map((t) => (
        <Chip
          key={t.id}
          id={t.id}
          label={t.label}
          count={t.count}
          color={t.color}
          active={activeTags.has(t.id)}
          onToggle={onToggle}
          briefScope={t.brief}
          onBrief={onBrief}
        />
      ))}
      {rest.length > TOPIC_LIMIT && (
        <button type="button" className="side-more" aria-expanded={all} onClick={() => setAll((o) => !o)}>
          {all ? "fewer" : `+${rest.length - TOPIC_LIMIT} more`}
        </button>
      )}
    </div>
  );
}

/**
 * Modules as chips, one line per course in course order: the course's name (itself a filter), its
 * modules in reading order, then its pages no lesson links yet. Pages in no course close the list.
 */
function ModuleFilters({ curriculum, facets, activeTags, onToggle, onBrief }: {
  curriculum: Curriculum;
  facets: Facets;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
  onBrief?: (scope: string) => void;
}) {
  const theme = useTheme();
  const outside = facets.get(OUTSIDE_COURSES)?.size ?? 0;
  return (
    <div className="mod-filters" role="group" aria-label="Filter by module">
      {curriculum.courses.map((c) => {
        const color = courseColor(c.id, theme);
        const courseId = courseFacet(c.id);
        const gap = facets.get(gapFacet(c.id))?.size ?? 0;
        return (
          <div key={c.id} className="cur-chips mod-course" role="group" aria-label={c.title}>
            <button
              type="button"
              className="mod-course-name"
              aria-pressed={activeTags.has(courseId)}
              style={{ color }}
              onClick={() => onToggle(courseId)}
            >
              {c.title}
            </button>
            {c.modules.map((m) => {
              const id = moduleFacet(c.id, m.id);
              const count = facets.get(id)?.size ?? 0;
              if (!count && !activeTags.has(id)) return null;
              return (
                <Chip
                  key={id}
                  id={id}
                  label={m.title}
                  count={count}
                  color={color}
                  active={activeTags.has(id)}
                  onToggle={onToggle}
                  briefScope={`course/${c.id}/${m.id}`}
                  onBrief={onBrief}
                />
              );
            })}
            {gap > 0 && (
              <Chip id={gapFacet(c.id)} label="not yet in a lesson" count={gap} color="var(--text-soft)" active={activeTags.has(gapFacet(c.id))} onToggle={onToggle} />
            )}
          </div>
        );
      })}
      {outside > 0 && (
        <div className="cur-chips mod-course">
          <Chip id={OUTSIDE_COURSES} label="Not in a course" count={outside} color="var(--text-soft)" active={activeTags.has(OUTSIDE_COURSES)} onToggle={onToggle} />
        </div>
      )}
    </div>
  );
}

/** What an active filter the current view does not list is called. */
function labelOfActive(tag: string, curriculum: Curriculum | null, areas: Area[], glossary: Glossary | null): string {
  if (tag.startsWith("module:")) {
    const [course, module] = tag.slice(7).split("/");
    const m = curriculum?.courses.find((c) => c.id === course)?.modules.find((x) => x.id === module);
    return m?.title ?? module ?? tag;
  }
  if (tag.startsWith("note:")) {
    const id = tag.slice(5);
    for (const c of curriculum?.courses ?? []) {
      for (const m of c.modules) {
        const n = m.notes.find((x) => x.id === id);
        if (n) return `${m.title} › ${n.title}`;
      }
    }
    return id.split("/").pop() ?? id;
  }
  if (tag.startsWith("course:")) return curriculum?.courses.find((c) => c.id === tag.slice(7))?.title ?? tag.slice(7);
  if (tag.startsWith("area:")) return areas.find((a) => a.id === tag.slice(5))?.title ?? tag.slice(5);
  if (tag.startsWith("gap:")) {
    const title = curriculum?.courses.find((c) => c.id === tag.slice(4))?.title ?? areas.find((a) => a.id === tag.slice(4))?.title;
    return `${title ?? tag.slice(4)}: not yet in a lesson`;
  }
  if (tag === OUTSIDE_COURSES) return "Not in a course";
  if (tag.startsWith("beyond:")) return `${tag.slice(7)}: not in a course`;
  if (tag.startsWith("term:")) return glossary?.terms.find((t) => t.id === tag.slice(5))?.label ?? tag.slice(5);
  if (tag.startsWith("dir:") || tag.startsWith("tag:")) return tag.slice(4);
  return tag;
}

/** Whether the view lists this filter itself: the modules in Modules, the topics in Wiki. */
function isListed(tag: string, grouping: Grouping, curriculum: Curriculum | null, topics: Set<string>): boolean {
  if (grouping === "wiki") return topics.has(tag);
  return !!curriculum && (/^(course|module|gap):/.test(tag) || tag === OUTSIDE_COURSES);
}

interface FiltersProps {
  areas: Area[];
  curriculum: Curriculum | null;
  glossary: Glossary | null;
  facets: Facets;
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
  onBrief?: (domain: string) => void;
  /** Modules lists the course modules (the large units); Wiki lists the wiki topics (the small ones). */
  grouping?: Grouping;
}

/**
 * The map's filters, in the Filters popover or inline under the chat. They follow Browse by:
 * Modules lists each course's modules as chips, and its pages no lesson links yet;
 * Wiki lists the wiki topics, the directories then the tags and glossary terms as one set. A filter
 * the view does not list (one set in the other view, or by a link) stays above as a chip.
 */
export function FiltersPanel({ areas, curriculum, glossary, facets, activeTags, onChange, onBrief, grouping = "domain" }: FiltersProps) {
  const theme = useTheme();
  const toggle = (tag: string) => {
    const next = new Set(activeTags);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    onChange(next);
  };
  const topicIds = useMemo(() => {
    const { dirs, rest } = wikiTopics(facets, glossary, theme);
    return new Set([...dirs, ...rest].map((t) => t.id));
  }, [facets, glossary, theme]);
  const unlisted = [...activeTags].filter((t) => !isListed(t, grouping, curriculum, topicIds)).sort();

  return (
    <div className="filters-panel">
      <div className="filters-head">
        <span className="filters-count">{activeTags.size ? `${activeTags.size} active` : "No filter"}</span>
        <button type="button" className="pill-btn" disabled={activeTags.size === 0} onClick={() => onChange(new Set())}>
          Clear
        </button>
      </div>
      {unlisted.length > 0 && (
        <div className="cur-chips" role="group" aria-label="Active filters">
          {unlisted.map((t) => (
            <Chip key={t} id={t} label={labelOfActive(t, curriculum, areas, glossary)} color="var(--accent)" active onToggle={toggle} />
          ))}
        </div>
      )}
      {grouping === "domain" ? (
        <section className="filters-group" aria-label="Modules">
          <span className="panel-label">Modules</span>
          {curriculum ? (
            <ModuleFilters curriculum={curriculum} facets={facets} activeTags={activeTags} onToggle={toggle} onBrief={onBrief} />
          ) : (
            <p className="side-empty">Loading courses…</p>
          )}
        </section>
      ) : (
        <section className="filters-group" aria-label="Wiki topics">
          <span className="panel-label">Wiki topics</span>
          <TopicFilters facets={facets} glossary={glossary} activeTags={activeTags} onToggle={toggle} onBrief={onBrief} />
        </section>
      )}
    </div>
  );
}
