import { useMemo, useState, type ReactNode } from "react";
import { useTheme } from "../hooks/useTheme";
import { areaColor, courseColor, domainColor, tagColor } from "../theme/domains";
import type { Area, Curriculum, CurriculumCourse, Facets, Glossary } from "../types";
import { courseFacet, isFacetId, moduleFacet, OUTSIDE_COURSES, termFacet } from "../utils/curriculum";

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
const TYPE_TAGS = new Set(["concept", "pattern", "decision", "project", "comparison", "reference", "conflict"]);
/** Terms listed before a search narrows them: the most mentioned. */
const TERM_LIMIT = 12;
/** Tags listed before "more", so the popover stays short. */
const TOPIC_LIMIT = 12;

interface FilterProps {
  facets: Facets;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
  onBrief?: (domain: string) => void;
}

const isActive = (tags: Set<string>, prefix: string) => [...tags].some((t) => t.startsWith(prefix));

function Section({ title, children, defaultOpen = true }: { title: string; children: ReactNode; defaultOpen?: boolean }) {
  return (
    <details className="side-section" open={defaultOpen}>
      <summary className="panel-label">{title}</summary>
      <div className="side-section-body">{children}</div>
    </details>
  );
}

/** Wiki directories, largest first, each with a brief. */
function DirectoryFilters({ facets, activeTags, onToggle, onBrief }: FilterProps) {
  useTheme();
  const dirs = [...facets]
    .filter(([id]) => id.startsWith("dir:"))
    .map(([id, pages]) => ({ id, dir: id.slice(4), count: pages.size }))
    .sort((a, b) => b.count - a.count || a.dir.localeCompare(b.dir));
  return (
    <div className="cur-chips" role="group" aria-label="Filter by directory">
      {dirs.map((d) => (
        <Chip
          key={d.id}
          id={d.id}
          label={d.dir}
          count={d.count}
          color={domainColor(d.dir)}
          active={activeTags.has(d.id)}
          onToggle={onToggle}
          briefScope={d.dir}
          onBrief={onBrief}
        />
      ))}
    </div>
  );
}

/** Glossary terms as filters: a term lights the pages that mention it. The most mentioned first. */
function GlossaryFilters({ glossary, activeTags, onToggle }: { glossary: Glossary } & Pick<FilterProps, "activeTags" | "onToggle">) {
  const [query, setQuery] = useState("");
  const terms = useMemo(() => {
    const q = query.trim().toLowerCase();
    const all = glossary.terms
      .map((t) => ({ ...t, pages: glossary.mentions[t.id]?.length ?? 0 }))
      .filter((t) => t.pages > 0);
    const hits = q ? all.filter((t) => t.label.toLowerCase().includes(q) || t.id.includes(q)) : all;
    const ranked = hits.sort((a, b) => b.pages - a.pages || a.label.localeCompare(b.label));
    // Active terms stay listed whatever the search, so they can be switched off.
    const shown = q ? ranked : ranked.slice(0, TERM_LIMIT);
    const active = all.filter((t) => activeTags.has(termFacet(t.id)) && !shown.includes(t));
    return [...active, ...shown];
  }, [glossary, query, activeTags]);

  return (
    <>
      <input
        type="search"
        className="side-search"
        placeholder={`Search ${glossary.terms.length} terms`}
        aria-label="Search glossary terms"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="cur-chips" role="group" aria-label="Glossary terms">
        {terms.map((t) => (
          <Chip
            key={t.id}
            id={termFacet(t.id)}
            label={t.label}
            count={t.pages}
            color="var(--concept)"
            active={activeTags.has(termFacet(t.id))}
            onToggle={onToggle}
          />
        ))}
        {terms.length === 0 && <span className="side-empty">No term matches.</span>}
      </div>
    </>
  );
}

function TopicTagFilters({ facets, activeTags, onToggle }: FilterProps) {
  const theme = useTheme();
  const [all, setAll] = useState(false);
  const tags = useMemo(
    () =>
      [...facets]
        .filter(([id]) => id.startsWith("tag:") && id !== "tag:tombstone" && !TYPE_TAGS.has(id.slice(4)))
        .map(([id, pages]) => ({ id, tag: id.slice(4), count: pages.size }))
        .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag)),
    [facets],
  );
  return (
    <div className="cur-chips" role="group" aria-label="Filter by tag">
      {(all ? tags : tags.filter((r, i) => i < TOPIC_LIMIT || activeTags.has(r.id))).map((r) => (
        <Chip
          key={r.id}
          id={r.id}
          label={r.tag}
          count={r.count}
          color={tagColor(r.tag, theme)}
          active={activeTags.has(r.id)}
          onToggle={onToggle}
        />
      ))}
      {tags.length > TOPIC_LIMIT && (
        <button type="button" className="side-more" aria-expanded={all} onClick={() => setAll((o) => !o)}>
          {all ? "fewer" : `+${tags.length - TOPIC_LIMIT} more`}
        </button>
      )}
    </div>
  );
}

/**
 * Pages no lesson links yet, per course area (and per directory in no area): what the course has
 * still to cover. Shown once the curriculum is in, since a gap is only known against it.
 */
function GapFilters({ areas, facets, activeTags, onToggle }: { areas: Area[] } & FilterProps) {
  useTheme();
  const mapped = new Set(areas.flatMap((a) => a.domains));
  const rows = [
    ...areas.map((a) => ({ id: `gap:${a.id}`, label: a.title, color: areaColor(a.id) })),
    ...[...facets.keys()]
      .filter((id) => id.startsWith("beyond:") && id !== OUTSIDE_COURSES && !mapped.has(id.slice(7)))
      .sort()
      .map((id) => ({ id, label: id.slice(7), color: domainColor(id.slice(7)) })),
  ].filter((r) => (facets.get(r.id)?.size ?? 0) > 0);
  if (!rows.length) return <span className="side-empty">Every page is in a lesson.</span>;
  return (
    <div className="cur-chips" role="group" aria-label="Not yet in a lesson">
      {rows.map((r) => (
        <Chip key={r.id} id={r.id} label={r.label} count={facets.get(r.id)!.size} color={r.color} active={activeTags.has(r.id)} onToggle={onToggle} />
      ))}
    </div>
  );
}

/** What an active filter that no section lists is called: a module, a course or area from a link. */
function labelOfActive(tag: string, curriculum: Curriculum | null, areas: Area[]): string {
  if (tag.startsWith("module:")) {
    const [course, module] = tag.slice(7).split("/");
    const m = curriculum?.courses.find((c) => c.id === course)?.modules.find((x) => x.id === module);
    return m?.title ?? module ?? tag;
  }
  if (tag.startsWith("course:")) return curriculum?.courses.find((c) => c.id === tag.slice(7))?.title ?? tag.slice(7);
  if (tag.startsWith("area:")) return areas.find((a) => a.id === tag.slice(5))?.title ?? tag.slice(5);
  if (tag === OUTSIDE_COURSES) return "Not in a course";
  return tag;
}

const LISTED = /^(dir|tag|term|gap):/;
const isListed = (tag: string) => LISTED.test(tag) || (tag.startsWith("beyond:") && tag !== OUTSIDE_COURSES);

interface FiltersProps {
  areas: Area[];
  curriculum: Curriculum | null;
  glossary: Glossary | null;
  facets: Facets;
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
  onBrief?: (domain: string) => void;
}

/**
 * The map's filters, for the Filters popover: any filter set by a link that nothing below lists
 * (a module, from the topic page), then the pages no lesson links yet, the wiki directories, the
 * glossary terms and the topic tags.
 */
export function FiltersPanel({ areas, curriculum, glossary, facets, activeTags, onChange, onBrief }: FiltersProps) {
  useTheme();
  const toggle = (tag: string) => {
    const next = new Set(activeTags);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    onChange(next);
  };
  const hasTags = [...facets.keys()].some((k) => k.startsWith("tag:"));
  const unlisted = [...activeTags].filter((t) => !isListed(t)).sort();
  const row = { facets, activeTags, onToggle: toggle, onBrief };

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
            <Chip key={t} id={t} label={labelOfActive(t, curriculum, areas)} color="var(--accent)" active onToggle={toggle} />
          ))}
        </div>
      )}
      {curriculum && (
        <Section title="Not yet in a lesson" defaultOpen={isActive(activeTags, "gap:") || isActive(activeTags, "beyond:")}>
          <GapFilters areas={areas} {...row} />
        </Section>
      )}
      <Section title="Directories">
        <DirectoryFilters {...row} />
      </Section>
      {glossary && (
        <Section title="Glossary" defaultOpen={isActive(activeTags, "term:")}>
          <GlossaryFilters glossary={glossary} activeTags={activeTags} onToggle={toggle} />
        </Section>
      )}
      {hasTags && (
        <Section title="Tags" defaultOpen={isActive(activeTags, "tag:")}>
          <TopicTagFilters {...row} />
        </Section>
      )}
    </div>
  );
}
