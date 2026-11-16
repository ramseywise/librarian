"""Search results rendered as text for a model or a human (the `search_wiki` tool output)."""

from __future__ import annotations

from pathlib import Path

from librarian.config import get_settings
from librarian.retrieval import corpus, index, ranking, sections
from librarian.retrieval.graph_expansion import expand_one_hop

UNSCOPED_LESSON_LIMIT = 3
# Results that carry their best section in full; the rest show title and summary only.
SECTION_RESULTS = 3

# Degradation reason → what the caller loses. Phrased for a model reading the
# tool output: it should know to widen its query or re-read a page rather than
# treat a thin result set as evidence the wiki has nothing.
_DEGRADED_NOTES = {
    "no_fts": "full-text search is unavailable, so results come from a weaker "
    "substring match and ranking is less reliable",
    "stale_index": "the search index is behind the files on disk, so results may "
    "omit or misquote recent edits",
    "embeddings_unavailable": "the embedding model failed to load, so ranking uses text "
    "matching only",
}


def degraded_notice(degraded: list[str]) -> str:
    """Render a leading warning block for degraded retrieval ('' when healthy)."""
    if not degraded:
        return ""
    notes = [_DEGRADED_NOTES.get(r, r) for r in degraded]
    return "**DEGRADED RETRIEVAL** — " + "; ".join(notes) + ".\n\n"


def cap_section(text: str, max_chars: int | None = None) -> str:
    """`text` cut to at most `max_chars` (setting `section_output_chars`) at a paragraph break.

    A first paragraph longer than the cap is cut at the cap. A cut text ends with a marker,
    so the reader knows to read the section for the rest.
    """
    cap = get_settings().section_output_chars if max_chars is None else max_chars
    if len(text) <= cap:
        return text
    cut = text.rfind("\n\n", 0, cap)
    return (text[:cut] if cut > 0 else text[:cap]).rstrip() + "\n\n[… section continues]"


def section_ref(page_ref: str, heading_path: str) -> str:
    """The `read_page` argument that returns just this section ('' for the page introduction)."""
    return f"{page_ref}#{heading_path.split(sections.PATH_SEP)[-1]}" if heading_path else ""


def best_section_block(page_ref: str, section: tuple[str, str] | None) -> str:
    """A result's best section, rendered under its heading path; '' when there is none."""
    if section is None:
        return ""
    heading_path, text = section
    ref = section_ref(page_ref, heading_path)
    label = heading_path or "Introduction"
    where = f' (`read_page("{ref}")` for this section alone)' if ref else ""
    return f"Best section: {label}{where}\n\n{cap_section(text)}"


def course_lessons_section(query: str) -> str:
    """Best lessons for an unscoped search, kept out of the wiki ranking ('' if none)."""
    if not corpus.COURSES_DIR.is_dir():
        return ""
    rows, _ = ranking.search_rows(
        query, domain=corpus.COURSE_DOMAIN, limit=UNSCOPED_LESSON_LIMIT, tool="search_courses"
    )
    if not rows:
        return ""
    lines = [f"- **{r[1]}** (`{corpus.course_ref(r[0])}`)\n  {r[3]}" for r in rows]
    return (
        f"\n\n---\n\n**Course lessons** (read with read_page; "
        f'search with domain="{corpus.COURSE_DOMAIN}"):\n\n' + "\n".join(lines)
    )


def expansion_section(seed_paths: list[str]) -> str:
    """Render the one-hop typed-relationship neighbourhood of a result set.

    Returns an empty string when nothing is one hop away, so a wiki region with
    no typed annotations degrades to plain search rather than an empty header.
    """
    con = index.open_index()
    try:
        edges = con.execute("SELECT source_path, target_path, relationship FROM edges").fetchall()
        neighbours = expand_one_hop(seed_paths, edges)
        if not neighbours:
            return ""

        meta = {
            path: (title, summary)
            for path, title, summary in con.execute(
                "SELECT path, title, summary FROM pages"
            ).fetchall()
        }
    finally:
        con.close()

    lines = [
        f"- **{meta.get(path, (path, ''))[0]}** (`{path}`) "
        f"— {rel} of `{Path(sorted(seeds)[0]).stem}`\n"
        f"  {meta.get(path, ('', ''))[1]}"
        for path, rel, seeds in neighbours
    ]
    return (
        f"\n\n---\n\n**{len(neighbours)} page(s) one typed hop away** "
        f"(prerequisite-for / extends):\n\n" + "\n".join(lines)
    )


def search_text(query: str, domain: str = "", limit: int = 10, expand: bool = False) -> str:
    """Search the wiki and course lessons, rendered: title, summary, path and a snippet each.

    Leads with a warning line when retrieval ran degraded (full-text search unavailable, or the
    index behind the files on disk).
    """
    in_courses = corpus.is_course_domain(domain)
    # /compact-wiki reads tool="search_wiki" telemetry as evidence about wiki pages.
    tool = "search_courses" if in_courses else "search_wiki"
    rows, degraded = ranking.search_rows(query, domain=domain, limit=limit, tool=tool)
    warning = degraded_notice(degraded)
    lessons = "" if domain else course_lessons_section(query)

    if not rows:
        suffix = f" in domain '{domain}'" if domain else ""
        return f"{warning}No wiki pages found for: {query!r}{suffix}{lessons}"

    table = "course_pages" if in_courses else "pages"
    # A section output cap of 0 switches this off: every result gets the short snippet.
    top = [r[0] for r in rows[:SECTION_RESULTS]] if get_settings().section_output_chars else []
    best = ranking.best_sections(query, top, table)

    results = []
    for path, title, tags, summary, content, backlinks, _score in rows:
        location = (
            f"Page: `{corpus.course_ref(path)}`\nDomain: {corpus.course_domain(path)}\n"
            if in_courses
            else f"Path: `{path}`\nTags: {tags} · Backlinks: {backlinks}\n"
        )
        if path in best:
            ref = corpus.course_ref(path) if in_courses else path
            results.append(
                f"**{title}**\n{location}Summary: {summary}\n" + best_section_block(ref, best[path])
            )
            continue

        lower = content.lower()
        idx = lower.find(query.lower())
        if idx < 0:
            # BM25 matches on stems, so the verbatim phrase may be absent —
            # snippet around the first individual term that does appear
            for term in query.lower().split():
                idx = lower.find(term)
                if idx >= 0:
                    break
        snippet = ""
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(content), idx + 160)
            snippet = content[start:end].replace("\n", " ").strip()

        results.append(
            f"**{title}**\n"
            f"{location}"
            f"Summary: {summary}\n" + (f"Snippet: ...{snippet}..." if snippet else "")
        )

    body = warning + f"Found {len(rows)} result(s):\n\n" + "\n\n---\n\n".join(results)

    if expand:
        body += expansion_section([r[0] for r in rows])

    return body + lessons
