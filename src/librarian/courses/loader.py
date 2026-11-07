"""Reading data/courses/ and data/wiki/ into catalog records: the dataclasses, directory walks, module metadata, decks and quizzes.

Pure parsing helpers: nothing here reads a module-level path, so `librarian.courses.catalog` keeps
the patchable settings and the cache.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter
import yaml

from librarian.courses import quiz
from librarian.log_config import get_logger
from librarian.wiki.common import LinkEntry, LinkIndex, fm, page_aliases

log = get_logger(__name__)

DEFAULT_ORDER = 999  # no (usable) `order`: sorts after every numbered entry
PRIVATE_COURSES = "private"  # data/courses/private/, same name as data/wiki/private/
DRILL_KEYS = ("track", "topic", "difficulty", "timebox_min")  # programming/drills/README.md schema
LESSON_RAW_PREFIX = "data/raw/repos/learn-ai-engineering/"


@dataclass
class WikiRef:
    id: str
    title: str
    summary: str
    domain: str
    sources: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


@dataclass
class LessonRec:
    id: str  # path under COURSES_DIR without .md
    course: str
    module: str
    title: str
    summary: str
    order: int
    section: str
    kind: str
    source: str
    body: str
    concepts: list[str] = field(default_factory=list)  # wiki page ids, ranked
    drill: dict[str, Any] = field(default_factory=dict)  # DRILL_KEYS, kind == "drill" only
    flashcards: int = 0
    questions: int = 0
    private: bool = False  # under data/courses/private/: local only


@dataclass
class Catalog:
    courses: list[dict[str, Any]]
    lessons: dict[str, LessonRec]  # id → lesson, in course order
    wiki: dict[str, WikiRef]
    by_concept: dict[str, list[str]]  # wiki id → lesson ids
    decks: dict[str, dict[str, Any]] = field(default_factory=dict)  # module or lesson id → deck
    quizzes: dict[str, dict[str, Any]] = field(default_factory=dict)  # module or lesson id → quiz


def _signature(*dirs: Path) -> tuple[int, int]:
    """Cheap change detector: (file count, newest mtime) over the markdown trees."""
    count, newest = 0, 0
    for d in dirs:
        if not d.is_dir():
            continue
        for p in d.rglob("*.md"):
            count += 1
            newest = max(newest, p.stat().st_mtime_ns)
    return count, newest


def _load_wiki(wiki_dir: Path) -> dict[str, WikiRef]:
    refs: dict[str, WikiRef] = {}
    if not wiki_dir.is_dir():
        return refs
    for md in sorted(wiki_dir.rglob("*.md")):
        rel = md.relative_to(wiki_dir)
        if md.name.startswith("_") or rel.parts[0] == "private":
            continue
        try:
            post = frontmatter.load(md)
        except yaml.YAMLError as e:
            log.error("wiki_page_skipped", page=md.name, error=str(e).splitlines()[0])
            continue
        tags = fm(post).get("tags") or []
        if "tombstone" in tags:
            continue
        refs[md.stem] = WikiRef(
            id=md.stem,
            title=str(fm(post).get("title") or md.stem),
            summary=str(fm(post).get("summary") or ""),
            domain=rel.parts[0] if len(rel.parts) > 1 else "",
            sources=tuple(str(x) for x in fm(post).get("sources") or []),
            aliases=tuple(page_aliases(post.metadata)),
        )
    return refs


def _wiki_slugs(wiki: dict[str, WikiRef]) -> LinkIndex:
    """The shared link resolver over the public pages, so a lesson's link to a page's old name
    keeps resolving after a rename and means the same page it does in the graph and the index."""
    return LinkIndex(
        LinkEntry(key=r.id, path=r.id, stem=r.id, title=r.title, aliases=r.aliases)
        for r in wiki.values()
    )


def _compiled_from(wiki: dict[str, WikiRef]) -> dict[str, list[str]]:
    """Lesson id → the pages compiled from its raw copy."""
    out: dict[str, list[str]] = {}
    for ref in wiki.values():
        for src in ref.sources:
            if src.startswith(LESSON_RAW_PREFIX) and src.endswith(".md"):
                lesson = src[len(LESSON_RAW_PREFIX) : -3].replace("--", "/")
                out.setdefault(lesson, []).append(ref.id)
    return out


def _order(value: Any, where: str) -> int:  # noqa: ANN401 - raw frontmatter value
    """Sort order from frontmatter. 0 is a real order (00-start-here); a missing or unusable
    value sorts last, and an unusable one is logged."""
    if value is None:
        return DEFAULT_ORDER
    try:
        return int(value)
    except (TypeError, ValueError):
        log.warning("order_invalid", where=where, value=repr(value))
        return DEFAULT_ORDER


def _course_dirs(courses_dir: Path, public: bool = False) -> dict[str, list[Path]]:
    """Course name → its directories: the public one, then the same name under private/
    (not at all in public mode)."""
    found: dict[str, list[Path]] = {}
    roots = [(courses_dir, True)]
    if not public:
        roots.append((courses_dir / PRIVATE_COURSES, False))
    for root, is_public_root in roots:
        if not root.is_dir():
            continue
        for d in sorted(p for p in root.iterdir() if p.is_dir()):
            if is_public_root and d.name == PRIVATE_COURSES:
                continue
            found.setdefault(d.name, []).append(d)
    return dict(sorted(found.items()))


def _module_dirs(course_dirs: list[Path]) -> dict[str, list[Path]]:
    found: dict[str, list[Path]] = {}
    for course_dir in course_dirs:
        for d in sorted(p for p in course_dir.iterdir() if p.is_dir()):
            found.setdefault(d.name, []).append(d)
    return dict(sorted(found.items()))


def _first_meta(dirs: list[Path], name: str) -> dict[str, Any]:
    """Frontmatter of the first of `dirs` that has `name`; public comes first, so it wins."""
    return next((_meta(d / name) for d in dirs if (d / name).exists()), {})


def _merged_readings(mod_dirs: list[Path]) -> list[Any]:
    """Readings from every `_module.md` of the module (public first, then the private overlay)."""
    seen: set[str] = set()
    merged: list[Any] = []
    for d in mod_dirs:
        for r in _meta(d / "_module.md").get("readings") or []:
            key = str(r.get("source", r)) if isinstance(r, dict) else str(r)
            if key not in seen:
                seen.add(key)
                merged.append(r)
    return merged


def _readings_count(mod_dirs: list[Path]) -> int:
    """`readings_count` from the public `_module.md`: what the list held before it moved."""
    return max(
        (int(_meta(d / "_module.md").get("readings_count") or 0) for d in mod_dirs), default=0
    )


def _meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return frontmatter.load(path).metadata
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
        log.warning(
            "meta_skipped", path=str(path), error=str(e).splitlines()[0] if str(e) else repr(e)
        )
        return {}


def _load_cards(path: Path, recs: dict[str, LessonRec]) -> list[dict[str, Any]]:
    """Well-formed cards from a module's _flashcards.md. A `lesson` not in this module (its
    source was dropped, or a hand edit) falls back to the module deck."""
    if not path.exists():
        return []
    raw = _meta(path).get("cards")
    cards: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict) or not item.get("front") or not item.get("back"):
            continue
        rec = recs.get(str(item.get("lesson")))
        cards.append(
            {
                "id": str(len(cards)),
                "front": str(item["front"]),
                "back": str(item["back"]),
                "lesson": rec.id if rec else None,
                "lessonTitle": rec.title if rec else None,
            }
        )
    return cards


def _build_decks(
    course: str, module: str, title: str, cards: list[dict[str, Any]], recs: list[LessonRec]
) -> dict[str, dict[str, Any]]:
    """The module's deck, plus one per lesson with cards. Sets each lesson's flashcard count."""
    if not cards:
        return {}
    module_id = f"{course}/{module}"
    decks = {module_id: {"id": module_id, "title": title, "course": course, "cards": cards}}
    for r in recs:
        mine = [c for c in cards if c["lesson"] == r.id]
        r.flashcards = len(mine)
        if mine:
            decks[r.id] = {"id": r.id, "title": r.title, "course": course, "cards": mine}
    return decks


def _build_quizzes(
    course: str, module: str, title: str, questions: list[quiz.Question], recs: list[LessonRec]
) -> dict[str, dict[str, Any]]:
    """The module's quiz, plus one per lesson with questions. Sets each lesson's question count."""
    if not questions:
        return {}
    module_id = f"{course}/{module}"
    quizzes = {
        module_id: {"id": module_id, "title": title, "course": course, "questions": questions}
    }
    for r in recs:
        mine = [q for q in questions if q.lesson == r.id]
        r.questions = len(mine)
        if mine:
            quizzes[r.id] = {"id": r.id, "title": r.title, "course": course, "questions": mine}
    return quizzes


def _outline(r: LessonRec) -> dict[str, Any]:
    return {
        "id": r.id,
        "title": r.title,
        "section": r.section,
        "kind": r.kind,
        "summary": r.summary,
        **({"drill": r.drill} if r.drill else {}),
        **({"flashcardCount": r.flashcards} if r.flashcards else {}),
        **({"quizCount": r.questions} if r.questions else {}),
        **({"private": True} if r.private else {}),
    }


def outline(r: LessonRec) -> dict[str, Any]:
    """The sidebar row of a lesson."""
    return _outline(r)


def _wiki_json(ref: WikiRef) -> dict[str, str]:
    return {"id": ref.id, "title": ref.title, "summary": ref.summary, "domain": ref.domain}
