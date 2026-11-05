"""Leitner scheduling for flashcards, replayed from the self-grade log.

Pure functions over the records `POST /api/courses/flashcard-results` appends to
logs/flashcards.jsonl. Nothing is stored but the log: a card's box and due date are
recomputed from it on every read.

Rules: five boxes reviewed every 1, 2, 4, 8 and 16 days. "knew" moves a card up one box and a
miss returns it to box 1. A "knew" before the due date reschedules nothing, so studying a deck
twice in one sitting cannot walk a card to box 5.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from shared.log_config import get_logger

log = get_logger(__name__)

BOX_DAYS = (1, 2, 4, 8, 16)
CARD_KEY_HASH_CHARS = 16
GRADES = ("knew", "missed")

Status = Literal["new", "due", "later"]


@dataclass(frozen=True)
class CardState:
    box: int
    due_on: date


def card_key(deck: str, front: str) -> str:
    """Identity of a card across decks and edits to its neighbours.

    The API's card id is the card's position in its deck, which shifts when a deck is edited,
    and old log records never had it. The module (first two segments of the deck id) and the
    front text are in every record, and a module's lesson decks share its cards, so a card keeps
    one schedule however it was studied. Editing a card's front makes it a new card.
    """
    module = "/".join(deck.split("/")[:2])
    digest = hashlib.sha256(front.encode("utf-8")).hexdigest()[:CARD_KEY_HASH_CHARS]
    return f"{module}:{digest}"


def _timestamp(raw: object) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        ts = datetime.fromisoformat(raw)
    except ValueError:
        return None
    ts = ts if ts.tzinfo else ts.replace(tzinfo=UTC)
    try:
        # A date at the end of the calendar has no local day, or no due date after it.
        ts.astimezone().date() + timedelta(days=max(BOX_DAYS))
    except (OverflowError, OSError):
        return None
    return ts


def _review(rec: object) -> tuple[datetime, str, str] | None:
    """(when, card key, grade) from one log record, or None when a field can't be read."""
    if not isinstance(rec, dict):
        return None
    ts = _timestamp(rec.get("ts"))
    grade = rec.get("result")
    if ts is None or grade not in GRADES:
        return None
    key = rec.get("card")
    if not isinstance(key, str) or not key:
        deck, front = rec.get("deck"), rec.get("front")
        if not isinstance(deck, str) or not isinstance(front, str):
            return None
        key = card_key(deck, front)
    return ts, key, grade


def _next_state(state: CardState | None, grade: str, day: date) -> CardState:
    if grade == "missed":
        return CardState(1, day + timedelta(days=BOX_DAYS[0]))
    if state is None:
        box = 2
    elif day < state.due_on:
        return state
    else:
        box = min(state.box + 1, len(BOX_DAYS))
    return CardState(box, day + timedelta(days=BOX_DAYS[box - 1]))


def replay(records: list[Any]) -> dict[str, CardState]:
    """Each card's state after its reviews in time order. Unreadable records are skipped."""
    reviews = [review for rec in records if (review := _review(rec))]
    skipped = len(records) - len(reviews)
    if skipped:
        log.warning("flashcards.log_records_skipped", count=skipped)
    states: dict[str, CardState] = {}
    for ts, key, grade in sorted(reviews, key=lambda r: r[0]):
        states[key] = _next_state(states.get(key), grade, ts.astimezone().date())
    return states


def load_states(path: Path) -> dict[str, CardState]:
    """Replay the log at `path`. A missing or unreadable log means every card is new."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError) as e:
        log.warning("flashcards.log_unreadable", error=str(e))
        return {}
    records: list[Any] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append(None)
    return replay(records)


def status_of(state: CardState | None, today: date) -> Status:
    if state is None:
        return "new"
    return "due" if state.due_on <= today else "later"
