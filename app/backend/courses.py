"""Course API — serves data/courses/ (lessons imported by core/import_courses.py or
hand-authored) to the React course view, and ties lessons to wiki graph nodes.

Layout: data/courses/<course>/_course.md, <course>/<module>/_module.md, and lesson
.md files anywhere below a module. Ordering and titles come from frontmatter. Flashcards live
in <course>/<module>/_flashcards.md, frontmatter `cards: [{front, back, lesson?}, ...]`.

Lesson ↔ concept links come from four places, ranked in this order:
- explicit: `wiki: [page-id, ...]` in lesson frontmatter, or inline [[Wiki Title]]
- compiled: wiki pages whose `sources:` list this lesson's raw copy (data/raw/repos/
  learn-ai-engineering/<lesson path with / as -->.md): the page was written from it
- mentioned: wiki page titles that appear verbatim in the lesson text (multi-word
  titles only — single words like "Memory" match everything)
- semantic: nearest wiki pages by embedding cosine (local MiniLM via shared.embeddings,
  at most SEMANTIC_TOP_K above SEMANTIC_THRESHOLD). Needs the `api` extra; without it
  (CI) linking falls back to the first two sources.
Private and tombstoned wiki pages are never surfaced here.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import frontmatter
import yaml
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.wiki_common import WIKILINK_RE, page_aliases, slugify
from shared.log_config import get_logger

from . import leitner

log = get_logger(__name__)

ROOT = Path(__file__).parent.parent.parent
COURSES_DIR = ROOT / "data" / "courses"
WIKI_DIR = ROOT / "data" / "wiki"
# Read live from the private sisyphus checkout and never copied into data/ — this repo is
# public and the log is personal history. Absent → drills just show no attempts.
DRILL_LOG = (
    Path(os.environ.get("SISYPHUS_DIR", ROOT.parent / "sisyphus"))
    / "drills"
    / "coding"
    / "drill-log.md"
)
# Personal study history: logs/*.jsonl is gitignored and this repo is public. Read by
# learn-ai-engineering's scripts/review/signals.py to find cards and slides worth re-reading.
FLASHCARD_LOG = ROOT / "logs" / "flashcards.jsonl"

ASSET_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_CONCEPTS = 12
# Semantic linking (D5). 0.55 kept after a spot check on the real courses (2026-10-30):
# pairs >= ~0.62 are reliably on-topic, 0.55-0.62 are mostly same-area neighbours, and
# below 0.5 MiniLM pairs lessons with pages that only share vocabulary. Raising to 0.58
# or 0.60 cut lesson coverage from 324 to 284 / 267 of 762 without removing a clear
# class of bad links.
SEMANTIC_THRESHOLD = 0.55
SEMANTIC_TOP_K = 6
LESSON_PROSE_CHARS = 1500
LESSON_RAW_PREFIX = "data/raw/repos/learn-ai-engineering/"
# Lesson vectors keyed by content hash, so a warm restart re-embeds nothing (gitignored).
LESSON_VEC_CACHE = ROOT / ".cache" / "lesson_embeddings.npz"
DRILL_KEYS = ("track", "topic", "difficulty", "timebox_min")  # programming/drills/README.md schema
_FENCE_RE = re.compile(r"^\s*(```|~~~)")

router = APIRouter(prefix="/api/courses")


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


@dataclass
class Catalog:
    courses: list[dict[str, Any]]
    lessons: dict[str, LessonRec]  # id → lesson, in course order
    wiki: dict[str, WikiRef]
    by_concept: dict[str, list[str]]  # wiki id → lesson ids
    decks: dict[str, dict[str, Any]] = field(default_factory=dict)  # module or lesson id → deck


# ── Loading ──────────────────────────────────────────────────────────────────


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
        _current = _load(COURSES_DIR, WIKI_DIR, sig)
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
        tags = post.get("tags") or []
        if "tombstone" in tags:
            continue
        refs[md.stem] = WikiRef(
            id=md.stem,
            title=str(post.get("title") or md.stem),
            summary=str(post.get("summary") or ""),
            domain=rel.parts[0] if len(rel.parts) > 1 else "",
            sources=tuple(str(x) for x in post.get("sources") or []),
            aliases=tuple(page_aliases(post.metadata)),
        )
    return refs


def _wiki_slugs(wiki: dict[str, WikiRef]) -> dict[str, str]:
    """Link slug → page id. Stems beat titles beat aliases, so an imported lesson's link to a
    page's old name keeps resolving after a rename."""
    aliases = {slugify(a): r.id for r in wiki.values() for a in r.aliases}
    return aliases | {slugify(r.title): r.id for r in wiki.values()} | {slugify(i): i for i in wiki}


def _compiled_from(wiki: dict[str, WikiRef]) -> dict[str, list[str]]:
    """Lesson id → the pages compiled from its raw copy."""
    out: dict[str, list[str]] = {}
    for ref in wiki.values():
        for src in ref.sources:
            if src.startswith(LESSON_RAW_PREFIX) and src.endswith(".md"):
                lesson = src[len(LESSON_RAW_PREFIX) : -3].replace("--", "/")
                out.setdefault(lesson, []).append(ref.id)
    return out


def _prose(body: str) -> str:
    """Body with fenced code removed — concept mentions inside code are noise."""
    out, in_fence = [], False
    for line in body.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _concept_matcher(wiki: dict[str, WikiRef]) -> tuple[re.Pattern[str] | None, dict[str, str]]:
    by_title: dict[str, str] = {}
    for ref in wiki.values():
        t = ref.title.strip().lower()
        if len(t.split()) >= 2 and len(t) <= 60:
            by_title.setdefault(t, ref.id)
    if not by_title:
        return None, by_title
    alts = sorted(by_title, key=len, reverse=True)
    pattern = re.compile(
        r"(?<![\w-])(" + "|".join(re.escape(t) for t in alts) + r")(?![\w-])", re.I
    )
    return pattern, by_title


def _resolve_wikilink(target: str, wiki: dict[str, WikiRef], slugs: dict[str, str]) -> str | None:
    target = target.strip()
    if target in wiki:
        return target
    return slugs.get(slugify(target))


@lru_cache(maxsize=2)
def _load(courses_dir: Path, wiki_dir: Path, _sig: tuple[int, int]) -> Catalog:
    wiki = _load_wiki(wiki_dir)
    slugs = _wiki_slugs(wiki)
    matcher, by_title = _concept_matcher(wiki)
    compiled = _compiled_from(wiki)
    # Private/tombstoned page ids: never echoed back, not even as a drill tag.
    hidden = {md.stem for md in wiki_dir.rglob("*.md")} - set(wiki) if wiki_dir.is_dir() else set()

    courses: list[dict[str, Any]] = []
    lessons: dict[str, LessonRec] = {}
    decks: dict[str, dict[str, Any]] = {}
    embed_texts: dict[str, str] = {}  # lesson id → text to embed
    if not courses_dir.is_dir():
        return Catalog([], {}, wiki, {})

    for course_dir in sorted(p for p in courses_dir.iterdir() if p.is_dir()):
        cmeta = _meta(course_dir / "_course.md")
        modules: list[dict[str, Any]] = []
        for mod_dir in sorted(p for p in course_dir.iterdir() if p.is_dir()):
            mmeta = _meta(mod_dir / "_module.md")
            recs: list[LessonRec] = []
            for md in mod_dir.rglob("*.md"):
                if md.name.startswith("_") or "assets" in md.relative_to(mod_dir).parts:
                    continue
                post = frontmatter.load(md)
                lid = str(md.relative_to(courses_dir).with_suffix(""))
                embed_texts[lid] = _lesson_text(post, md.stem)
                recs.append(
                    LessonRec(
                        id=lid,
                        course=course_dir.name,
                        module=mod_dir.name,
                        title=str(post.get("title") or md.stem),
                        summary=str(post.get("summary") or ""),
                        order=int(post.get("order") or 999),
                        section=str(post.get("section") or ""),
                        kind=str(post.get("kind") or "reading"),
                        source=str(post.get("source") or ""),
                        body=post.content,
                        concepts=_rank_concepts(
                            post, wiki, slugs, matcher, by_title, compiled.get(lid, [])
                        ),
                        drill=_drill_meta(post, wiki, slugs, hidden)
                        if post.get("kind") == "drill"
                        else {},
                    )
                )
            recs.sort(key=lambda r: (r.order, r.id))
            for r in recs:
                lessons[r.id] = r
            if not recs and not mmeta.get("readings") and not mmeta.get("references"):
                continue
            module_title = str(mmeta.get("title") or mod_dir.name)
            cards = _load_cards(mod_dir / "_flashcards.md", {r.id: r for r in recs})
            decks |= _build_decks(course_dir.name, mod_dir.name, module_title, cards, recs)
            modules.append(
                {
                    "id": mod_dir.name,
                    "title": module_title,
                    "summary": str(mmeta.get("summary") or ""),
                    # 00-start-here is order 0, so `or 999` would sort it last.
                    "order": int(999 if mmeta.get("order") is None else mmeta["order"]),
                    "readings": mmeta.get("readings") or [],
                    "references": mmeta.get("references") or [],
                    "lessons": [_outline(r) for r in recs],
                    **({"flashcardCount": len(cards)} if cards else {}),
                }
            )
        modules.sort(key=lambda m: (m["order"], m["id"]))
        courses.append(
            {
                "id": course_dir.name,
                "title": str(cmeta.get("title") or course_dir.name),
                "summary": str(cmeta.get("summary") or ""),
                "order": int(cmeta.get("order") or 999),
                "lessonCount": sum(len(m["lessons"]) for m in modules),
                "modules": modules,
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
    return Catalog(courses, ordered, wiki, by_concept, decks)


def _meta(path: Path) -> dict[str, Any]:
    return frontmatter.load(path).metadata if path.exists() else {}


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


def _drill_meta(
    post: frontmatter.Post, wiki: dict[str, WikiRef], slugs: dict[str, str], hidden: set[str]
) -> dict[str, Any]:
    """DRILL_KEYS, plus `tags`: declared concepts with no wiki page yet (shown as plain labels)."""
    meta = {k: post[k] for k in DRILL_KEYS if post.get(k) is not None}
    tags = [
        str(x)
        for x in (post.get("wiki") or [])
        if not _resolve_wikilink(str(x), wiki, slugs) and slugify(str(x)) not in hidden
    ]
    return meta | ({"tags": tags} if tags else {})


def _rank_concepts(
    post: frontmatter.Post,
    wiki: dict[str, WikiRef],
    slugs: dict[str, str],
    matcher: re.Pattern[str] | None,
    by_title: dict[str, str],
    compiled: list[str],
) -> list[str]:
    explicit = [str(x) for x in (post.get("wiki") or [])]
    explicit += [m.group(1) for m in WIKILINK_RE.finditer(post.content)]
    ranked: list[str] = []
    for target in explicit:
        pid = _resolve_wikilink(target, wiki, slugs)
        if pid and pid not in ranked:
            ranked.append(pid)
    ranked += [pid for pid in compiled if pid not in ranked]
    if matcher:
        counts: dict[str, int] = {}
        text = f"{post.get('title') or ''}\n{_prose(post.content)}"
        for m in matcher.finditer(text):
            pid = by_title[m.group(1).lower()]
            counts[pid] = counts.get(pid, 0) + 1
        for pid, _ in sorted(counts.items(), key=lambda kv: -kv[1]):
            if pid not in ranked:
                ranked.append(pid)
    return ranked[:MAX_CONCEPTS]


# ── Semantic concept linking ─────────────────────────────────────────────────

# (lesson texts, eligible wiki ids) → per text, (wiki id, cosine) candidates best first,
# or None when embeddings are unavailable. Module-level so tests can swap in a fake.
Neighbours = list[list[tuple[str, float]]]


def _lesson_text(post: frontmatter.Post, stem: str) -> str:
    title = str(post.get("title") or stem)
    summary = str(post.get("summary") or "")
    return f"{title}. {summary}\n\n{_prose(post.content)[:LESSON_PROSE_CHARS]}"


def _semantic_neighbours(texts: list[str], wiki_ids: list[str]) -> Neighbours | None:
    """Embedding neighbours among `wiki_ids` for each text, via shared.embeddings.

    Wiki vectors come from compute_embeddings() (the same DuckDB-cached vectors the
    semantic graph edges and UMAP use); lesson vectors from encode_texts_cached().
    Returns None — and the catalog keeps explicit + title-mention links only — when the
    `api` extra is missing or anything in the embedding stack fails.
    """
    try:
        import numpy as np

        from shared.embeddings import compute_embeddings, encode_texts_cached
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


def _merge_semantic(
    ranked: list[str], candidates: list[tuple[str, float]], wiki: set[str]
) -> list[str]:
    """Append up to SEMANTIC_TOP_K new candidates ≥ SEMANTIC_THRESHOLD after `ranked`.

    Explicit and title-mention links keep their places; `wiki` is the visible page set,
    so a private or tombstoned id can never get in even if the embedder returns one.
    """
    out = list(ranked)
    added = 0
    for pid, score in sorted(candidates, key=lambda c: -c[1]):
        if added >= SEMANTIC_TOP_K or len(out) >= MAX_CONCEPTS or score < SEMANTIC_THRESHOLD:
            break
        if pid in wiki and pid not in out:
            out.append(pid)
            added += 1
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


def _outline(r: LessonRec) -> dict[str, Any]:
    return {
        "id": r.id,
        "title": r.title,
        "section": r.section,
        "kind": r.kind,
        "summary": r.summary,
        **({"drill": r.drill} if r.drill else {}),
        **({"flashcardCount": r.flashcards} if r.flashcards else {}),
    }


def _wiki_json(ref: WikiRef) -> dict[str, str]:
    return {"id": ref.id, "title": ref.title, "summary": ref.summary, "domain": ref.domain}


def _link_wikilinks(body: str, cat: Catalog) -> str:
    """[[Title|alias]] → [alias](#wiki:<id>) outside code; unresolved → plain text."""
    slugs = _wiki_slugs(cat.wiki)
    out, in_fence = [], False
    for line in body.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
        elif not in_fence and "[[" in line:

            def sub(m: re.Match[str]) -> str:
                inner = m.group(0)[2:-2]
                target, _, alias = inner.partition("|")
                label = alias or target.split("#")[0]
                pid = _resolve_wikilink(target.split("#")[0], cat.wiki, slugs)
                return f"[{label}](#wiki:{pid})" if pid else label

            line = re.sub(r"\[\[[^\]]+\]\]", sub, line)
        out.append(line)
    return "\n".join(out)


# ── Routes ───────────────────────────────────────────────────────────────────


@router.get("")
def list_courses() -> list[dict[str, Any]]:
    return catalog().courses


@router.get("/lessons/{lesson_id:path}")
def get_lesson(lesson_id: str) -> dict[str, Any]:
    cat = catalog()
    lesson = cat.lessons.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="lesson not found")
    ids = [i for i, r in cat.lessons.items() if r.course == lesson.course]
    pos = ids.index(lesson_id)
    neighbour = lambda i: _outline(cat.lessons[ids[i]]) if 0 <= i < len(ids) else None  # noqa: E731
    return {
        **_outline(lesson),
        "course": lesson.course,
        "module": lesson.module,
        "source": lesson.source,
        "body": _link_wikilinks(lesson.body, cat),
        "concepts": [_wiki_json(cat.wiki[c]) for c in lesson.concepts if c in cat.wiki],
        "prev": neighbour(pos - 1),
        "next": neighbour(pos + 1),
    }


_MD_NOISE_RE = re.compile(r"\[\[|\]\]|[#*_`|>]+|-{3,}|\[([^\]]*)\]\([^)]*\)")


def _snippet(r: LessonRec, term: str) -> str:
    """~240 chars of plain text around the first prose mention of `term`."""
    text = " ".join(_MD_NOISE_RE.sub(lambda m: m.group(1) or " ", _prose(r.body)).split())
    idx = text.lower().find(term)
    if idx < 0:
        return r.summary
    start = max(0, idx - 80)
    while 0 < start < idx and text[start - 1] != " ":  # don't open mid-word
        start += 1
    return ("…" if start else "") + text[start : idx + 160] + "…"


@router.get("/search")
def search(q: str, limit: int = 30) -> list[dict[str, Any]]:
    terms = [t for t in q.lower().split() if len(t) > 1]
    if not terms:
        return []
    hits: list[tuple[int, LessonRec, str]] = []
    for r in catalog().lessons.values():
        title, body = r.title.lower(), r.body.lower()
        if not all(t in title or t in body for t in terms):
            continue
        score = sum(10 * title.count(t) + min(body.count(t), 20) for t in terms)
        hits.append((score, r, _snippet(r, terms[0])))
    hits.sort(key=lambda h: -h[0])
    return [
        {**_outline(r), "course": r.course, "snippet": snip}
        for _, r, snip in hits[: max(1, min(limit, 100))]
    ]


@router.get("/concept/{page_id}")
def lessons_for_concept(page_id: str) -> list[dict[str, Any]]:
    """Lessons that cover a wiki page — the graph → course direction."""
    cat = catalog()
    return [
        {**_outline(cat.lessons[i]), "course": cat.lessons[i].course}
        for i in cat.by_concept.get(page_id, [])
    ]


@router.get("/practice")
def practice(
    track: str | None = None, difficulty: str | None = None, concept: str | None = None
) -> list[dict[str, Any]]:
    """Drills (lessons of kind "drill"), filtered — the Practice mode list."""
    cat = catalog()
    attempts = _drill_attempts(DRILL_LOG)
    out = []
    for r in cat.lessons.values():
        if r.kind != "drill":
            continue
        if track and r.drill.get("track") != track:
            continue
        if difficulty and r.drill.get("difficulty") != difficulty:
            continue
        if concept and concept not in r.concepts and concept not in r.drill.get("tags", []):
            continue
        concepts = [_wiki_json(cat.wiki[c]) for c in r.concepts if c in cat.wiki]
        row = {**_outline(r), "course": r.course, "concepts": concepts}
        if (hit := attempts.get(Path(r.id).name)) is not None:
            row["attempts"] = hit
        out.append(row)
    return out


def _scheduled_deck(
    deck: dict[str, Any], states: dict[str, leitner.CardState], today: date
) -> dict[str, Any]:
    """A copy of a cached deck with each card's Leitner state and the deck's counts."""
    cards: list[dict[str, Any]] = []
    for card in deck["cards"]:
        state = states.get(leitner.card_key(deck["id"], card["front"]))
        cards.append(
            card
            | {
                "box": state.box if state else None,
                "dueOn": state.due_on.isoformat() if state else None,
                "status": leitner.status_of(state, today),
            }
        )
    counts = Counter(c["status"] for c in cards)
    return deck | {"cards": cards, "dueCount": counts["due"], "newCount": counts["new"]}


@router.get("/flashcards/{deck_id:path}")
def flashcards(deck_id: str) -> dict[str, Any]:
    """A study deck: every card in a module (`<course>/<module>`) or one lesson (lesson id)."""
    deck = catalog().decks.get(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="no flashcards here")
    return _scheduled_deck(deck, leitner.load_states(FLASHCARD_LOG), date.today())


@router.get("/flashcards-due")
def flashcards_due() -> dict[str, Any]:
    """Cards to study today across every module deck, reviewed and never-seen counted apart."""
    states = leitner.load_states(FLASHCARD_LOG)
    today = date.today()
    modules: list[dict[str, Any]] = []
    for deck_id, deck in catalog().decks.items():
        if deck_id.count("/") != 1:
            continue
        counted = _scheduled_deck(deck, states, today)
        if counted["dueCount"] or counted["newCount"]:
            modules.append(
                {
                    "deck": deck_id,
                    "title": deck["title"],
                    "due": counted["dueCount"],
                    "new": counted["newCount"],
                }
            )
    modules.sort(key=lambda m: (-m["due"], m["deck"]))
    return {
        "today": today.isoformat(),
        "due": sum(m["due"] for m in modules),
        "new": sum(m["new"] for m in modules),
        "modules": modules,
    }


class CardResult(BaseModel):
    deck: str
    card: str
    result: Literal["knew", "missed"]


@router.post("/flashcard-results")
def flashcard_result(body: CardResult) -> dict[str, bool]:
    """Log one self-graded card. The text comes from the catalog, never from the request.

    A failed write returns logged=false rather than an error: it must not interrupt studying.
    """
    cat = catalog()
    card = next(
        (c for c in cat.decks.get(body.deck, {}).get("cards", []) if c["id"] == body.card), None
    )
    if card is None:
        raise HTTPException(status_code=404, detail="no such card")
    rec = cat.lessons.get(card["lesson"]) if card["lesson"] else None
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "deck": body.deck,
        "card": leitner.card_key(body.deck, card["front"]),
        "lesson": card["lesson"],
        "source": rec.source if rec else "",
        "front": card["front"],
        "result": body.result,
    }
    try:
        FLASHCARD_LOG.parent.mkdir(exist_ok=True)
        with FLASHCARD_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        log.warning("flashcard_log_failed", error=str(e))
        return {"logged": False}
    return {"logged": True}


def _drill_attempts(log: Path) -> dict[str, dict[str, Any]]:
    """drill slug (log QID) → {count, last, score} from the log's Markdown table.

    Only those three columns are read; the free-text Note column never leaves the file.
    """
    try:
        text = log.read_text()
    except OSError:
        return {}
    cols: list[str] = []
    out: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cols:
            cols = [c.lower() for c in cells]
            continue
        row = dict(zip(cols, cells, strict=False))
        qid, date = row.get("qid", ""), row.get("date", "")
        if not qid or not re.match(r"\d{4}-\d{2}-\d{2}$", date):
            continue  # the |---| separator, or a malformed row
        prev = out.get(qid)
        if prev is None or date >= prev["last"]:
            out[qid] = {
                "count": (prev or {"count": 0})["count"] + 1,
                "last": date,
                "score": row.get("score", ""),
            }
        else:
            prev["count"] += 1
    return out


@router.get("/files/{file_path:path}")
def course_file(file_path: str) -> FileResponse:
    # Same two-step guard as /api/writeback: reject traversal syntax, then confirm the
    # resolved path is inside the courses root. Only images are served.
    if ".." in Path(file_path).parts or file_path.startswith("/"):
        raise HTTPException(status_code=400, detail="invalid path")
    target = (COURSES_DIR / file_path).resolve()
    if not target.is_relative_to(COURSES_DIR.resolve()) or target.suffix.lower() not in ASSET_TYPES:
        raise HTTPException(status_code=400, detail="invalid path")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(target)
