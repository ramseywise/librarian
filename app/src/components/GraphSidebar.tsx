import { useMemo, useState, type ReactNode } from "react";
import { useTheme } from "../hooks/useTheme";
import { tagColor } from "../theme/domains";
import type { Curriculum, Facets, Glossary } from "../types";
import { termFacet } from "../utils/curriculum";
import { Chip, TagFilterPanel } from "./TagFilterPanel";

/** Type tags (CLAUDE.md, "Type Tags"): one per page, so they get their own row. */
const TYPE_TAGS = new Set(["concept", "pattern", "decision", "project", "comparison", "reference", "conflict"]);
/** Terms listed before a search narrows them: the most mentioned. */
const TERM_LIMIT = 12;
/** Topic tags listed before "more", so layers and the minimap stay in view. */
const TOPIC_LIMIT = 12;

interface Props {
  id: string;
  open: boolean;
  domains: string[];
  curriculum: Curriculum | null;
  glossary: Glossary | null;
  facets: Facets;
  activeTags: Set<string>;
  onChange: (tags: Set<string>) => void;
  onBrief?: (domain: string) => void;
  /** Layer toggles and layout; none on the atlas, which draws neither. */
  layers?: ReactNode;
  /** The canvas minimap; none on the atlas. */
  minimap?: ReactNode;
}

function Section({ title, children, defaultOpen = true }: { title: string; children: ReactNode; defaultOpen?: boolean }) {
  return (
    <details className="side-section" open={defaultOpen}>
      <summary className="panel-label">{title}</summary>
      <div className="side-section-body">{children}</div>
    </details>
  );
}

function TagsSection({ facets, glossary, activeTags, onToggle }: {
  facets: Facets;
  glossary: Glossary | null;
  activeTags: Set<string>;
  onToggle: (id: string) => void;
}) {
  const theme = useTheme();
  const [query, setQuery] = useState("");
  const [allTopics, setAllTopics] = useState(false);
  const { topic, type } = useMemo(() => {
    const rows = [...facets]
      .filter(([id]) => id.startsWith("tag:") && id !== "tag:tombstone")
      .map(([id, pages]) => ({ id, tag: id.slice(4), count: pages.size }))
      .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));
    return { topic: rows.filter((r) => !TYPE_TAGS.has(r.tag)), type: rows.filter((r) => TYPE_TAGS.has(r.tag)) };
  }, [facets]);

  const terms = useMemo(() => {
    if (!glossary) return [];
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

  const chip = (r: { id: string; tag: string; count: number }) => (
    <Chip
      key={r.id}
      id={r.id}
      label={r.tag}
      count={r.count}
      color={tagColor(r.tag, theme)}
      active={activeTags.has(r.id)}
      onToggle={onToggle}
    />
  );

  return (
    <>
      <div className="cur-chips" role="group" aria-label="Topic tags">
        {(allTopics ? topic : topic.filter((r, i) => i < TOPIC_LIMIT || activeTags.has(r.id))).map(chip)}
        {topic.length > TOPIC_LIMIT && (
          <button type="button" className="side-more" aria-expanded={allTopics} onClick={() => setAllTopics((o) => !o)}>
            {allTopics ? "fewer" : `+${topic.length - TOPIC_LIMIT} more`}
          </button>
        )}
      </div>
      <div className="panel-label side-sublabel">Type</div>
      <div className="cur-chips" role="group" aria-label="Type tags">{type.map(chip)}</div>
      {glossary && (
        <>
          <div className="panel-label side-sublabel">Glossary terms</div>
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
      )}
    </>
  );
}

/**
 * The map's left column, from under the header down: curriculum, tags (frontmatter tags and
 * glossary terms, all filters), layers and the minimap. Below 760px it is the ☰ drawer.
 */
export function GraphSidebar({
  id,
  open,
  domains,
  curriculum,
  glossary,
  facets,
  activeTags,
  onChange,
  onBrief,
  layers,
  minimap,
}: Props) {
  const toggle = (tag: string) => {
    const next = new Set(activeTags);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    onChange(next);
  };
  const hasTags = [...facets.keys()].some((k) => k.startsWith("tag:"));

  return (
    <aside id={id} className={`graph-sidebar${open ? " is-open" : ""}`} aria-label="Map filters and layers">
      <div className="side-head">
        <span className="side-title">Filters</span>
        <button
          type="button"
          className="chip chip--all"
          aria-pressed={activeTags.size === 0}
          onClick={() => onChange(new Set())}
        >
          {activeTags.size ? `Clear (${activeTags.size})` : "All"}
        </button>
      </div>
      <Section title="Curriculum">
        <TagFilterPanel
          domains={domains}
          curriculum={curriculum}
          activeTags={activeTags}
          onChange={onChange}
          onBrief={onBrief}
        />
      </Section>
      {hasTags && (
        <Section title="Tags">
          <TagsSection facets={facets} glossary={glossary} activeTags={activeTags} onToggle={toggle} />
        </Section>
      )}
      {layers && <Section title="Layers">{layers}</Section>}
      {minimap && (
        <Section title="Minimap">
          <div className="side-minimap">{minimap}</div>
        </Section>
      )}
    </aside>
  );
}
