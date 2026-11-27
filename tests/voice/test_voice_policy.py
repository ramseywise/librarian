"""D10: who may run where is read from the server's catalog, and it fails closed."""

from __future__ import annotations

from dataclasses import replace

import pytest
from pydantic import ValidationError
from voice_fakes import REFERENCE_QUOTE, make_catalog

from librarian.courses.loader import Catalog
from librarian.voice.config import VoiceConfig, load_config
from librarian.voice.policy import Refusal, SessionPlan, SessionRequest, resolve_session

CATALOG = make_catalog()
HOSTED = VoiceConfig(stt_provider="openai", tts_provider="openai", hosted_key_set=True)


def _plan(cfg: VoiceConfig | None = None, **body: object) -> SessionPlan:
    return resolve_session(SessionRequest(**body), CATALOG, cfg or VoiceConfig())  # type: ignore[arg-type]


LOCAL_ONLY = [
    {"mode": "interview", "lesson": "interviewing/m/tell-me"},
    {"mode": "interview", "lesson": "interviewing/m/drill"},
    {"mode": "approach", "lesson": "interviewing/m/drill"},  # a mode that doesn't name the course
    {"mode": "flashcard", "deck": "interviewing/m"},
    {"mode": "flashcard", "deck": "maths/borrowed"},  # a public deck, but its card isn't
]


@pytest.mark.parametrize("body", LOCAL_ONLY)
def test_interviewing_stays_local_even_with_hosted_configured(body: dict) -> None:
    plan = _plan(HOSTED, **body)
    assert (plan.local_only, plan.stt, plan.tts) == (True, "local", "local")


@pytest.mark.parametrize(
    "body",
    [{"mode": "approach", "lesson": "maths/m/drill"}, {"mode": "flashcard", "deck": "maths/m"}],
)
def test_the_default_for_every_other_mode_is_local_too(body: dict) -> None:
    key_but_no_choice = VoiceConfig(hosted_key_set=True)
    plan = _plan(key_but_no_choice, **body)
    assert (plan.local_only, plan.stt, plan.tts) == (False, "local", "local")


def test_hosted_needs_both_the_setting_and_the_key() -> None:
    assert _plan(HOSTED, mode="flashcard", deck="maths/m").stt == "openai"
    no_key = VoiceConfig(stt_provider="openai")
    with pytest.raises(Refusal) as refused:
        _plan(no_key, mode="flashcard", deck="maths/m")
    assert refused.value.status == 503


def test_an_unknown_provider_is_refused_rather_than_guessed() -> None:
    with pytest.raises(Refusal):
        _plan(VoiceConfig(stt_provider="whatever"), mode="flashcard", deck="maths/m")


@pytest.mark.parametrize(
    "extra", [{"stt": "openai"}, {"localOnly": False}, {"course": "maths"}, {"provider": "openai"}]
)
def test_a_crafted_request_cannot_carry_its_own_routing(extra: dict) -> None:
    with pytest.raises(ValidationError):
        SessionRequest(mode="interview", lesson="interviewing/m/tell-me", **extra)


@pytest.mark.parametrize(
    "lesson_id",
    [
        "INTERVIEWING/m/tell-me",
        "interviewing/m/tell-me/",
        "./interviewing/m/tell-me",
        "interviewing//m",
    ],
)
def test_other_spellings_of_an_interviewing_id_reach_nothing(lesson_id: str) -> None:
    with pytest.raises(Refusal) as refused:
        _plan(HOSTED, mode="approach", lesson=lesson_id)
    assert refused.value.status == 404


@pytest.mark.parametrize(
    "body, status",
    [
        ({"mode": "interview", "lesson": "maths/m/a"}, 422),  # interview only on that course
        ({"mode": "approach", "lesson": "maths/m/a"}, 422),  # not a drill
        ({"mode": "approach", "lesson": "maths/m/odd-drill"}, 422),  # shape not recognised
        ({"mode": "approach", "lesson": "maths/m/gone"}, 404),
        ({"mode": "flashcard", "deck": "maths/gone"}, 404),
        ({"mode": "flashcard", "deck": "maths/empty"}, 422),
        ({"mode": "flashcard"}, 400),
        ({"mode": "approach"}, 400),
        ({"mode": "flashcard", "deck": "maths/m", "lesson": "maths/m/a"}, 400),
        ({"mode": "approach", "lesson": "maths/m/drill", "deck": "maths/m"}, 400),
    ],
)
def test_refusals(body: dict, status: int) -> None:
    with pytest.raises(Refusal) as refused:
        _plan(**body)
    assert refused.value.status == status


def test_approach_says_the_prompt_and_only_holds_the_rest_as_reference() -> None:
    plan = _plan(mode="approach", lesson="maths/m/drill")
    assert "lanterns" in plan.prompt
    assert REFERENCE_QUOTE not in plan.prompt
    assert "running tally" not in plan.prompt
    assert REFERENCE_QUOTE in plan.reference


def test_the_defaults_need_no_env_at_all() -> None:
    cfg = load_config({})
    assert (cfg.stt_provider, cfg.tts_provider, cfg.hosted_key_set) == ("local", "local", False)
    assert cfg.max_turns > 0
    assert cfg.max_tokens > 0


def test_model_setting_follows_the_repo_convention_and_can_be_overridden() -> None:
    from librarian.config import get_settings

    assert load_config({}).model == get_settings().chat_model
    assert load_config({"VOICE_MODEL": "m-v"}).model == "m-v"


@pytest.mark.parametrize("raw", ["soon", "0", "-1"])
def test_a_bad_limit_stops_startup(raw: str) -> None:
    with pytest.raises(ValueError, match="VOICE_MAX_DURATION_S"):
        load_config({"VOICE_MAX_DURATION_S": raw})


# ── Private content never reaches a voice session ────────────────────────────


def _private_catalog() -> Catalog:
    cat = make_catalog()
    cat.lessons["maths/m/drill"] = replace(cat.lessons["maths/m/drill"], private=True)
    cat.lessons["maths/m/hidden"] = replace(
        cat.lessons["maths/m/a"], id="maths/m/hidden", private=True
    )
    cat.decks["private/maths/m"] = cat.decks["maths/m"]
    cat.decks["maths/leaky"] = {
        "id": "maths/leaky",
        "title": "Leaky",
        "course": "maths",
        "cards": [{"front": "Q?", "back": "A.", "lesson": "maths/m/hidden"}],
    }
    return cat


@pytest.mark.parametrize(
    "body",
    [
        {"mode": "approach", "lesson": "maths/m/drill"},
        {"mode": "approach", "lesson": "private/maths/m/drill"},
        {"mode": "flashcard", "deck": "private/maths/m"},
        {"mode": "flashcard", "deck": "maths/leaky"},  # its only card is a private lesson's
    ],
)
def test_private_lessons_and_decks_are_refused(body: dict) -> None:
    with pytest.raises(Refusal) as err:
        resolve_session(SessionRequest(**body), _private_catalog(), VoiceConfig())
    assert err.value.status in {404, 422}
