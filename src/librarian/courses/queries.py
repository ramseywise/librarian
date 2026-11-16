"""Read-side queries the API routes call: lessons, search, drills, flashcard decks and study state.

Study state (schedules, drill history) is per user: those functions take the `User`. The catalog is
reached through `librarian.courses.catalog` at call time, so a test that patches `catalog.catalog`
still takes effect here."""

from __future__ import annotations

import difflib
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from librarian.accounts import User
from librarian.courses import attempts, labs, leitner, sources
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
        "labs": [lab_outline(lab) for lab in labs_for_lesson(lesson_id)],
    }


def lab_outline(lab: labs.Lab) -> dict[str, Any]:
    """The list row of a lab."""
    return {
        "id": lab.id,
        "title": lab.title,
        "course": lab.course,
        "module": lab.module,
        "path": lab.path,
        "purpose": lab.purpose,
        "pattern": lab.pattern,
        "language": lab.language,
        "runsOffline": lab.runs_offline,
        "hasRun": lab.run is not None,
        "hasCheck": lab.check is not None,
    }


def _lab_notes(cat: Any) -> dict[str, list[str]]:  # noqa: ANN401 - the Catalog
    """Lab id → the public lesson ids it backs: its manifest's `demonstrates`, plus any note in
    its module that names the lab's file (a manifest can leave `demonstrates` empty)."""
    by_module: dict[str, list[LessonRec]] = {}
    for r in cat.lessons.values():
        if not r.private:
            by_module.setdefault("/".join(r.id.split("/")[:2]), []).append(r)
    lower = {i.lower(): i for i in cat.lessons if not cat.lessons[i].private}
    out: dict[str, list[str]] = {}
    for lab in labs.all_labs().values():
        found = [lower[n.lower()] for n in lab.notes if n.lower() in lower]
        name = Path(lab.path).name
        for r in by_module.get(f"{lab.course}/{lab.module}", []):
            if r.id not in found and r.kind != "drill" and name in r.body:
                found.append(r.id)
        out[lab.id] = found
    return out


def labs_for_lesson(lesson_id: str) -> list[labs.Lab]:
    """The labs that back one lesson — the note → lab direction."""
    all_labs = labs.all_labs()
    notes = _lab_notes(_cat().catalog())
    return [all_labs[i] for i, ids in notes.items() if lesson_id in ids]


def list_labs(
    course: str | None = None, module: str | None = None, language: str | None = None
) -> list[dict[str, Any]]:
    """Every mirrored lab, filtered, each with the notes it backs — the Labs mode list."""
    cat = _cat().catalog()
    notes = _lab_notes(cat)
    out = []
    for lab in labs.all_labs().values():
        if (
            (course and lab.course != course)
            or (module and lab.module != module)
            or (language and lab.language != language)
        ):
            continue
        lesson_rows = [_outline(cat.lessons[i]) for i in notes.get(lab.id, [])]
        out.append({**lab_outline(lab), "notes": lesson_rows})
    return out


def lab_detail(lab_id: str) -> dict[str, Any] | None:
    """One lab with its editable files' text, the notes it backs and its commands; None when unknown."""
    lab = labs.get(lab_id)
    if lab is None:
        return None
    cat = _cat().catalog()
    files = []
    for rel in lab.files:
        if (path := labs.lab_file(lab, rel)) is None:
            continue
        try:
            files.append({"path": rel, "text": path.read_text()})
        except (OSError, UnicodeDecodeError):
            continue
    return {
        **lab_outline(lab),
        "licence": lab.licence,
        "verifiedBy": lab.verified_by,
        "run": lab.run.display() if lab.run else None,
        "check": lab.check.display() if lab.check else None,
        "files": files,
        "notes": [_outline(cat.lessons[i]) for i in _lab_notes(cat).get(lab.id, [])],
    }


BRIEF_DIFF_CHARS = 12_000
BRIEF_CODE_CHARS = 12_000
BRIEF_OUTPUT_CHARS = 8_000


def lab_brief(
    lab_id: str, files: dict[str, str], output: str = "", exit_code: int | None = None
) -> str | None:
    """What the chat agent is told about an open lab: its purpose, the notes it backs, the user's
    edit as a diff from the mirror's copy (or the entry file when nothing changed) and the tail of
    the last run. None for an unknown lab. Every part is capped, the output keeping its end."""
    lab = labs.get(lab_id)
    if lab is None:
        return None
    cat = _cat().catalog()
    notes = [cat.lessons[i] for i in _lab_notes(cat).get(lab.id, [])]
    parts = [f"Lab: {lab.title} ({lab.id})", f"Language: {lab.language}", f"Purpose: {lab.purpose}"]
    if notes:
        parts.append("Notes it backs:\n" + "\n".join(f"- {r.title}: {r.summary}" for r in notes))
    if lab.run:
        parts.append(f"Run command: {lab.run.display()}")
    if lab.check:
        parts.append(f"Check command: {lab.check.display()}")

    diffs = []
    for rel in lab.files:
        if rel not in files or (path := labs.lab_file(lab, rel)) is None:
            continue
        try:
            original = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        if files[rel] != original:
            diffs.append(
                "".join(
                    difflib.unified_diff(
                        original.splitlines(keepends=True),
                        files[rel].splitlines(keepends=True),
                        f"original/{rel}",
                        f"edited/{rel}",
                    )
                )
            )
    if diffs:
        parts.append("The user's edit (unified diff):\n" + "\n".join(diffs)[:BRIEF_DIFF_CHARS])
    else:
        parts.append("The user has not changed the lab's files.")
        entry = next((f for f in lab.files if f.endswith(".py")), None)
        if entry and (path := labs.lab_file(lab, entry)) is not None:
            text = files.get(entry) or path.read_text(errors="replace")
            parts.append(f"{entry}:\n{text[:BRIEF_CODE_CHARS]}")
    if output:
        tail = output[-BRIEF_OUTPUT_CHARS:]
        status = "" if exit_code is None else f" (exit status {exit_code})"
        cut = "" if len(tail) == len(output) else " — the end of it"
        parts.append(f"Last run's output{status}{cut}:\n{tail}")
    return "\n\n".join(parts)


def _public_lesson(cat: Any, lesson_id: str | None) -> LessonRec | None:  # noqa: ANN401 - the Catalog
    rec = cat.lessons.get(lesson_id) if lesson_id else None
    return None if rec is None or rec.private else rec


def _lesson_part(rec: LessonRec, query: str) -> str:
    """A lesson's title, summary and the indexed section of it that best fits `query`."""
    from librarian.retrieval import corpus, ranking
    from librarian.retrieval.format import cap_section

    ref = f"{corpus.COURSE_DOMAIN}/{rec.id}.md"
    head = f'Lesson: {rec.title} (read_page("{ref}") for all of it)\nSummary: {rec.summary}'
    path = str(corpus.COURSES_DIR / f"{rec.id}.md")
    best = ranking.best_sections(query, [path], table="course_pages").get(path)
    if best is None:
        return head
    heading, text = best
    return f"{head}\n\nThe part of it this is about ({heading or 'Introduction'}):\n{cap_section(text)}"


def study_brief(
    *,
    deck: str | None = None,
    card: str | None = None,
    quiz_id: str | None = None,
    question: str | None = None,
    lesson: str | None = None,
    revealed: bool = False,
) -> str | None:
    """What the chat agent is told about the card, question or lesson the user is studying.

    Built from catalog ids, never from text the client sends. A quiz's answer and explanation
    go in only once `revealed` (the user has answered), so the tutor cannot give it away. None for
    an unknown id and for anything private: private course text never reaches the chat model.
    """
    cat = _cat().catalog()
    parts: list[str] = []
    rec: LessonRec | None = None
    query = ""
    if deck is not None or card is not None:
        item = next(
            (c for c in cat.decks.get(deck or "", {}).get("cards", []) if c["id"] == card), None
        )
        if item is None or (deck or "").startswith("private/"):
            return None
        rec = _public_lesson(cat, item["lesson"])
        if item["lesson"] and rec is None:
            return None
        parts.append(f"Flashcard\nFront: {item['front']}\nBack: {item['back']}")
        query = f"{item['front']} {item['back']}"
    elif quiz_id is not None or question is not None:
        qz = cat.quizzes.get(quiz_id or "")
        q = next((x for x in qz["questions"] if x.id == question), None) if qz else None
        if q is None or (quiz_id or "").startswith("private/"):
            return None
        rec = _public_lesson(cat, q.lesson)
        if q.lesson and rec is None:
            return None
        lines = [f"Quiz question: {q.prompt}"]
        lines += [f"- {o}" for o in q.options]
        if revealed:
            lines.append(f"Answer: {q.answer}")
            if q.explanation:
                lines.append(f"Explanation: {q.explanation}")
        else:
            lines.append("The user has not answered yet: the answer is withheld.")
        parts.append("\n".join(lines))
        query = q.prompt
    elif lesson is not None:
        rec = _public_lesson(cat, lesson)
        if rec is None:
            return None
        query = f"{rec.title} {rec.summary}"
    else:
        return None
    if rec is not None:
        parts.append(_lesson_part(rec, query))
    return "\n\n".join(parts)


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
    user: User,
    track: str | None = None,
    difficulty: str | None = None,
    concept: str | None = None,
) -> list[dict[str, Any]]:
    """Drills (lessons of kind "drill"), filtered, with `user`'s attempts — the Practice mode list."""
    cat = _cat().catalog()
    history = drill_history(user)
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


def study_deck(user: User, deck_id: str) -> dict[str, Any] | None:
    """A study deck: every card in a module (`<course>/<module>`) or one lesson (lesson id)."""
    deck = _cat().catalog().decks.get(deck_id)
    if not deck:
        return None
    return _scheduled_deck(deck, leitner.load_states(user), leitner.today(user))


def flashcards_due(user: User) -> dict[str, Any]:
    """`user`'s cards to study today across every module deck, reviewed and never-seen counted apart."""
    states = leitner.load_states(user)
    today = leitner.today(user)
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


def log_flashcard_result(user: User, deck_id: str, card_id: str, result: str) -> bool | None:
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
        user.id,
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


def drill_history(user: User) -> dict[str, dict[str, Any]]:
    """Drill slug -> {count, last, score} from `user`'s drill attempts.

    An app run is keyed by its lesson id, whose last segment is the slug; a row imported from the
    sisyphus log (`librarian db import-drill-log`) is keyed by the slug itself. `last` is a date in
    the user's timezone and `score` the latest run's: the log's score, else the app's result (pass,
    fail or revealed).
    """
    tz = leitner.zone(user.timezone)
    merged: dict[str, dict[str, Any]] = {}
    for a in attempts.attempts(user.id, ["drill"]):
        slug, day = Path(a.item).name, a.ts.astimezone(tz).date().isoformat()
        score = str(a.payload.get("score") or a.result)
        prev = merged.get(slug)
        if prev is None:
            merged[slug] = {"count": 1, "last": day, "score": score}
        else:
            prev["count"] += 1
            if day >= prev["last"]:
                prev["last"], prev["score"] = day, score
    return merged
