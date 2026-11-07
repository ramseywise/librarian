"""Read-side queries the API routes call: lessons, search, drills, flashcard decks and study state.

The catalog and the drill log are reached through `librarian.courses.catalog` at call time, so a test
that patches `catalog.catalog` or `catalog.DRILL_LOG` still takes effect here."""

from __future__ import annotations

import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from librarian.courses import attempts, leitner, sources
from librarian.courses.linker import _link_wikilinks, _prose
from librarian.courses.loader import LessonRec, _outline, _wiki_json


def _cat():  # noqa: ANN202 - the catalog module; imported late because it imports this one
    from librarian.courses import catalog as module

    return module


def list_courses() -> list[dict[str, Any]]:
    return _cat().catalog().courses


def lesson_detail(lesson_id: str) -> dict[str, Any] | None:
    """One lesson with its body, concepts and neighbours in its course; None when unknown."""
    cat = _cat().catalog()
    lesson = cat.lessons.get(lesson_id)
    if not lesson:
        return None
    # A public lesson's neighbours are public: prev/next never leads from it into private/.
    ids = [
        i
        for i, r in cat.lessons.items()
        if r.course == lesson.course and (lesson.private or not r.private)
    ]
    pos = ids.index(lesson_id)
    neighbour = lambda i: _outline(cat.lessons[ids[i]]) if 0 <= i < len(ids) else None  # noqa: E731
    return {
        **_outline(lesson),
        "course": lesson.course,
        "module": lesson.module,
        "source": lesson.source,
        "body": _link_wikilinks(lesson.body, cat),
        "sourceLinks": sources.source_links(lesson_id, lesson.body),
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


def search_lessons(q: str, limit: int = 30) -> list[dict[str, Any]]:
    terms = [t for t in q.lower().split() if len(t) > 1]
    if not terms:
        return []
    hits: list[tuple[int, LessonRec, str]] = []
    for r in _cat().catalog().lessons.values():
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


def lessons_for_concept(page_id: str) -> list[dict[str, Any]]:
    """Lessons that cover a wiki page — the graph → course direction."""
    cat = _cat().catalog()
    return [
        {**_outline(cat.lessons[i]), "course": cat.lessons[i].course}
        for i in cat.by_concept.get(page_id, [])
    ]


def practice_drills(
    track: str | None = None, difficulty: str | None = None, concept: str | None = None
) -> list[dict[str, Any]]:
    """Drills (lessons of kind "drill"), filtered — the Practice mode list."""
    cat = _cat().catalog()
    history = drill_history()
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
        if (hit := history.get(Path(r.id).name)) is not None:
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


def study_deck(deck_id: str) -> dict[str, Any] | None:
    """A study deck: every card in a module (`<course>/<module>`) or one lesson (lesson id)."""
    deck = _cat().catalog().decks.get(deck_id)
    if not deck:
        return None
    return _scheduled_deck(deck, leitner.load_states(), date.today())


def flashcards_due() -> dict[str, Any]:
    """Cards to study today across every module deck, reviewed and never-seen counted apart."""
    states = leitner.load_states()
    today = date.today()
    modules: list[dict[str, Any]] = []
    for deck_id, deck in _cat().catalog().decks.items():
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


def log_flashcard_result(deck_id: str, card_id: str, result: str) -> bool | None:
    """Store one self-graded card. The text comes from the catalog, never from the caller.

    None when the deck has no such card. A failed write returns False rather than raising:
    it must not interrupt studying.
    """
    cat = _cat().catalog()
    card = next(
        (c for c in cat.decks.get(deck_id, {}).get("cards", []) if c["id"] == card_id), None
    )
    if card is None:
        return None
    rec = cat.lessons.get(card["lesson"]) if card["lesson"] else None
    return attempts.record(
        "flashcard",
        leitner.card_key(deck_id, card["front"]),
        deck_id,
        result,
        payload={
            "lesson": card["lesson"],
            "source": rec.source if rec else "",
            "front": card["front"],
        },
    )


def drill_history() -> dict[str, dict[str, Any]]:
    """Drill slug -> {count, last, score}: the sisyphus log (read-only) plus runs recorded in the app.

    An app run is keyed by its lesson id, whose last segment is the slug the log uses. `score` is the
    latest one by date; a run recorded in the app shows as its result (pass, fail or revealed).
    """
    merged = _drill_attempts(_cat().DRILL_LOG)
    for a in attempts.attempts(["drill"]):
        slug, day = Path(a.item).name, a.ts.astimezone().date().isoformat()
        prev = merged.get(slug)
        if prev is None:
            merged[slug] = {"count": 1, "last": day, "score": a.result}
        else:
            prev["count"] += 1
            if day >= prev["last"]:
                prev["last"], prev["score"] = day, a.result
    return merged


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
