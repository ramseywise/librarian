import { useMemo, useState, type ReactNode } from "react";
import { useTheme } from "../hooks/useTheme";
import { areaColor, courseColor, domainColor, tagColor } from "../theme/domains";
import type { Area, Curriculum, CurriculumCourse, CurriculumModule, Facets, Glossary } from "../types";
import { areaFacet, beyondFacet, courseFacet, dirFacet, gapFacet, moduleFacet, termFacet } from "../utils/curriculum";
import type { Grouping } from "../utils/mapRoute";
import { Chip } from "./TagFilterPanel";

/** Type tags (CLAUDE.md, "Type Tags") say what kind of page it is, not what it is about, so they are not filters here. */
const TYPE_TAGS = new Set(["concept", "pattern", "decision", "project", "comparison", "reference", "conflict"]);
/** Terms listed before a search narrows them: the most mentioned. */
const TERM_LIMIT = 12;
/** Tags listed before "more", so the sidebar stays short. */
const TOPIC_LIMIT = 12;
/** Pages listed under a module or a gap before "more". */
const PAGE_LIMIT = 30;

interface Props {
  id: string;
  open: boolean;
  /** Which filters the panel lists; on the atlas it also arranges the ring. */
  grouping: Grouping;
  onGrouping: (g: Grouping) => void;
  /** The map's search box. */
  search?: ReactNode;
  /** The ring's area sectors (one per course); a directory in none is listed on its own. */
  areas: Area[];
  curriculum: Curriculum | null;
  glossary: Glossary | null;
  facets: Facets;
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
  onBrief?: (domain: string) => void;
  /** A page's title, for the page rows of the Domain tree. */
  titleOf?: (id: string) => string;
  /** Open a page on the map, from a page row. */
  onOpenPage?: (id: string) => void;
  /** How a focused map is drawn: connections, arrangement, minimap. Absent on the atlas, which draws no lines. */
  map?: ReactNode;
}

function Section({ title, children, defaultOpen = true }: { title: string; children: ReactNode; defaultOpen?: boolean }) {
  return (
    <details className="side-section" open={defaultOpen}>
      <summary className="panel-label">{title}</summary>
      <div className="side-section-body">{children}</div>
    </details>
  );
}

const isActive = (tags: Set<string>, prefix: string) => [...tags].some((t) => t.startsWith(prefix));

function Toggle({ open, what, onClick }: { open: boolean; what: string; onClick: () => void }) {
  return (
    <button
      type="button"
      className="cur-toggle"
      aria-expanded={open}
      aria-label={`${open ? "Hide" : "Show"} ${what}`}
      onClick={onClick}
    >
      {open ? "▾" : "▸"}
    </button>
  );
}

/** The leaves of the Domain tree: the pages of a module or a gap, each opening on the map. */
function PageRows({ ids, titleOf, onOpenPage }: { ids: string[]; titleOf: (id: string) => string; onOpenPage?: (id: string) => void }) {
  const [all, setAll] = useState(false);
  const sorted = useMemo(() => [...ids].sort((a, b) => titleOf(a).localeCompare(titleOf(b))), [ids, titleOf]);
  const shown = all ? sorted : sorted.slice(0, PAGE_LIMIT);
  return (
    <ul className="cur-pages">
      {shown.map((id) => (
        <li key={id}>
          <button type="button" className="cur-page" onClick={() => onOpenPage?.(id)} disabled={!onOpenPage}>
            {titleOf(id)}
          </button>
        </li>
      ))}
      {sorted.length > PAGE_LIMIT && (
        <li>
          <button type="button" className="side-more" aria-expanded={all} onClick={() => setAll((o) => !o)}>
            {all ? "fewer" : `+${sorted.length - PAGE_LIMIT} more`}
          </button>
        </li>
      )}
    </ul>
  );
}

interface RowProps {
  facets: Facets;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
  onBrief?: (domain: string) => void;
  titleOf: (id: string) => string;
  onOpenPage?: (id: string) => void;
}

/** A filter row: ▸ toggle, the filter button (dot, name, count), then any actions. */
function FilterRow({ facet, label, count, color, disabled, title, active, onToggle, toggle, actions, className }: {
  facet: string;
  label: string;
  count: number;
  color: string;
  disabled?: boolean;
  title?: string;
  active: boolean;
  onToggle: (id: string) => void;
  toggle?: ReactNode;
  actions?: ReactNode;
  className?: string;
}) {
  return (
    <div className={`cur-row${className ? ` ${className}` : ""}`} title={title}>
      {toggle ?? <span className="cur-toggle" aria-hidden="true" />}
      <button
        type="button"
        className="cur-filter"
        aria-pressed={active}
        disabled={disabled}
        style={active ? { color, borderColor: color } : undefined}
        onClick={() => onToggle(facet)}
      >
        <span className="cur-dot" style={{ background: color }} aria-hidden="true" />
        <span className="cur-name">{label}</span> <span className="cur-count">{count}</span>
      </button>
      {actions}
    </div>
  );
}

/** A course's module: its pages behind a toggle, a link to its lessons, a brief. */
function ModuleRow({ course, module: m, color, facets, activeTags, onToggle, onBrief, titleOf, onOpenPage }: RowProps & {
  course: CurriculumCourse;
  module: CurriculumModule;
  color: string;
}) {
  const [open, setOpen] = useState(false);
  const facet = moduleFacet(course.id, m.id);
  const ids = [...(facets.get(facet) ?? m.pageIds)];
  const empty = ids.length === 0;
  return (
    <li>
      <FilterRow
        facet={facet}
        label={m.title}
        count={ids.length}
        color={color}
        disabled={empty}
        title={empty ? "No wiki pages cover this yet" : undefined}
        active={activeTags.has(facet)}
        onToggle={onToggle}
        toggle={empty ? undefined : <Toggle open={open} what={`pages in ${m.title}`} onClick={() => setOpen((o) => !o)} />}
        actions={
          <>
            {m.firstLesson && (
              <a className="cur-action" href={`#/courses/${m.firstLesson}`} aria-label={`Open lessons for ${m.title}`} title={`Open lessons for ${m.title}`}>
                ▤
              </a>
            )}
            {onBrief && !empty && (
              <button type="button" className="cur-action" aria-label={`Brief me on ${m.title}`} title={`Brief me on ${m.title}`} onClick={() => onBrief(`course/${course.id}/${m.id}`)}>
                ↗
              </button>
            )}
          </>
        }
      />
      {open && <PageRows ids={ids} titleOf={titleOf} onOpenPage={onOpenPage} />}
    </li>
  );
}

/** Pages of a sector no lesson links yet: what its course has still to cover. */
function GapRow({ facet, color, facets, activeTags, onToggle, titleOf, onOpenPage }: RowProps & { facet: string; color: string }) {
  const [open, setOpen] = useState(false);
  const ids = [...(facets.get(facet) ?? [])];
  if (!ids.length) return null;
  return (
    <li>
      <FilterRow
        facet={facet}
        label="Not yet in a lesson"
        count={ids.length}
        color={color}
        className="cur-gap"
        active={activeTags.has(facet)}
        onToggle={onToggle}
        toggle={<Toggle open={open} what="pages not yet in a lesson" onClick={() => setOpen((o) => !o)} />}
      />
      {open && <PageRows ids={ids} titleOf={titleOf} onOpenPage={onOpenPage} />}
    </li>
  );
}

/**
 * A course row: the area's pages (every page in its directories) as the filter, and under the
 * toggle the course's modules and its gap. A course with no area (no directory of its own)
 * filters by the pages its lessons link.
 */
function CourseRow({ area, course, curriculum, ...row }: RowProps & {
  area: Area | null;
  course: CurriculumCourse | null;
  curriculum: Curriculum | null;
}) {
  const [open, setOpen] = useState(false);
  const { facets, activeTags, onToggle, onBrief } = row;
  const id = area?.id ?? course!.id;
  const label = area?.title ?? course!.title;
  const facet = area && facets.has(areaFacet(area.id)) ? areaFacet(area.id) : courseFacet(id);
  const count = facets.get(facet)?.size ?? course?.pageIds.length ?? 0;
  const color = area ? areaColor(area.id) : courseColor(id);
  const brief = area?.domains[0];
  const modules = course?.modules ?? [];
  return (
    <li>
      <FilterRow
        facet={facet}
        label={label}
        count={count}
        color={color}
        disabled={count === 0}
        active={activeTags.has(facet)}
        onToggle={onToggle}
        toggle={<Toggle open={open} what={`modules in ${label}`} onClick={() => setOpen((o) => !o)} />}
        actions={
          onBrief && brief ? (
            <button type="button" className="cur-action" aria-label={`Brief me on ${label}`} title={`Brief me on ${label}`} onClick={() => onBrief(brief)}>
              ↗
            </button>
          ) : undefined
        }
      />
      {open && (
        <ul className="cur-modules">
          {!curriculum && <li className="side-empty">Loading courses…</li>}
          {modules.map((m) => (
            <ModuleRow key={m.id} course={course!} module={m} color={color} {...row} />
          ))}
          {curriculum && !modules.length && area && <li className="side-empty">No course covers this yet.</li>}
          {curriculum && area && <GapRow facet={gapFacet(area.id)} color={color} {...row} />}
        </ul>
      )}
    </li>
  );
}

/** A wiki directory in no area: its own row, with its pages no lesson links as the gap. */
function LooseDirectoryRow({ dir, curriculum, ...row }: RowProps & { dir: string; curriculum: Curriculum | null }) {
  const [open, setOpen] = useState(false);
  const { facets, activeTags, onToggle, onBrief, titleOf, onOpenPage } = row;
  const facet = dirFacet(dir);
  const ids = [...(facets.get(facet) ?? [])];
  const color = domainColor(dir);
  return (
    <li>
      <FilterRow
        facet={facet}
        label={dir}
        count={ids.length}
        color={color}
        active={activeTags.has(facet)}
        onToggle={onToggle}
        toggle={<Toggle open={open} what={`pages in ${dir}`} onClick={() => setOpen((o) => !o)} />}
        actions={
          onBrief ? (
            <button type="button" className="cur-action" aria-label={`Brief me on ${dir}`} title={`Brief me on ${dir}`} onClick={() => onBrief(dir)}>
              ↗
            </button>
          ) : undefined
        }
      />
      {open && (
        <ul className="cur-modules">
          <li>
            <PageRows ids={ids} titleOf={titleOf} onOpenPage={onOpenPage} />
          </li>
          {curriculum && <GapRow facet={beyondFacet(dir)} color={color} {...row} />}
        </ul>
      )}
    </li>
  );
}

/**
 * Course → module → page. Each course is one of the ring's areas, so its row filters the area's
 * pages (every page in its directories). Under it sit its modules, each opening to the wiki pages
 * its lessons link, and the pages of the area no lesson links yet. Courses with no area and
 * directories in no area follow.
 */
function DomainTree({ areas, curriculum, ...row }: RowProps & { areas: Area[]; curriculum: Curriculum | null }) {
  useTheme();
  const { facets } = row;
  const count = (id: string) => facets.get(id)?.size ?? 0;
  const areaById = new Map(areas.map((a) => [a.id, a]));
  const courseById = new Map((curriculum?.courses ?? []).map((c) => [c.id, c]));
  const present = areas.filter((a) => count(areaFacet(a.id)) > 0);
  const looseCourses = (curriculum?.courses ?? []).filter((c) => !areaById.has(c.id) && c.pageIds.length > 0);
  const mapped = new Set(areas.flatMap((a) => a.domains));
  const looseDirs = [...facets.keys()]
    .filter((id) => id.startsWith("dir:") && !mapped.has(id.slice(4)))
    .map((id) => id.slice(4))
    .sort((a, b) => count(dirFacet(b)) - count(dirFacet(a)) || a.localeCompare(b));

  return (
    <div role="group" aria-label="Filter by domain">
      <ul className="cur-tree">
        {present.map((a) => (
          <CourseRow key={a.id} area={a} course={courseById.get(a.id) ?? null} curriculum={curriculum} {...row} />
        ))}
        {looseCourses.map((c) => (
          <CourseRow key={c.id} area={null} course={c} curriculum={curriculum} {...row} />
        ))}
        {looseDirs.map((d) => (
          <LooseDirectoryRow key={d} dir={d} curriculum={curriculum} {...row} />
        ))}
      </ul>
    </div>
  );
}

/** Wiki directories, largest first, each with a brief. */
function DirectorySection({ facets, activeTags, onToggle, onBrief }: {
  facets: Facets;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
  onBrief?: (domain: string) => void;
}) {
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
function GlossarySection({ glossary, activeTags, onToggle }: {
  glossary: Glossary;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
}) {
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

function TagsSection({ facets, activeTags, onToggle }: {
  facets: Facets;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
}) {
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
 * The map's left column, from under the header down. A Domain / Wiki switch picks the filters:
 * Domain is the tree course → module → page, with each course's "Not yet in a lesson" gap; Wiki
 * is three folding sections, the wiki directories, the glossary terms and the topic tags. Search
 * sits in both; the Map section (connections, arrangement, minimap) only on a focused level,
 * where there is a drawn map to change. Below 760px it is the ☰ drawer.
 */
export function GraphSidebar({
  id,
  open,
  grouping,
  onGrouping,
  search,
  areas,
  curriculum,
  glossary,
  facets,
  activeTags,
  onChange,
  onBrief,
  titleOf = (pageId) => pageId,
  onOpenPage,
  map,
}: Props) {
  const toggle = (tag: string) => {
    const next = new Set(activeTags);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    onChange(next);
  };
  const hasTags = [...facets.keys()].some((k) => k.startsWith("tag:"));

  return (
    <aside id={id} className={`graph-sidebar${open ? " is-open" : ""}`} aria-label="Map filters and connections">
      <div className="side-head">
        <div className="seg" role="group" aria-label="Browse by">
          {(["domain", "wiki"] as const).map((g) => (
            <button key={g} type="button" className="seg-btn" aria-pressed={grouping === g} onClick={() => onGrouping(g)}>
              {g === "domain" ? "Domain" : "Wiki"}
            </button>
          ))}
        </div>
        <button
          type="button"
          className="chip chip--all"
          aria-pressed={activeTags.size === 0}
          onClick={() => onChange(new Set())}
        >
          {activeTags.size ? `Clear (${activeTags.size})` : "All"}
        </button>
      </div>
      {search && <div className="side-search-row">{search}</div>}
      {map && <Section title="Map">{map}</Section>}
      {grouping === "domain" ? (
        <Section title="Domains">
          <DomainTree
            areas={areas}
            curriculum={curriculum}
            facets={facets}
            activeTags={activeTags}
            onToggle={toggle}
            onBrief={onBrief}
            titleOf={titleOf}
            onOpenPage={onOpenPage}
          />
        </Section>
      ) : (
        <>
          <Section title="Directories">
            <DirectorySection facets={facets} activeTags={activeTags} onToggle={toggle} onBrief={onBrief} />
          </Section>
          {glossary && (
            <Section title="Glossary" defaultOpen={isActive(activeTags, "term:")}>
              <GlossarySection glossary={glossary} activeTags={activeTags} onToggle={toggle} />
            </Section>
          )}
          {hasTags && (
            <Section title="Tags" defaultOpen={isActive(activeTags, "tag:")}>
              <TagsSection facets={facets} activeTags={activeTags} onToggle={toggle} />
            </Section>
          )}
        </>
      )}
    </aside>
  );
}
