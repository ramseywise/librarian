"""What the index covers and what may be served: locations, page enumeration, privacy, telemetry.

The module-level locations are read at call time by every other retrieval module (as
`corpus.WIKI_DIR`, never `from corpus import WIKI_DIR`), so a test can repoint them in one place.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from librarian.config import get_settings
from librarian.log_config import get_logger

log = get_logger(__name__)

# Locations come from librarian.config, anchored on the repo root and not on the working
# directory, so `librarian api` and `librarian mcp` find the same wiki root and index.
REPO_ROOT = get_settings().root
WIKI_DIR = get_settings().wiki_dir
PRIVATE_DIR = WIKI_DIR / "private"
COURSES_DIR = get_settings().courses_dir
COURSE_DOMAIN = "course"
DB_PATH = get_settings().wiki_db_path
INDEX_DIR = get_settings().index_dir
LOGS_DIR = get_settings().logs_dir
RETRIEVAL_LOG = LOGS_DIR / "retrieval.jsonl"
# Past this size the log moves to `retrieval.jsonl.1` (one generation kept, the older one replaced).
RETRIEVAL_LOG_MAX_BYTES = 5_000_000


def wiki_domains() -> list[str]:
    """Domain names derived from disk: directories under data/wiki/, minus private/.

    Replaces a hardcoded list that had drifted (6 directories missing, 1 phantom).
    Read at call time so tests can repoint WIKI_DIR.
    """
    if not WIKI_DIR.is_dir():
        return []
    return sorted(d.name for d in WIKI_DIR.iterdir() if d.is_dir() and d.name != "private")


def course_domain(path: Path | str) -> str:
    """`course/<subject>` for a lesson path. The path is the only source of a lesson's domain."""
    return f"{COURSE_DOMAIN}/{Path(path).relative_to(COURSES_DIR).parts[0]}"


def course_ref(path: Path | str) -> str:
    """The `course/<relative path>` form of a lesson path, as read_page accepts it."""
    return f"{COURSE_DOMAIN}/{Path(path).relative_to(COURSES_DIR).as_posix()}"


def course_domains() -> list[str]:
    """`course` plus one `course/<subject>` per directory under data/courses/."""
    if not COURSES_DIR.is_dir():
        return []
    subjects = sorted(d.name for d in COURSES_DIR.iterdir() if d.is_dir() and d.name != "private")
    return [COURSE_DOMAIN, *(f"{COURSE_DOMAIN}/{s}" for s in subjects)]


def is_course_domain(domain: str) -> bool:
    return domain == COURSE_DOMAIN or domain.startswith(f"{COURSE_DOMAIN}/")


def is_under_private(path: Path | str, private_dir: Path) -> bool:
    """True if path lies under private_dir — never indexed, never served.

    Buyi invariant "data/wiki/private/ never leaves the machine", clause (b). Resolved
    before comparison so ../ traversal and absolute paths cannot slip past.

    private_dir is a parameter, not this module's PRIVATE_DIR, so callers and
    tests can supply their own root; `is_private` binds it to PRIVATE_DIR read
    at call time.
    """
    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError):
        return True  # unresolvable path — refuse rather than risk serving it
    root = private_dir.resolve()
    return resolved == root or root in resolved.parents


def courses_private_dir() -> Path:
    """data/courses/private/, beside whichever COURSES_DIR is current."""
    return COURSES_DIR / "private"


def is_private(path: Path | str) -> bool:
    """is_under_private bound to the private trees: data/wiki/private/ and data/courses/private/
    (both read at call time)."""
    return is_under_private(path, PRIVATE_DIR) or is_under_private(path, courses_private_dir())


def resolve_course_dir(domain: str) -> Path | None:
    """Directory for `course`, `course/<subject>` or deeper; None if absent or outside the root."""
    rel = domain.removeprefix(COURSE_DOMAIN).strip("/")
    candidate = COURSES_DIR / rel
    if (
        candidate.is_dir()
        and candidate.resolve().is_relative_to(COURSES_DIR.resolve())
        and not is_private(candidate)
    ):
        return candidate
    return None


def resolve_domain_dir(domain: str) -> Path | None:
    """Return the wiki subdirectory for a domain name, or None if not found.

    Resolves to None for data/wiki/private/ so list_domain and get_domain_briefing
    cannot address it as a domain.
    """
    root = WIKI_DIR.resolve()
    for name in (domain, domain.replace("_", "-").lower()):
        candidate = WIKI_DIR / name
        if (
            candidate.is_dir()
            and candidate.resolve().is_relative_to(root)
            and not is_private(candidate)
        ):
            return candidate
    return None


def wiki_pages() -> list[Path]:
    """Indexable wiki pages: no private pages, no `_` or `.` files."""
    return [
        p for p in WIKI_DIR.rglob("*.md") if not p.name.startswith((".", "_")) and not is_private(p)
    ]


def course_pages(root: Path | None = None) -> list[Path]:
    """Indexable lessons under root (default all of data/courses/).

    `_course.md`, `_module.md` and `_flashcards.md` are skipped like any `_` file: the first
    two are frontmatter-only catalog metadata whose summary and titles reappear in lessons,
    and flashcards restate deck takeaways. A symlink leaving the course root is not a lesson, and nothing under
    data/courses/private/ is ever indexed.
    """
    courses_root = COURSES_DIR.resolve()
    if is_private(courses_root):
        return []
    # Runs several times per search, so resolve only files that are symlinks: rglob's `**`
    # does not descend through directory symlinks, and resolving every path is most of the cost.
    private_root = courses_private_dir()
    return [
        p
        for p in (root or COURSES_DIR).rglob("*.md")
        if not p.name.startswith((".", "_"))
        and private_root not in p.parents
        and (not p.is_symlink() or (p.resolve().is_relative_to(courses_root) and not is_private(p)))
    ]


def log_retrieval(tool: str, **fields: object) -> None:
    """Append one JSON line of retrieval telemetry to logs/retrieval.jsonl.

    Never raises — telemetry must not break retrieval. Rotates by size; concurrent writers are
    not locked (a lost line at rotation is acceptable for telemetry). Consumed by /compact-wiki
    as merge/retire evidence (see .claude/docs/plans/2026-07-17-knowledge-compaction.md).
    """
    try:
        LOGS_DIR.mkdir(exist_ok=True)
        if RETRIEVAL_LOG.exists() and RETRIEVAL_LOG.stat().st_size > RETRIEVAL_LOG_MAX_BYTES:
            RETRIEVAL_LOG.replace(RETRIEVAL_LOG.with_name(RETRIEVAL_LOG.name + ".1"))
        entry = {"ts": datetime.now(UTC).isoformat(), "tool": tool, **fields}
        with RETRIEVAL_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log.warning("telemetry_failed", error=str(e))
