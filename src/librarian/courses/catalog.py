"""Course API — serves data/courses/ (hand-authored lessons) to the React course view, and ties lessons to wiki graph nodes.

Layout: data/courses/<course>/_course.md, <course>/<module>/_module.md, and lesson
.md files anywhere below a module. Ordering and titles come from frontmatter. Flashcards live
in <course>/<module>/_flashcards.md, frontmatter `cards: [{front, back, lesson?}, ...]`; multiple-choice
questions in <course>/<module>/_quiz.md (see quiz.py).

Lesson ↔ concept links come from four places, ranked in this order:
- explicit: `wiki: [page-id, ...]` in lesson frontmatter, or inline [[Wiki Title]]
- compiled: wiki pages whose `sources:` list this lesson's raw copy (data/raw/repos/
  learn-ai-engineering/<lesson path with / as -->.md): the page was written from it
- mentioned: wiki page titles that appear verbatim in the lesson text (multi-word
  titles only — single words like "Memory" match everything)
- semantic: nearest wiki pages by embedding cosine (local MiniLM via librarian.retrieval.embeddings,
  at most SEMANTIC_TOP_K above SEMANTIC_THRESHOLD). Needs the `api` extra; without it
  (CI) linking falls back to the first two sources.
Private and tombstoned wiki pages are never surfaced here.

data/courses/private/ (gitignored, like data/wiki/private/) mirrors the public layout:
`private/<course>/<module>/...`. Its lessons are served to the local UI as part of the course
they name, each marked `private: true` (a module or course only they make up is marked too).
Public lessons never get them as prev/next. The curriculum facet, the gap list and the search
index leave them out, so nothing derived from them reaches a tracked file or an exported one.

The code is split by seam, and this module is the facade: the loaders are in `loader`, the
concept linking in `linker`, the read-side queries in `queries` and the image guard in `assets`.
What stays here is what tests and the API patch or flip at module level (the paths, `PUBLIC_MODE`,
`DRILL_LOG`, `LESSON_VEC_CACHE`) and the cache state. The moved names are re-exported, so
`from librarian.courses import catalog` keeps every name it had.
"""

from __future__ import annotations

import threading
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import frontmatter
import yaml

from librarian.config import get_settings
from librarian.courses import quiz
from librarian.courses.assets import (
    ASSET_TYPES as ASSET_TYPES,
)
from librarian.courses.assets import (
    asset_path as asset_path,
)
from librarian.courses.assets import (
    is_private_asset as is_private_asset,
)
from librarian.courses.linker import (
    LESSON_PROSE_CHARS as LESSON_PROSE_CHARS,
)
from librarian.courses.linker import (
    MAX_CONCEPTS as MAX_CONCEPTS,
)
from librarian.courses.linker import (
    SEMANTIC_THRESHOLD as SEMANTIC_THRESHOLD,
)
from librarian.courses.linker import (
    SEMANTIC_TOP_K as SEMANTIC_TOP_K,
)
from librarian.courses.linker import (
    Neighbours as Neighbours,
)
from librarian.courses.linker import (
    _concept_matcher as _concept_matcher,
)
from librarian.courses.linker import (
    _drill_meta as _drill_meta,
)
from librarian.courses.linker import (
    _lesson_text as _lesson_text,
)
from librarian.courses.linker import (
    _link_wikilinks as _link_wikilinks,
)
from librarian.courses.linker import (
    _merge_semantic as _merge_semantic,
)
from librarian.courses.linker import (
    _prose as _prose,
)
from librarian.courses.linker import (
    _rank_concepts as _rank_concepts,
)
from librarian.courses.linker import (
    _resolve_wikilink as _resolve_wikilink,
)
from librarian.courses.loader import (
    DEFAULT_ORDER as DEFAULT_ORDER,
)
from librarian.courses.loader import (
    DRILL_KEYS as DRILL_KEYS,
)
from librarian.courses.loader import (
    LESSON_RAW_PREFIX as LESSON_RAW_PREFIX,
)
from librarian.courses.loader import (
    PRIVATE_COURSES as PRIVATE_COURSES,
)
from librarian.courses.loader import (
    Catalog as Catalog,
)
from librarian.courses.loader import (
    LessonRec as LessonRec,
)
from librarian.courses.loader import (
    WikiRef as WikiRef,
)
from librarian.courses.loader import (
    _build_decks as _build_decks,
)
from librarian.courses.loader import (
    _build_quizzes as _build_quizzes,
)
from librarian.courses.loader import (
    _compiled_from as _compiled_from,
)
from librarian.courses.loader import (
    _course_dirs as _course_dirs,
)
from librarian.courses.loader import (
    _first_meta as _first_meta,
)
from librarian.courses.loader import (
    _load_cards as _load_cards,
)
from librarian.courses.loader import (
    _load_wiki as _load_wiki,
)
from librarian.courses.loader import (
    _merged_readings as _merged_readings,
)
from librarian.courses.loader import (
    _meta as _meta,
)
from librarian.courses.loader import (
    _module_dirs as _module_dirs,
)
from librarian.courses.loader import (
    _order as _order,
)
from librarian.courses.loader import (
    _outline as _outline,
)
from librarian.courses.loader import (
    _readings_count as _readings_count,
)
from librarian.courses.loader import (
    _signature as _signature,
)
from librarian.courses.loader import (
    _wiki_json as _wiki_json,
)
from librarian.courses.loader import (
    _wiki_slugs as _wiki_slugs,
)
from librarian.courses.loader import (
    outline as outline,
)
from librarian.courses.queries import (
    _drill_attempts as _drill_attempts,
)
from librarian.courses.queries import (
    _scheduled_deck as _scheduled_deck,
)
from librarian.courses.queries import (
    _snippet as _snippet,
)
from librarian.courses.queries import (
    drill_history as drill_history,
)
from librarian.courses.queries import (
    flashcards_due as flashcards_due,
)
from librarian.courses.queries import (
    lesson_detail as lesson_detail,
)
from librarian.courses.queries import (
    lessons_for_concept as lessons_for_concept,
)
from librarian.courses.queries import (
    list_courses as list_courses,
)
from librarian.courses.queries import (
    log_flashcard_result as log_flashcard_result,
)
from librarian.courses.queries import (
    practice_drills as practice_drills,
)
from librarian.courses.queries import (
    search_lessons as search_lessons,
)
from librarian.courses.queries import (
    study_deck as study_deck,
)
from librarian.log_config import get_logger
from librarian.retrieval.corpus import is_under_private
from librarian.wiki.common import fm

log = get_logger(__name__)

_settings = get_settings()
ROOT = _settings.root
COURSES_DIR = _settings.courses_dir
WIKI_DIR = _settings.wiki_dir
# Deployed container: the private/ course tree is not read at all. Module-level so a test can flip it.
PUBLIC_MODE = _settings.public_mode
# Read live from the private sisyphus checkout and never copied into data/ — this repo is
# public and the log is personal history. Absent → drills just show no attempts.
DRILL_LOG = _settings.drill_log
# Lesson vectors keyed by content hash, so a warm restart re-embeds nothing (gitignored).
LESSON_VEC_CACHE = _settings.lesson_vec_cache


# One build at a time: the startup warmup and an early request would otherwise both
# run the multi-second cold build (lru_cache does not dedupe concurrent misses).
_LOAD_LOCK = threading.Lock()


# Monotonic time of the last transient embedding failure. _load is cached on the markdown
# signature alone, so without this a one-off failure (DuckDB lock held by an ingest, model
# download hiccup) would pin a catalog without semantic links until some .md file changed.
_semantic_failed_at: float | None = None


SEMANTIC_RETRY_S = 60.0


# The last catalog built. While another thread rebuilds (a wiki edit or ingest changed
# the signature), requests get this one instead of queueing behind a multi-second build.
_current: Catalog | None = None


def catalog() -> Catalog:
    global _semantic_failed_at, _current
    # Stat the trees before taking the lock: it walks every .md, and holding the lock for
    # it would serialise every request, not just the rebuilds.
    sig = _signature(COURSES_DIR, WIKI_DIR)
    prev = _current
    if prev is None:
        _LOAD_LOCK.acquire()  # cold start: nothing to serve, so wait for the build
    elif not _LOAD_LOCK.acquire(blocking=False):
        return prev  # a rebuild is running: stale by at most that build, never a wait
    try:
        if (
            _semantic_failed_at is not None
            and time.monotonic() - _semantic_failed_at > SEMANTIC_RETRY_S
        ):
            _semantic_failed_at = None
            _load.cache_clear()
        _current = _load(COURSES_DIR, WIKI_DIR, sig, PUBLIC_MODE)
        return _current
    finally:
        _LOAD_LOCK.release()


def warm_catalog() -> None:
    """Build the catalog ahead of the first request (run off the event loop at startup).

    Never raises: a warmup failure must not take the server down, and the first request
    will rebuild and surface the real error.
    """
    start = time.perf_counter()
    try:
        cat = catalog()
    except Exception as e:  # optimisation only; the route reports real errors
        log.warning("courses.warmup.failed", error=str(e))
        return
    log.info(
        "courses.warmup.done",
        lessons=len(cat.lessons),
        with_concepts=sum(1 for r in cat.lessons.values() if r.concepts),
        seconds=round(time.perf_counter() - start, 2),
    )


@lru_cache(maxsize=2)
def _load(
    courses_dir: Path, wiki_dir: Path, _sig: tuple[int, int], public: bool = False
) -> Catalog:
    wiki = _load_wiki(wiki_dir)
    slugs = _wiki_slugs(wiki)
    matcher, by_title = _concept_matcher(wiki)
    compiled = _compiled_from(wiki)
    # Private/tombstoned page ids: never echoed back, not even as a drill tag.
    hidden = {md.stem for md in wiki_dir.rglob("*.md")} - set(wiki) if wiki_dir.is_dir() else set()

    courses: list[dict[str, Any]] = []
    lessons: dict[str, LessonRec] = {}
    decks: dict[str, dict[str, Any]] = {}
    quizzes: dict[str, dict[str, Any]] = {}
    embed_texts: dict[str, str] = {}  # lesson id → text to embed
    if not courses_dir.is_dir():
        return Catalog([], {}, wiki, {})

    private_root = courses_dir / PRIVATE_COURSES
    for course_name, course_dirs in _course_dirs(courses_dir, public).items():
        cmeta = _first_meta(course_dirs, "_course.md")
        modules: list[dict[str, Any]] = []
        for module_name, mod_dirs in _module_dirs(course_dirs).items():
            mmeta = _first_meta(mod_dirs, "_module.md")
            readings = _merged_readings(mod_dirs)
            readings_count = max(len(readings), _readings_count(mod_dirs))
            recs: list[LessonRec] = []
            for mod_dir in mod_dirs:
                for md in mod_dir.rglob("*.md"):
                    if md.name.startswith("_") or "assets" in md.relative_to(mod_dir).parts:
                        continue
                    try:
                        post = frontmatter.load(md)
                    except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
                        log.warning(
                            "lesson_skipped",
                            path=str(md),
                            error=str(e).splitlines()[0] if str(e) else repr(e),
                        )
                        continue
                    lid = str(md.relative_to(courses_dir).with_suffix(""))
                    embed_texts[lid] = _lesson_text(post, md.stem)
                    recs.append(
                        LessonRec(
                            id=lid,
                            course=course_name,
                            module=module_name,
                            title=str(fm(post).get("title") or md.stem),
                            summary=str(fm(post).get("summary") or ""),
                            order=_order(fm(post).get("order"), str(md)),
                            section=str(fm(post).get("section") or ""),
                            kind=str(fm(post).get("kind") or "reading"),
                            source=str(fm(post).get("source") or ""),
                            body=post.content,
                            concepts=_rank_concepts(
                                post, wiki, slugs, matcher, by_title, compiled.get(lid, [])
                            ),
                            drill=_drill_meta(post, wiki, slugs, hidden)
                            if fm(post).get("kind") == "drill"
                            else {},
                            private=is_under_private(md, private_root),
                        )
                    )
            recs.sort(key=lambda r: (r.order, r.id))
            for r in recs:
                lessons[r.id] = r
            if not recs and not readings_count and not mmeta.get("references"):
                continue
            module_title = str(mmeta.get("title") or module_name)
            cards = [
                c
                for d in mod_dirs
                for c in _load_cards(d / "_flashcards.md", {r.id: r for r in recs})
            ]
            for i, card in enumerate(cards):
                card["id"] = str(i)
            decks |= _build_decks(course_name, module_name, module_title, cards, recs)
            questions = [
                q for d in mod_dirs for q in quiz.load(d / quiz.QUIZ_FILE, {r.id for r in recs})
            ]
            quizzes |= _build_quizzes(course_name, module_name, module_title, questions, recs)
            modules.append(
                {
                    "id": module_name,
                    "title": module_title,
                    "summary": str(mmeta.get("summary") or ""),
                    "order": _order(mmeta.get("order"), module_name),
                    # Public: only the count. The list itself is in the private overlay.
                    "readings": readings,
                    "readingsCount": readings_count,
                    "references": mmeta.get("references") or [],
                    "lessons": [_outline(r) for r in recs],
                    **({"flashcardCount": len(cards)} if cards else {}),
                    **({"quizCount": len(questions)} if questions else {}),
                    **({"private": True} if all(r.private for r in recs) and recs else {}),
                }
            )
        modules.sort(key=lambda m: (m["order"], m["id"]))
        courses.append(
            {
                "id": course_name,
                "title": str(cmeta.get("title") or course_name),
                "summary": str(cmeta.get("summary") or ""),
                "order": _order(cmeta.get("order"), course_name),
                "lessonCount": sum(len(m["lessons"]) for m in modules),
                "modules": modules,
                **({"private": True} if modules and all(m.get("private") for m in modules) else {}),
            }
        )
    courses.sort(key=lambda c: (c["order"], c["id"]))

    _attach_semantic(lessons, embed_texts, wiki)

    # Re-key lessons in reading order so prev/next follows the sidebar.
    ordered = {
        lesson["id"]: lessons[lesson["id"]]
        for c in courses
        for m in c["modules"]
        for lesson in m["lessons"]
    }
    by_concept: dict[str, list[str]] = {}
    for lesson in ordered.values():
        for cid in lesson.concepts:
            by_concept.setdefault(cid, []).append(lesson.id)
    return Catalog(courses, ordered, wiki, by_concept, decks, quizzes)


def _semantic_neighbours(texts: list[str], wiki_ids: list[str]) -> Neighbours | None:
    """Embedding neighbours among `wiki_ids` for each text, via librarian.retrieval.embeddings.

    Wiki vectors come from compute_embeddings() (the same DuckDB-cached vectors the
    semantic graph edges and UMAP use); lesson vectors from encode_texts_cached().
    Returns None — and the catalog keeps explicit + title-mention links only — when the
    `api` extra is missing or anything in the embedding stack fails.
    """
    try:
        import numpy as np

        from librarian.retrieval.embeddings import compute_embeddings, encode_texts_cached
    except ImportError as e:
        log.info("courses.semantic.skipped", reason="api extra not installed", error=str(e))
        return None
    if not texts or not wiki_ids:
        return None
    global _semantic_failed_at
    try:
        page_ids, page_vecs = compute_embeddings()
        # compute_embeddings keys by file stem across all of data/wiki/, private/ included.
        # A stem that occurs twice (private/foo.md + rag/foo.md) can't be attributed to the
        # visible page, so it is left out rather than risk scoring private content.
        counts = Counter(page_ids)
        eligible = {pid for pid in wiki_ids if counts[pid] == 1}
        rows = [i for i, pid in enumerate(page_ids) if pid in eligible]
        if not rows:
            return None
        ids = [page_ids[i] for i in rows]
        wiki_mat = page_vecs[rows]
        lesson_mat = encode_texts_cached(texts, LESSON_VEC_CACHE)
    except Exception as e:  # model download, cache lock: degrade, never fail
        log.warning("courses.semantic.failed", error=str(e), retry_after_s=SEMANTIC_RETRY_S)
        _semantic_failed_at = time.monotonic()
        return None
    sims = lesson_mat @ wiki_mat.T  # both L2-normalised → cosine
    keep = SEMANTIC_TOP_K + MAX_CONCEPTS  # headroom for candidates already ranked
    out: Neighbours = []
    for row in sims:
        best = np.argsort(-row)[:keep]
        out.append([(ids[j], float(row[j])) for j in best])
    return out


def _attach_semantic(
    lessons: dict[str, LessonRec], texts: dict[str, str], wiki: dict[str, WikiRef]
) -> None:
    ids = [lid for lid in lessons if lid in texts]
    neighbours = _semantic_neighbours([texts[lid] for lid in ids], list(wiki))
    if neighbours is None:
        return
    visible = set(wiki)
    for lid, cands in zip(ids, neighbours, strict=True):
        lessons[lid].concepts = _merge_semantic(lessons[lid].concepts, cands, visible)
