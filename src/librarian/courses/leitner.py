"""Leitner scheduling for flashcards and quiz questions, replayed from the attempts store.

Pure functions over the graded events in `librarian.courses.attempts` (flashcard self-grades and
multiple-choice answers; drill runs are not scheduled). Nothing is stored but those events: an
item's box and due date are recomputed from them on every read. A wrong answer is a miss, so a
question comes back through the same queue as a card.

Rules: five boxes reviewed every 1, 2, 4, 8 and 16 days. "knew" moves a card up one box and a
miss returns it to box 1. A "knew" before the due date reschedules nothing, so studying a deck
twice in one sitting cannot walk a card to box 5.

Days are the user's calendar days (`users.timezone`), so a card graded at 23:30 in Lisbon is due
on the user's tomorrow, not the server's.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from librarian.accounts import User
from librarian.courses import attempts
from librarian.log_config import get_logger

log = get_logger(__name__)

BOX_DAYS = (1, 2, 4, 8, 16)
CARD_KEY_HASH_CHARS = 16
SCHEDULED_KINDS = ("flashcard", "mcq")

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
    one schedule however it was studied. A `private/` prefix is ignored, so a lesson's cards
    are the same in either tree. Editing a card's front makes it a new card.
    """
    module = "/".join(deck.removeprefix("private/").split("/")[:2])
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
        # A date at the end of the calendar has no day in every zone, or no due date after it.
        _ = (ts.astimezone(UTC) + timedelta(days=1)).date() + timedelta(days=max(BOX_DAYS))
    except (OverflowError, OSError):
        return None
    return ts


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


def zone(name: str) -> ZoneInfo:
    """The zone `name`, or UTC when it is not a zone this machine knows."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        log.warning("leitner.unknown_timezone", timezone=name)
        return ZoneInfo("UTC")


def today(user: User) -> date:
    """The date it is now where `user` is."""
    return datetime.now(zone(user.timezone)).date()


def _fold(reviews: Iterable[tuple[datetime, str, str]], tz: ZoneInfo) -> dict[str, CardState]:
    states: dict[str, CardState] = {}
    for ts, key, grade in sorted(reviews, key=lambda r: r[0]):
        states[key] = _next_state(states.get(key), grade, ts.astimezone(tz).date())
    return states


def states_from(rows: Iterable[attempts.Attempt], timezone: str = "UTC") -> dict[str, CardState]:
    """Each item's state after its flashcard and question attempts in time order, by `timezone`'s days."""
    reviews = [
        (a.ts, a.item, "knew" if a.good else "missed")
        for a in rows
        if a.kind in SCHEDULED_KINDS and _timestamp(a.ts.isoformat()) is not None
    ]
    return _fold(reviews, zone(timezone))


def load_states(user: User) -> dict[str, CardState]:
    """`user`'s schedule as of now. An empty or unreadable store means every item is new."""
    return states_from(attempts.attempts(user.id, SCHEDULED_KINDS), user.timezone)


def status_of(state: CardState | None, today: date) -> Status:
    if state is None:
        return "new"
    return "due" if state.due_on <= today else "later"
