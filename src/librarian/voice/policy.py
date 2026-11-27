"""Which session may run, on which speech services, decided here from the server's own catalog.

D10: interviewing stays on this machine. Whether a session is local-only is read from the lesson
or deck the catalog holds, never from a value the client sends: the request model forbids extra
fields, so `{"stt": "openai"}` is a 422, and an id is looked up exactly, so no other spelling
reaches a lesson while dodging the rule. Hosted speech is opt-in by env key, for non-interviewing
content only, and nothing ever falls back to it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .config import VoiceConfig
from .drill_prompt import drill_prompt, visible_text

if TYPE_CHECKING:
    from librarian.courses.loader import Catalog, LessonRec

Mode = Literal["flashcard", "approach", "interview"]

# Keep in step with LOCAL_ONLY_COURSES in app/frontend/src/voice/policy.ts.
LOCAL_ONLY_COURSES = frozenset({"interviewing"})
HOSTED_PROVIDER = "openai"
LOCAL_PROVIDER = "local"
MAX_REFERENCE_CHARS = 6_000
MAX_MATERIAL_CHARS = 8_000


class Refusal(Exception):  # noqa: N818  - not an error: a decision the user is told about
    """This session will not start. `message` is shown to the user as it stands."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


class SessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: Mode
    lesson: str | None = Field(default=None, max_length=512)
    deck: str | None = Field(default=None, max_length=512)


@dataclass(frozen=True)
class Card:
    front: str
    back: str
    lesson: str | None = None


@dataclass(frozen=True)
class SessionPlan:
    mode: Mode
    title: str
    local_only: bool
    stt: str = LOCAL_PROVIDER
    tts: str = LOCAL_PROVIDER
    lesson: str | None = None
    deck: str | None = None
    cards: tuple[Card, ...] = ()
    prompt: str = ""  # safe to say aloud
    reference: str = ""  # for the model to critique against, never to say
    material: str = ""  # a lesson's visible prose, to ask interview questions from
    user_id: str | None = None  # whose grades these are; None is the owner


def is_local_only_course(course: str | None) -> bool:
    return (course or "").strip().casefold() in LOCAL_ONLY_COURSES


def _is_local_only_id(item_id: str) -> bool:
    return is_local_only_course(item_id.split("/", 1)[0])


def choose_provider(setting: str, *, local_only: bool, hosted_key_set: bool, what: str) -> str:
    """Local unless hosted was asked for by env key, and always local when it must be."""
    if local_only or setting == LOCAL_PROVIDER:
        return LOCAL_PROVIDER
    if setting != HOSTED_PROVIDER:
        raise Refusal(400, f"Unknown {what} provider in the voice settings.")
    if not hosted_key_set:
        raise Refusal(503, f"Hosted {what} is selected but its API key is not set.")
    return HOSTED_PROVIDER


def _is_private_id(cat: Catalog, item_id: str | None) -> bool:
    """Private content never reaches a drill prompt: it is local to the owner's wiki tooling."""
    if not item_id:
        return False
    rec = cat.lessons.get(item_id)
    return item_id.startswith("private/") or (rec is not None and rec.private)


def _flashcard_plan(req: SessionRequest, cat: Catalog) -> dict[str, Any]:
    if not req.deck:
        raise Refusal(400, "Flashcard voice needs a deck.")
    if req.lesson:
        raise Refusal(400, "Flashcard voice takes a deck and no lesson.")
    # A private deck, or one holding a private lesson's card, is answered as if it did not exist.
    deck = None if _is_private_id(cat, req.deck) else cat.decks.get(req.deck)
    if deck is None:
        raise Refusal(404, "That flashcard deck does not exist.")
    cards = tuple(
        Card(str(c.get("front", "")), str(c.get("back", "")), c.get("lesson"))
        for c in deck.get("cards", [])
        if str(c.get("front", "")).strip()
        and str(c.get("back", "")).strip()
        and not _is_private_id(cat, c.get("lesson"))
    )
    if not cards:
        raise Refusal(422, "That deck has no cards to study.")
    # A deck, or any card in it, that draws on a local-only course makes the session local-only.
    card_courses = (getattr(cat.lessons.get(c.lesson or ""), "course", None) for c in cards)
    local_only = (
        is_local_only_course(deck.get("course"))
        or _is_local_only_id(req.deck)
        or any(is_local_only_course(course) for course in card_courses)
    )
    return {
        "title": str(deck.get("title", "")),
        "deck": req.deck,
        "cards": cards,
        "local_only": local_only,
    }


def _lesson(req: SessionRequest, cat: Catalog, mode_name: str) -> LessonRec:
    if not req.lesson:
        raise Refusal(400, f"{mode_name} needs a lesson.")
    if req.deck:
        raise Refusal(400, f"{mode_name} takes a lesson and no deck.")
    rec = cat.lessons.get(req.lesson)
    if rec is None or rec.private or req.lesson.startswith("private/"):
        raise Refusal(404, "That lesson does not exist.")
    return rec


def _approach_plan(req: SessionRequest, cat: Catalog) -> dict[str, Any]:
    rec = _lesson(req, cat, "Explain your approach")
    if rec.kind != "drill":
        raise Refusal(422, "Explain your approach works on drills only.")
    drill = drill_prompt(rec.body)
    if not drill.ok:
        raise Refusal(422, f"This drill can't be used by voice: {drill.reason}.")
    return {
        "title": rec.title,
        "lesson": rec.id,
        "prompt": drill.text,
        "reference": drill.withheld[:MAX_REFERENCE_CHARS],
        "local_only": is_local_only_course(rec.course) or _is_local_only_id(rec.id),
    }


def _interview_plan(req: SessionRequest, cat: Catalog) -> dict[str, Any]:
    rec = _lesson(req, cat, "Interview practice")
    if not (is_local_only_course(rec.course) and _is_local_only_id(rec.id)):
        raise Refusal(422, "Interview practice works on the interviewing course only.")
    if rec.kind == "drill":
        drill = drill_prompt(rec.body)
        if not drill.ok:
            raise Refusal(422, f"This drill can't be used by voice: {drill.reason}.")
        material = drill.text
    else:
        material = visible_text(rec.body)
    if not material:
        raise Refusal(422, "This lesson has nothing to ask questions from.")
    return {"title": rec.title, "lesson": rec.id, "material": material[:MAX_MATERIAL_CHARS]}


def resolve_session(req: SessionRequest, cat: Catalog, cfg: VoiceConfig) -> SessionPlan:
    """A plan for this request, or a `Refusal` that says why not."""
    if req.mode == "flashcard":
        fields = _flashcard_plan(req, cat)
    elif req.mode == "approach":
        fields = _approach_plan(req, cat)
    else:
        fields = {**_interview_plan(req, cat), "local_only": True}
    local_only = fields["local_only"]
    stt = choose_provider(
        cfg.stt_provider, local_only=local_only, hosted_key_set=cfg.hosted_key_set, what="speech"
    )
    tts = choose_provider(
        cfg.tts_provider, local_only=local_only, hosted_key_set=cfg.hosted_key_set, what="voice"
    )
    return SessionPlan(mode=req.mode, stt=stt, tts=tts, **fields)
