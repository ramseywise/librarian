"""Reading and listing pages: `read_page`, `list_domain`, `list_pages`, `domain_briefing`.

Filesystem operations apart from backlink counts, which come from the index. Every path that
serves page text excludes `data/wiki/private/` here, once, for the MCP tools and the chat agent.
"""

from __future__ import annotations

from pathlib import Path

from librarian.retrieval import corpus, index
from librarian.wiki.common import parse_frontmatter, slugify, text_aliases

# Courses are far bigger than wiki domains: a whole subject is megabytes of context. The
# largest AI Engineering module is under this limit.
COURSE_BRIEFING_MAX_CHARS = 1_000_000


def _pages_formerly_named(slug: str) -> list[Path]:
    """Public pages with `slug` among their aliases. Reads every page, so only after a slug miss."""
    return [
        page
        for page in corpus.wiki_pages()
        if any(slugify(alias) == slug for alias in text_aliases(page.read_text(encoding="utf-8")))
    ]


def _read_lesson(ref: str, not_found: str) -> str:
    """Serve a `course/<relative path>` ref (`.md` optional) from inside the course root only.

    Only COURSES_DIR counts here, so `course/../wiki/...` fails even for a public wiki page.
    """
    # lstrip keeps `course//etc/passwd` relative: an absolute part would replace the root.
    target = corpus.COURSES_DIR / ref.removeprefix(corpus.COURSE_DOMAIN).lstrip("/")
    if target.suffix != ".md":
        target = target.with_name(f"{target.name}.md")
    try:
        inside = target.resolve().is_relative_to(corpus.COURSES_DIR.resolve())
        readable = inside and target.is_file() and not corpus.is_private(target)
    except (OSError, RuntimeError, ValueError):
        readable = False
    if not readable:
        corpus.log_retrieval("read_page", path=ref, found=False, course=True)
        return not_found
    corpus.log_retrieval("read_page", path=str(target), found=True, course=True)
    return target.read_text(encoding="utf-8", errors="replace")


def read_page(path_or_title: str) -> str:
    """Resolve a page by path, wiki-relative path, slug, or title and return its text.

    The single page-read core — the read_page MCP tool and the chat agent both
    call this, so private exclusion and telemetry are enforced in one place.
    Lessons are reached by `course/<relative path>` or by the absolute path search returns.
    Slug and title lookup stays wiki-only: a loose match over 749 lessons would turn a
    clean miss, or a unique wiki match, into a wrong or ambiguous answer.
    """
    # Private pages are indistinguishable from missing ones — a distinct "denied"
    # message would itself confirm the page exists.
    not_found = f"Page not found: {path_or_title!r}. Run search_wiki to find the right path."

    if corpus.is_course_domain(path_or_title):
        return _read_lesson(path_or_title, not_found)

    wiki_dir = corpus.WIKI_DIR
    candidate = Path(path_or_title)
    if candidate.exists():
        resolved = candidate.resolve()
        if resolved.is_relative_to(corpus.COURSES_DIR.resolve()):
            ref = (
                f"{corpus.COURSE_DOMAIN}/"
                f"{resolved.relative_to(corpus.COURSES_DIR.resolve()).as_posix()}"
            )
            return _read_lesson(ref, not_found)
        if not resolved.is_relative_to(wiki_dir.resolve()):
            corpus.log_retrieval("read_page", path=str(candidate), found=False, outside_wiki=True)
            return not_found
        if corpus.is_private(candidate):
            corpus.log_retrieval("read_page", path=str(candidate), found=False, private=True)
            return not_found
        corpus.log_retrieval("read_page", path=str(candidate), found=True)
        return candidate.read_text(encoding="utf-8")

    wiki_candidate = wiki_dir / path_or_title
    if wiki_candidate.exists():
        if not wiki_candidate.resolve().is_relative_to(wiki_dir.resolve()):
            corpus.log_retrieval(
                "read_page", path=str(wiki_candidate), found=False, outside_wiki=True
            )
            return not_found
        if corpus.is_private(wiki_candidate):
            corpus.log_retrieval("read_page", path=str(wiki_candidate), found=False, private=True)
            return not_found
        corpus.log_retrieval("read_page", path=str(wiki_candidate), found=True)
        return wiki_candidate.read_text(encoding="utf-8")

    slug = slugify(path_or_title)
    matches = [p for p in wiki_dir.rglob(f"*{slug}*.md") if not corpus.is_private(p)]
    if not matches:
        matches = _pages_formerly_named(slug)
    if not matches:
        words = path_or_title.lower().split()
        for word in words:
            matches = [p for p in wiki_dir.rglob(f"*{word}*.md") if not corpus.is_private(p)]
            if matches:
                break

    if not matches:
        corpus.log_retrieval("read_page", path=path_or_title, found=False)
        return not_found

    if len(matches) == 1:
        corpus.log_retrieval("read_page", path=str(matches[0]), found=True)
        return matches[0].read_text(encoding="utf-8")

    corpus.log_retrieval(
        "read_page", path=path_or_title, found=False, ambiguous=True, n_matches=len(matches)
    )
    paths = "\n".join(f"  - {m}" for m in matches[:10])
    return f"Multiple pages match {path_or_title!r}. Be more specific:\n{paths}"


def _unknown_domain(domain: str) -> str:
    valid = ", ".join(corpus.wiki_domains() + corpus.course_domains())
    return f"Unknown domain: {domain!r}. Valid domains: {valid}"


def _frontmatter_of(path: Path) -> dict:
    """Frontmatter of a page, {} when the file is absent."""
    if not path.is_file():
        return {}
    return parse_frontmatter(path.read_text(encoding="utf-8", errors="ignore"))


def _course_line(page: Path) -> str:
    meta = _frontmatter_of(page)
    return (
        f"- **{meta.get('title', page.stem)}** (`{corpus.course_ref(page)}`)\n"
        f"  {meta.get('summary', '')}"
    )


def _list_course_domain(domain: str) -> str:
    """Courses for `course`, modules for `course/<subject>`, lessons for anything deeper."""
    root = corpus.resolve_course_dir(domain)
    if root is None:
        return _unknown_domain(domain)
    depth = len(root.relative_to(corpus.COURSES_DIR).parts)
    label = (
        f"{corpus.COURSE_DOMAIN}/{root.relative_to(corpus.COURSES_DIR).as_posix()}"
        if depth
        else corpus.COURSE_DOMAIN
    )

    if depth < 2:
        meta_file = "_module.md" if depth else "_course.md"
        kind = "module" if depth else "course"
        lines = []
        for child in sorted(d for d in root.iterdir() if d.is_dir()):
            n_lessons = len(corpus.course_pages(child))
            if not n_lessons:
                continue
            meta = _frontmatter_of(child / meta_file)
            lines.append(
                f"- **{meta.get('title', child.name)}** (`{label}/{child.name}`) · "
                f"{n_lessons} lesson(s)\n  {meta.get('summary', '')}"
            )
        corpus.log_retrieval("list_domain", domain=domain, n_results=len(lines))
        if not lines:
            return f"No pages found in domain '{domain}'"
        return f"**{len(lines)} {kind}(s) in `{label}`**:\n\n" + "\n".join(lines)

    lessons = sorted(corpus.course_pages(root))
    corpus.log_retrieval("list_domain", domain=domain, n_results=len(lessons))
    if not lessons:
        return f"No pages found in domain '{domain}'"
    lines = [_course_line(p) for p in lessons]
    return f"**{len(lines)} lesson(s) in `{label}`**:\n\n" + "\n".join(lines)


def _backlink_counts() -> dict[str, int]:
    """Backlink count per indexed page path; {} when the index cannot be read."""
    con = index.open_index()
    bl_map: dict[str, int] = {}
    try:
        for path, bl in con.execute("SELECT path, backlinks FROM pages").fetchall():
            bl_map[path] = bl
    except Exception:
        pass
    finally:
        con.close()
    return bl_map


def list_domain(domain: str) -> str:
    """List all pages in a domain directory, ordered by backlink count.

    Filesystem listing plus backlink counts from the index. `course` lists the courses,
    `course/<subject>` its modules, `course/<subject>/<module>` its lessons.
    """
    if corpus.is_course_domain(domain):
        return _list_course_domain(domain)

    domain_dir = corpus.resolve_domain_dir(domain)
    if domain_dir is None:
        return _unknown_domain(domain)

    pages = sorted(p for p in domain_dir.glob("*.md") if not p.name.startswith("_"))
    if not pages:
        return f"No pages found in domain '{domain}'"

    bl_map = _backlink_counts()

    results = []
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = parse_frontmatter(text)
        page_tags = meta.get("tags", [])
        bl = bl_map.get(str(page), 0)
        results.append(
            (
                bl,
                (
                    f"- **{meta.get('title', page.stem)}** (`{page}`) · ↑{bl} backlinks\n"
                    f"  Tags: {', '.join(page_tags) or 'none'}\n"
                    f"  {meta.get('summary', '')}"
                ),
            )
        )

    results.sort(key=lambda x: x[0], reverse=True)
    corpus.log_retrieval("list_domain", domain=domain, n_results=len(results))
    header = f"**{len(results)} page(s) in `data/wiki/{domain}/`** (sorted by backlinks):\n\n"
    return header + "\n".join(r[1] for r in results)


def list_pages(tag: str = "", directory: str = "") -> str:
    """List wiki pages and course lessons, optionally filtered by tag or directory.

    Raises ValueError for a `directory` that is absolute or climbs out of the wiki.
    """
    wiki_dir = corpus.WIKI_DIR
    lessons: list[Path] = []
    if directory:
        if ".." in directory or directory.startswith("/"):
            raise ValueError(f"Invalid directory: {directory!r}")
        search_dir = wiki_dir / directory
        if not search_dir.resolve().is_relative_to(wiki_dir.resolve()):
            raise ValueError(f"Directory escapes wiki root: {directory!r}")
    else:
        search_dir = wiki_dir
        lessons = corpus.course_pages()
    pages = [
        p
        for p in search_dir.rglob("*.md")
        if not p.name.startswith("_") and not corpus.is_private(p)
    ]
    if directory and corpus.is_course_domain(directory):
        course_dir = corpus.resolve_course_dir(directory)
        lessons = corpus.course_pages(course_dir) if course_dir else []
        pages = []

    bl_map = _backlink_counts()

    results = []
    for page in sorted(pages):
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = parse_frontmatter(text)
        page_tags = meta.get("tags", [])

        if tag and tag not in page_tags:
            continue

        bl = bl_map.get(str(page), 0)
        results.append(
            f"- **{meta.get('title', page.stem)}** (`{page}`) · ↑{bl}\n"
            f"  Tags: {', '.join(page_tags) or 'none'}\n"
            f"  {meta.get('summary', '')}"
        )

    for lesson in sorted(lessons):
        meta = _frontmatter_of(lesson)
        if tag and tag not in meta.get("tags", []):
            continue
        results.append(_course_line(lesson))

    if not results:
        return (
            "No pages found"
            + (f" with tag '{tag}'" if tag else "")
            + (f" in '{directory}'" if directory else "")
        )

    corpus.log_retrieval("list_pages", tag=tag, directory=directory, n_results=len(results))
    header = f"**{len(results)} page(s)**" + (f" tagged '{tag}'" if tag else "") + ":\n\n"
    return header + "\n".join(results)


def domain_briefing(domain: str) -> str:
    """All pages of a domain concatenated, ordered decisions → patterns → concepts.

    `course/<subject>/<module>` briefs one course module; larger course scopes are refused
    when they exceed COURSE_BRIEFING_MAX_CHARS.
    """
    if corpus.is_course_domain(domain):
        course_dir = corpus.resolve_course_dir(domain)
        if course_dir is None:
            return _unknown_domain(domain)
        pages = sorted(corpus.course_pages(course_dir))
        size = sum(p.stat().st_size for p in pages)
        if size > COURSE_BRIEFING_MAX_CHARS:
            return (
                f"Domain '{domain}' is too large to brief ({len(pages)} lessons, {size} bytes). "
                f"Use list_domain to pick a module, or search_wiki with this domain."
            )
    else:
        domain_dir = corpus.resolve_domain_dir(domain)
        if domain_dir is None:
            return _unknown_domain(domain)
        pages = sorted(p for p in domain_dir.glob("*.md") if not p.name.startswith("_"))
    if not pages:
        return f"No pages found in domain '{domain}'"

    type_order = {
        "decision": 0,
        "pattern": 1,
        "comparison": 2,
        "concept": 3,
        "reference": 4,
        "project": 5,
    }
    parsed = []
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = parse_frontmatter(text)
        tags = meta.get("tags", [])
        type_tag = next((t for t in tags if t in type_order), "concept")
        parsed.append((type_order.get(type_tag, 3), meta.get("title", page.stem), text))

    parsed.sort(key=lambda x: (x[0], x[1]))

    sections = []
    for _, title, content in parsed:
        sections.append(f"{'=' * 60}\n# {title}\n{'=' * 60}\n\n{content}")

    corpus.log_retrieval("get_domain_briefing", domain=domain, n_pages=len(parsed))
    header = (
        f"# Domain Briefing: {domain.upper()}\n"
        f"{len(parsed)} pages · use read_page for any individual page\n\n"
    )
    return header + "\n\n".join(sections)
