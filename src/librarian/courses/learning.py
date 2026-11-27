"""Concept mastery: what a learner has studied, folded into one score per wiki page.

A concept is a public wiki page. Evidence is whatever the learner did with a lesson that links the
page: finishing it (`progress`), a flashcard, a drill, a spoken grade, or a grade given straight to
a concept (`attempts`). Every read and write is per user; nothing is read from outside the store.
Private and tombstoned pages are not in `Catalog.wiki`, and a private lesson is never evidence or a
spoke, so neither reaches a result.

Scoring (`score_concept`): over the last WINDOW_N events of direct evidence (all evidence when
there is none), strength = sum(w*v) / (sum(w) + PRIOR); recency halves every HALF_LIFE_DAYS since
the last event; a concept is due when direct and strength*recency < DUE_THRESHOLD. Evidence that
is only semantic is capped at WEAK_ONLY_CAP and is never due.

Write side: `record_event` maps an API event onto the stores that already exist (a lesson mark, a
flashcard or drill attempt) or onto the `voice_grade` / `concept_grade` attempt kinds, which carry
no catalog item. Imported drill rows (keyed by file slug) count as drill evidence; their notes are
never read.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, Final, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from librarian.courses import attempts, leitner, progress
from librarian.courses import catalog as courses
from librarian.courses.loader import Catalog, LessonRec, WikiRef, outline

LinkTier = Literal["explicit", "semantic"]
EvidenceKind = Literal["lesson", "drill", "card"]
VoiceMode = Literal["flashcard", "approach", "interview"]

WINDOW_N: Final = 20  # events kept per concept
PRIOR: Final = 1.0  # pseudo-weight of "no evidence" in the strength mean
HALF_LIFE_DAYS: Final = 14.0
DUE_THRESHOLD: Final = 0.2
LESSON_VALUE: Final = 0.7  # reading a lesson to the end is weaker evidence than a pass
WEAK_ONLY_CAP: Final = 0.25
LINK_WEIGHT: Final = {"explicit": 1.0, "semantic": 0.5}
DIRECT_LINKS: Final = {"explicit"}
NEXT_MAX_LINKS: Final = 5  # lessons, drills and decks shown per Due row
PASS_AT: Final = 0.5  # a score at or above this is a pass / knew it
KINDS: Final = ("flashcard", "drill", "voice_grade", "concept_grade")  # what mastery reads


def utcnow() -> datetime:
    """The clock. Module-level so tests can move time without sleeping."""
    return datetime.now(UTC)


class LearningError(Exception):
    """The event could not be stored."""


# -- Events ----------------------------------------------------------------------------------

ID_RE = re.compile(r"^[\w./+-]+$")
Id = Annotated[str, StringConstraints(pattern=ID_RE.pattern, max_length=300)]


class EventIn(BaseModel):
    """`extra="forbid"`: an answer or a transcript is refused, not silently dropped."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["lesson_done", "drill_attempt", "card_grade", "voice_grade"]
    ts: datetime | None = None
    lesson: Id | None = None
    concept: Id | None = None
    score: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    deck: Id | None = None
    card: Id | None = None
    mode: VoiceMode | None = None  # voice_grade only: which spoken drill gave the score

    @field_validator("ts")
    @classmethod
    def _aware(cls, ts: datetime | None) -> datetime | None:
        return ts.replace(tzinfo=UTC) if ts is not None and ts.tzinfo is None else ts

    @model_validator(mode="after")
    def _has_what_its_kind_needs(self) -> Self:
        if self.kind == "lesson_done" and not self.lesson:
            raise ValueError("lesson_done needs a lesson")
        if self.kind != "lesson_done" and self.score is None:
            raise ValueError(f"{self.kind} needs a score")
        if self.kind == "drill_attempt" and not (self.lesson or self.concept):
            raise ValueError("drill_attempt needs a lesson or a concept")
        if self.kind == "card_grade" and not (self.concept or (self.deck and self.card)):
            raise ValueError("card_grade needs a deck and card, or a concept")
        if self.kind == "voice_grade":
            if self.mode is None:
                raise ValueError("voice_grade needs a mode")
            if not (self.lesson or self.deck):
                raise ValueError("voice_grade needs a lesson or a deck")
        elif self.mode is not None:
            raise ValueError("mode belongs to voice_grade")
        return self


# -- Links -----------------------------------------------------------------------------------


def lesson_links(cat: Catalog, rec: LessonRec) -> dict[str, LinkTier]:
    """A public lesson's concepts: the ranked ones are explicit, the trailing `semantic` ones weak.
    A private lesson links nothing."""
    if rec.private:
        return {}
    cut = len(rec.concepts) - rec.semantic
    return {
        cid: "explicit" if i < cut else "semantic"
        for i, cid in enumerate(rec.concepts)
        if cid in cat.wiki
    }


def _public(cat: Catalog, lesson_id: str | None) -> LessonRec | None:
    rec = cat.lessons.get(lesson_id) if lesson_id else None
    return None if rec is None or rec.private else rec


def _card_in(cat: Catalog, deck: str | None, card: str | None) -> dict[str, Any] | None:
    if (
        not deck
        or deck.startswith("private/")
        or (deck in cat.lessons and cat.lessons[deck].private)
    ):
        return None
    found = next((c for c in cat.decks.get(deck, {}).get("cards", []) if c["id"] == card), None)
    if found and found["lesson"] and cat.lessons[found["lesson"]].private:
        return None
    return found


def _drill_slugs(cat: Catalog) -> dict[str, str | None]:
    """Drill file slug -> lesson id; None when two public drills share the slug."""
    slugs: dict[str, str | None] = {}
    for rec in cat.lessons.values():
        if rec.kind == "drill" and not rec.private:
            slug = Path(rec.id).name
            slugs[slug] = None if slug in slugs else rec.id
    return slugs


def _linked(cat: Catalog, lesson: str | None, concept: str | None) -> dict[str, LinkTier]:
    rec = _public(cat, lesson)
    links: dict[str, LinkTier] = lesson_links(cat, rec) if rec else {}
    if concept and concept in cat.wiki:
        links[concept] = "explicit"  # named outright: as explicit as it gets
    return links


# -- Scoring (pure) --------------------------------------------------------------------------


@dataclass(frozen=True)
class Evidence:
    kind: EvidenceKind
    ts: datetime
    value: float
    link: LinkTier
    lesson: str | None = None  # where it came from, for the Due reason
    score_label: str | None = None
    deck: str | None = None  # the deck a card grade came from


@dataclass(frozen=True)
class ConceptScore:
    strength: float
    recency: float
    due: bool
    direct: bool
    last: Evidence
    counts: dict[str, int]


def score_concept(evidence: list[Evidence], now: datetime) -> ConceptScore | None:
    """The formula over one concept's evidence (any order); None with no evidence at all."""
    if not evidence:
        return None
    direct = [e for e in evidence if e.link in DIRECT_LINKS]
    used = sorted(direct or evidence, key=lambda e: e.ts)
    window = used[-WINDOW_N:]
    weight = sum(LINK_WEIGHT[e.link] for e in window)
    strength = sum(LINK_WEIGHT[e.link] * e.value for e in window) / (weight + PRIOR)
    if not direct:
        strength = min(strength, WEAK_ONLY_CAP)
    last = window[-1]
    days = max(0.0, (now - last.ts).total_seconds() / 86400)
    recency = 0.5 ** (days / HALF_LIFE_DAYS)
    tally = Counter(e.kind for e in used)
    return ConceptScore(
        strength=strength,
        recency=recency,
        due=bool(direct) and strength * recency < DUE_THRESHOLD,
        direct=bool(direct),
        last=last,
        counts={"lessons": tally["lesson"], "drills": tally["drill"], "cards": tally["card"]},
    )


# -- Folding the stores into evidence --------------------------------------------------------


def _value(a: attempts.Attempt) -> float:
    """The score of one attempt: its numeric payload `score` if it has one, else the result."""
    raw = a.payload.get("score")
    if isinstance(raw, (int, float)) and not isinstance(raw, bool) and 0 <= raw <= 1:
        return float(raw)
    return 1.0 if a.good else 0.0


def _attempt_entries(
    cat: Catalog, rows: list[attempts.Attempt]
) -> list[tuple[Evidence, dict[str, LinkTier]]]:
    slugs = _drill_slugs(cat)
    out: list[tuple[Evidence, dict[str, LinkTier]]] = []
    for a in rows:
        value = _value(a)
        lesson = a.payload.get("lesson")
        lesson = lesson if isinstance(lesson, str) else None
        concept = a.payload.get("concept")
        concept = concept if isinstance(concept, str) else None
        if a.kind == "flashcard":
            lesson = lesson or (a.scope if a.scope in cat.lessons else None)
            ev = Evidence("card", a.ts, value, "explicit", lesson, deck=a.scope)
        elif a.kind == "drill":
            lesson = a.item if a.item in cat.lessons else slugs.get(Path(a.item).name)
            label = f"{value * 100:.0f}%" if "score" in a.payload else a.result
            ev = Evidence("drill", a.ts, value, "explicit", lesson, score_label=label)
        elif a.kind == "voice_grade":
            lesson = lesson or (a.item if a.item in cat.lessons else None)
            if a.payload.get("mode") == "flashcard":
                ev = Evidence("card", a.ts, value, "explicit", lesson, deck=a.scope)
            else:
                label = f"{value * 100:.0f}% by voice"
                ev = Evidence("drill", a.ts, value, "explicit", lesson, score_label=label)
        elif a.kind == "concept_grade":
            kind: EvidenceKind = "card" if a.payload.get("source") == "card" else "drill"
            ev = Evidence(kind, a.ts, value, "explicit", lesson)
        else:
            continue
        out.append((ev, _linked(cat, lesson, concept)))
    return out


def _evidence_by_concept(
    user_id: str, cat: Catalog
) -> tuple[dict[str, list[Evidence]], dict[str, datetime]]:
    done = {
        lid: ts
        for lid, (state, ts) in progress.lessons(user_id).items()
        if state == "done" and _public(cat, lid) is not None
    }
    entries: list[tuple[Evidence, dict[str, LinkTier]]] = [
        (Evidence("lesson", ts, LESSON_VALUE, "explicit", lid), lesson_links(cat, cat.lessons[lid]))
        for lid, ts in done.items()
    ]
    entries += _attempt_entries(cat, attempts.attempts(user_id, KINDS))
    by_concept: dict[str, list[Evidence]] = {}
    for evidence, links in entries:
        for cid, link in links.items():
            by_concept.setdefault(cid, []).append(replace(evidence, link=link))
    return by_concept, done


def _scores(
    user_id: str, cat: Catalog, now: datetime
) -> tuple[dict[str, ConceptScore], dict[str, datetime]]:
    evidence, done = _evidence_by_concept(user_id, cat)
    scores = {cid: s for cid, ev in evidence.items() if (s := score_concept(ev, now)) is not None}
    return scores, done


def _module_bars(cat: Catalog, scores: dict[str, ConceptScore]) -> dict[str, dict[str, Any]]:
    """Per `<course>/<module>`: mean current strength (strength x recency) of its direct concepts.

    `strength` is null when none of the module's concepts has direct evidence: "no data" is not
    0%. Semantic links stay out of the mean on both sides.
    """
    concepts: dict[str, set[str]] = {}
    for rec in cat.lessons.values():
        if rec.private:
            continue
        direct = {c for c, tier in lesson_links(cat, rec).items() if tier == "explicit"}
        concepts.setdefault(f"{rec.course}/{rec.module}", set()).update(direct)
    bars: dict[str, dict[str, Any]] = {}
    for module, ids in concepts.items():
        seen = [scores[c] for c in ids if c in scores and scores[c].direct]
        current = sum(s.strength * s.recency for s in seen)
        bars[module] = {
            "strength": round(current / len(ids), 4) if seen else None,
            "concepts": len(ids),
            "withEvidence": len(seen),
        }
    return bars


def _wiki_json(ref: WikiRef) -> dict[str, str]:
    return {"id": ref.id, "title": ref.title, "summary": ref.summary, "domain": ref.domain}


def _mastery_json(s: ConceptScore) -> dict[str, Any]:
    return {
        "strength": round(s.strength, 4),
        "recency": round(s.recency, 4),
        "lastSeen": s.last.ts.isoformat(),
        "due": s.due,
        "evidence": "direct" if s.direct else "weak",
        "counts": s.counts,
    }


def build_state(user_id: str, cat: Catalog, now: datetime) -> dict[str, Any]:
    """Per concept, per module and the lessons done, for one user."""
    scores, done = _scores(user_id, cat, now)
    return {
        "concepts": {cid: _mastery_json(s) for cid, s in scores.items()},
        "modules": _module_bars(cat, scores),
        "lessonsDone": [lid for lid in cat.lessons if lid in done],
        # False while the cache is being built: an empty lessonsDone then means "don't know yet".
        "catalogReady": bool(cat.lessons),
    }


# -- The Due list ----------------------------------------------------------------------------

_LINK_LABEL = {"explicit": "linked page", "semantic": "similar text"}


def _ago(then: datetime, now: datetime) -> str:
    days = max(0, (now - then).days)
    return "today" if days == 0 else "1 day ago" if days == 1 else f"{days} days ago"


def _reason(cat: Catalog, score: ConceptScore, now: datetime) -> str:
    """Why this is due, naming the event behind it and how it is linked, so that a bad link shows
    up as a visibly wrong source."""
    last = score.last
    when = _ago(last.ts, now)
    if last.kind == "lesson":
        text = f"Lesson read {when}"
    elif last.kind == "card":
        text = f"Last flashcard {when}: {'knew it' if last.value >= PASS_AT else 'missed it'}"
    else:
        text = f"Last drilled {when}, score {last.score_label or f'{last.value * 100:.0f}%'}"
    rec = _public(cat, last.lesson)
    return f"{text}, via {rec.title} ({_LINK_LABEL[last.link]})" if rec else text


@dataclass(frozen=True)
class Spokes:
    lessons: list[LessonRec]
    drills: list[LessonRec]
    decks: list[dict[str, str]]


def _spokes(cat: Catalog, cid: str, last: Evidence | None = None) -> Spokes:
    """What links to a concept, strongest link first. Given the latest evidence, the lesson and
    deck behind it lead, so a cap can't drop the very thing a Due row is due because of."""
    rank = {"explicit": 0, "semantic": 1}
    linked = sorted(
        (r for lid in cat.by_concept.get(cid, []) if (r := _public(cat, lid)) is not None),
        key=lambda r: rank[lesson_links(cat, r).get(cid, "semantic")],
    )
    source = _public(cat, last.lesson) if last else None
    if source is not None:
        linked = [source, *(r for r in linked if r.id != source.id)]
    deck_ids = [r.id for r in linked if r.id in cat.decks]
    if last and source is None and last.deck in cat.decks and _card_in(cat, last.deck, "0"):
        deck_ids = [last.deck, *(d for d in deck_ids if d != last.deck)]
    return Spokes(
        lessons=[r for r in linked if r.kind != "drill"],
        drills=[r for r in linked if r.kind == "drill"],
        decks=[{"id": d, "title": cat.decks[d]["title"]} for d in deck_ids],
    )


def build_next(user_id: str, cat: Catalog, now: datetime, limit: int) -> list[dict[str, Any]]:
    """Due concepts, weakest first."""
    scores, _ = _scores(user_id, cat, now)
    due = sorted(
        ((cid, s) for cid, s in scores.items() if s.due and cid in cat.wiki),
        key=lambda item: (item[1].strength * item[1].recency, item[0]),
    )
    rows: list[dict[str, Any]] = []
    for cid, score in due[:limit]:
        spokes = _spokes(cat, cid, score.last)
        rows.append(
            {
                "concept": _wiki_json(cat.wiki[cid]),
                "strength": round(score.strength, 4),
                "due": True,
                "reason": _reason(cat, score, now),
                "lessons": [outline(r) for r in spokes.lessons][:NEXT_MAX_LINKS],
                "drills": [outline(r) for r in spokes.drills][:NEXT_MAX_LINKS],
                "decks": spokes.decks[:NEXT_MAX_LINKS],
            }
        )
    return rows


def build_concept(user_id: str, cat: Catalog, cid: str, now: datetime) -> dict[str, Any] | None:
    """A public wiki page and what links to it, with this user's mastery of it. None for a page
    that is private, tombstoned or unknown (all three look the same)."""
    ref = cat.wiki.get(cid)
    if ref is None:
        return None
    scores, _ = _scores(user_id, cat, now)
    score = scores.get(cid)
    spokes = _spokes(cat, cid)

    def spoke(r: LessonRec) -> dict[str, Any]:
        return {**outline(r), "course": r.course, "link": lesson_links(cat, r).get(cid)}

    return {
        **_wiki_json(ref),
        "mastery": _mastery_json(score) if score else None,
        "lessons": [spoke(r) for r in spokes.lessons],
        "drills": [spoke(r) for r in spokes.drills],
        "decks": spokes.decks,
        "catalogReady": bool(cat.lessons),
    }


# -- Writing ---------------------------------------------------------------------------------


def _result(score: float) -> str:
    return "pass" if score >= PASS_AT else "fail"


def record_event(user_id: str, body: EventIn, now: datetime | None = None) -> dict[str, Any]:
    """Store one event for `user_id`. `{"logged", "concepts"}`: `logged` is false (nothing stored)
    for a lesson or card the catalog does not have; an unknown drill or voice id is stored and
    counts for nothing. Raises LearningError when the store cannot be written."""
    cat = courses.catalog()
    now = now or utcnow()
    # A future timestamp would outrank later events for good, so it is treated as now.
    when = min(body.ts, now) if body.ts is not None else now
    ts = when.isoformat()
    score = body.score if body.score is not None else 0.0
    payload: dict[str, Any] = {"score": round(score, 4)}
    if body.concept:
        payload["concept"] = body.concept
    ok = True

    if body.kind == "lesson_done":
        lesson = body.lesson or ""
        if _public(cat, lesson) is None:
            return {"logged": False, "concepts": []}
        ok = progress.mark(user_id, lesson, "done")
        links = _linked(cat, lesson, None)
    elif body.kind == "card_grade" and body.deck and body.card:
        card = _card_in(cat, body.deck, body.card)
        if card is None or (card["lesson"] and _public(cat, card["lesson"]) is None):
            return {"logged": False, "concepts": []}
        payload |= {"lesson": card["lesson"], "source": "app", "front": card["front"]}
        result = "knew" if score >= PASS_AT else "missed"
        ok = attempts.record(
            user_id,
            "flashcard",
            leitner.card_key(body.deck, card["front"]),
            body.deck,
            result,
            payload=payload,
            ts=ts,
        )
        links = _linked(cat, card["lesson"], body.concept)
    elif body.kind == "card_grade":
        payload["source"] = "card"
        ok = attempts.record(
            user_id, "concept_grade", body.concept or "", body.concept or "", _result(score),
            payload=payload, ts=ts,
        )  # fmt: skip
        links = _linked(cat, None, body.concept)
    elif body.kind == "drill_attempt" and body.lesson:
        payload["source"] = "app"
        result = "pass" if score >= PASS_AT else "fail"
        ok = attempts.record(
            user_id, "drill", body.lesson, body.lesson, result, payload=payload, ts=ts
        )
        links = _linked(cat, body.lesson, body.concept)
    elif body.kind == "drill_attempt":
        payload["source"] = "drill"
        ok = attempts.record(
            user_id, "concept_grade", body.concept or "", body.concept or "", _result(score),
            payload=payload, ts=ts,
        )  # fmt: skip
        links = _linked(cat, None, body.concept)
    else:  # voice_grade
        item = body.lesson or body.deck or ""
        payload |= {"mode": body.mode}
        if body.lesson:
            payload["lesson"] = body.lesson
        ok = attempts.record(
            user_id, "voice_grade", item, body.deck or item, _result(score), payload=payload, ts=ts
        )
        links = _linked(cat, body.lesson, body.concept)

    if not ok:
        raise LearningError("could not record the event")
    return {"logged": True, "concepts": sorted(links)}


class ReconcileIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    done: list[str] = Field(max_length=5000)


def reconcile(user_id: str, body: ReconcileIn) -> dict[str, list[str]]:
    """Merge a browser's locally stored done marks. Safe to repeat: a lesson already done stays
    done. Only ids in the public catalog are recorded; `resolved` are safe for the browser to
    forget, `unresolved` it must keep (during a cache build every id is unresolved)."""
    cat = courses.catalog()
    known = {i: bool(ID_RE.match(i)) and _public(cat, i) is not None for i in body.done}
    resolved = [i for i, ok in known.items() if ok]
    unresolved = [i for i, ok in known.items() if not ok]
    already = progress.lessons(user_id)
    for lid in resolved:
        if already.get(lid, ("", utcnow()))[0] != "done" and not progress.mark(
            user_id, lid, "done"
        ):
            raise LearningError("could not record the events")
    return {"resolved": resolved, "unresolved": unresolved}
