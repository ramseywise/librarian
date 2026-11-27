import "../card.css";
import { useConceptLessons } from "../../hooks/useConceptLessons";
import { useTheme } from "../../hooks/useTheme";
import type { PageOrigin } from "../../schemas/graph";
import { tagColor } from "../../theme/domains";
import type { RelatedPages } from "../NodeDetailPanel";
import { wikiNoteHref, type AtlasPageInfo } from "./atlasText";

interface Props {
  pageId: string;
  /** The page's links grouped by kind ("Builds on", "Leads to", …), best-linked first. */
  related: RelatedPages[];
  /** The pages closest to this one by embedding, best first. */
  similar?: { id: string; title: string; score: number }[];
  /** Where the note lives and what it came from. */
  page?: AtlasPageInfo;
  tags: string[];
  activeTags?: Set<string>;
  /** Moves the atlas selection to a page; never leaves the atlas. */
  onSelect: (pageId: string) => void;
  onTagClick?: (tag: string) => void;
  colorOf: (pageId: string) => string;
}

const LESSONS = 6;
const ORIGIN_LABEL: Record<PageOrigin["links"][number]["kind"], string> = { arxiv: "arXiv", pdf: "PDF", web: "Source" };
// Everything that leaves the app opens beside it, so the card stays where it was.
const NEW_TAB = { target: "_blank", rel: "noopener noreferrer" } as const;

/**
 * What a selected page is, where it came from, what it links to, and where it is taught.
 * Page links move the atlas selection; the note, its sources and its lessons open in a new tab.
 */
export function AtlasPageDetail({ pageId, related, similar = [], page, tags, activeTags, onSelect, onTagClick, colorOf }: Props) {
  const lessons = useConceptLessons(pageId);
  const theme = useTheme();
  const origins = page?.origins ?? [];
  const unlinked = Math.max(0, (page?.sourceCount ?? 0) - origins.length);
  const rows = [
    ...related.flatMap((g) => g.pages.map((p) => ({ id: p.id, title: p.title, key: g.label.toLowerCase() }))),
    ...similar.map((p) => ({ id: p.id, title: p.title, key: `sim ${p.score.toFixed(2)}` })),
  ];
  const moreLinked = related.reduce((n, g) => n + g.more, 0);
  const practice = lessons.reduce((n, l) => n + (l.flashcardCount ?? 0) + (l.quizCount ?? 0) + (l.problemCount ?? 0), 0);

  return (
    <div className="atlas-detail">
      {(page?.path || origins.length > 0 || unlinked > 0) && (
        <div className="atlas-detail-group">
          <div className="panel-label reading-sub">Read</div>
          {page?.path && (
            <a className="reading-link atlas-out" href={wikiNoteHref(page.path)} {...NEW_TAB}>
              Wiki note ↗
            </a>
          )}
          {origins.length > 0 && (
            <ul className="reading-list atlas-rows">
              {origins.map((o) => (
                <li key={o.links[0].href} className="atlas-row">
                  <span className="atlas-row-key">
                    {o.links.map((l) => (
                      <a key={l.href} className="atlas-out" href={l.href} {...NEW_TAB} aria-label={`${o.title} (${ORIGIN_LABEL[l.kind]})`}>
                        {ORIGIN_LABEL[l.kind]}
                      </a>
                    ))}
                  </span>
                  <span className="atlas-row-title">{o.title}</span>
                </li>
              ))}
            </ul>
          )}
          {unlinked > 0 && (
            <div className="detail-more">
              {origins.length ? `+${unlinked} more` : unlinked} {unlinked === 1 ? "source" : "sources"} with no public link
            </div>
          )}
        </div>
      )}

      {rows.length > 0 && (
        <div className="atlas-detail-group">
          <div className="panel-label reading-sub">Links</div>
          <ul className="reading-list atlas-rows">
            {rows.map((r) => (
              <li key={`${r.key}:${r.id}`} className="atlas-row">
                <span className="atlas-row-key">{r.key}</span>
                <button type="button" className="reading-link" onClick={() => onSelect(r.id)}>
                  <span className="cur-dot" style={{ background: colorOf(r.id) }} aria-hidden="true" />
                  {r.title}
                </button>
              </li>
            ))}
          </ul>
          {moreLinked > 0 && <div className="detail-more">+{moreLinked} more linked</div>}
        </div>
      )}

      {lessons.length > 0 && (
        <div className="atlas-detail-group">
          <div className="panel-label reading-sub">
            Learn{practice > 0 && ` · ${practice} practice ${practice === 1 ? "item" : "items"}`}
          </div>
          {lessons.slice(0, LESSONS).map((l) => (
            <a key={l.id} href={`#/courses/${l.id}`} {...NEW_TAB} className="detail-lesson atlas-out">
              <span className="detail-lesson-title">{l.title} ↗</span>
              <span className="detail-lesson-course">{l.course}</span>
            </a>
          ))}
          {lessons.length > LESSONS && <div className="detail-more">+{lessons.length - LESSONS} more</div>}
        </div>
      )}

      {tags.length > 0 && (
        <div className="atlas-detail-tags">
          {tags.map((tag) => {
            const c = tagColor(tag, theme);
            const on = activeTags?.has(tag) ?? false;
            return (
              <button
                key={tag}
                type="button"
                className="tag-chip"
                aria-pressed={onTagClick ? on : undefined}
                onClick={onTagClick ? () => onTagClick(tag) : undefined}
                title={onTagClick ? `Filter the atlas by ${tag}` : undefined}
                style={{
                  background: on ? c + "33" : c + "18",
                  border: `1px solid ${on ? c : c + "44"}`,
                  color: on || theme === "light" ? c : c + "bb",
                  cursor: onTagClick ? "pointer" : "default",
                }}
              >
                {tag}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
