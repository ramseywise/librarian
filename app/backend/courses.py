"""Course API — serves data/courses/ (lessons imported by core/import_courses.py or
hand-authored) to the React course view, and ties lessons to wiki graph nodes.

Layout: data/courses/<course>/_course.md, <course>/<module>/_module.md, and lesson
.md files anywhere below a module. Ordering and titles come from frontmatter.

Lesson ↔ concept links come from two places:
- explicit: `wiki: [page-id, ...]` in lesson frontmatter, or inline [[Wiki Title]]
- mentioned: wiki page titles that appear verbatim in the lesson text (multi-word
  titles only — single words like "Memory" match everything)
Private and tombstoned wiki pages are never surfaced here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import frontmatter
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from core.wiki_common import WIKILINK_RE, slugify

ROOT = Path(__file__).parent.parent.parent
COURSES_DIR = ROOT / "data" / "courses"
WIKI_DIR = ROOT / "data" / "wiki"

ASSET_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_CONCEPTS = 12
DRILL_KEYS = ("track", "topic", "difficulty", "timebox_min")  # sisyphus drill schema
_FENCE_RE = re.compile(r"^\s*(```|~~~)")

router = APIRouter(prefix="/api/courses")


@dataclass
class WikiRef:
    id: str
    title: str
    summary: str
    domain: str


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


@dataclass
class Catalog:
    courses: list[dict[str, Any]]
    lessons: dict[str, LessonRec]  # id → lesson, in course order
    wiki: dict[str, WikiRef]
    by_concept: dict[str, list[str]]  # wiki id → lesson ids


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


def catalog() -> Catalog:
    return _load(COURSES_DIR, WIKI_DIR, _signature(COURSES_DIR, WIKI_DIR))


def _load_wiki(wiki_dir: Path) -> dict[str, WikiRef]:
    refs: dict[str, WikiRef] = {}
    if not wiki_dir.is_dir():
        return refs
    for md in sorted(wiki_dir.rglob("*.md")):
        rel = md.relative_to(wiki_dir)
        if md.name.startswith("_") or rel.parts[0] == "private":
            continue
        post = frontmatter.load(md)
        tags = post.get("tags") or []
        if "tombstone" in tags:
            continue
        refs[md.stem] = WikiRef(
            id=md.stem,
            title=str(post.get("title") or md.stem),
            summary=str(post.get("summary") or ""),
            domain=rel.parts[0] if len(rel.parts) > 1 else "",
        )
    return refs


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
    slugs = {slugify(r.title): r.id for r in wiki.values()} | {slugify(i): i for i in wiki}
    matcher, by_title = _concept_matcher(wiki)

    courses: list[dict[str, Any]] = []
    lessons: dict[str, LessonRec] = {}
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
                        concepts=_rank_concepts(post, wiki, slugs, matcher, by_title),
                        drill={k: post[k] for k in DRILL_KEYS if post.get(k) is not None}
                        if post.get("kind") == "drill"
                        else {},
                    )
                )
            recs.sort(key=lambda r: (r.order, r.id))
            for r in recs:
                lessons[r.id] = r
            if not recs and not mmeta.get("readings") and not mmeta.get("references"):
                continue
            modules.append(
                {
                    "id": mod_dir.name,
                    "title": str(mmeta.get("title") or mod_dir.name),
                    "summary": str(mmeta.get("summary") or ""),
                    "order": int(mmeta.get("order") or 999),
                    "readings": mmeta.get("readings") or [],
                    "references": mmeta.get("references") or [],
                    "lessons": [_outline(r) for r in recs],
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
    return Catalog(courses, ordered, wiki, by_concept)


def _meta(path: Path) -> dict[str, Any]:
    return frontmatter.load(path).metadata if path.exists() else {}


def _rank_concepts(
    post: frontmatter.Post,
    wiki: dict[str, WikiRef],
    slugs: dict[str, str],
    matcher: re.Pattern[str] | None,
    by_title: dict[str, str],
) -> list[str]:
    explicit = [str(x) for x in (post.get("wiki") or [])]
    explicit += [m.group(1) for m in WIKILINK_RE.finditer(post.content)]
    ranked: list[str] = []
    for target in explicit:
        pid = _resolve_wikilink(target, wiki, slugs)
        if pid and pid not in ranked:
            ranked.append(pid)
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


def _outline(r: LessonRec) -> dict[str, Any]:
    return {
        "id": r.id,
        "title": r.title,
        "section": r.section,
        "kind": r.kind,
        "summary": r.summary,
        **({"drill": r.drill} if r.drill else {}),
    }


def _wiki_json(ref: WikiRef) -> dict[str, str]:
    return {"id": ref.id, "title": ref.title, "summary": ref.summary, "domain": ref.domain}


def _link_wikilinks(body: str, cat: Catalog) -> str:
    """[[Title|alias]] → [alias](#wiki:<id>) outside code; unresolved → plain text."""
    slugs = {slugify(r.title): r.id for r in cat.wiki.values()}
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
    out = []
    for r in cat.lessons.values():
        if r.kind != "drill":
            continue
        if track and r.drill.get("track") != track:
            continue
        if difficulty and r.drill.get("difficulty") != difficulty:
            continue
        if concept and concept not in r.concepts:
            continue
        concepts = [_wiki_json(cat.wiki[c]) for c in r.concepts if c in cat.wiki]
        out.append({**_outline(r), "course": r.course, "concepts": concepts})
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
