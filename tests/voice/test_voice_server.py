"""The voice process's slot and refusals, and the API's broker, with no Pipecat and no microphone."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from voice_fakes import make_catalog

from librarian.api.routers import voice as voice_broker
from librarian.api.security import require_user
from librarian.voice.config import VoiceConfig
from librarian.voice.server import create_app, host_allowed

ORIGIN = "http://localhost:5173"
DECK = {"mode": "flashcard", "deck": "maths/m"}
INTERVIEW = {"mode": "interview", "lesson": "interviewing/m/tell-me"}


class FakeLive:
    def __init__(self) -> None:
        self.closed = 0
        self.offers: list[dict] = []
        self.ice_calls: list[dict] = []
        self.offer_error: Exception | None = None

    async def offer(self, body: dict[str, Any]) -> dict[str, Any]:
        self.offers.append(body)
        if self.offer_error is not None:
            raise self.offer_error
        return {"sdp": "answer", "type": "answer", "pc_id": "pc"}

    async def ice(self, body: dict[str, Any]) -> None:
        self.ice_calls.append(body)

    async def close(self) -> None:
        self.closed += 1


class Rig:
    def __init__(self, cfg: VoiceConfig | None = None, **state: str) -> None:
        self.models = SimpleNamespace(
            stt=state.get("stt", "ready"), tts=state.get("tts", "ready"), start_loading=lambda: None
        )
        self.lives: list[FakeLive] = []
        self.plans: list[Any] = []
        self.ends: list[Callable[[], None]] = []
        self.clock = 0.0
        app = create_app(
            cfg or VoiceConfig(),
            self.models,
            self._factory,
            catalog=make_catalog,
            now=lambda: self.clock,  # type: ignore[arg-type]
        )
        self.client = TestClient(app, base_url="http://localhost")

    def _factory(self, plan: object, on_end: Callable[[], None]) -> FakeLive:
        live = FakeLive()
        self.plans.append(plan)
        self.lives.append(live)
        self.ends.append(on_end)
        return live


@pytest.fixture(autouse=True)
def _api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-real-key")


def test_the_session_is_planned_for_the_user_the_broker_names() -> None:
    rig = Rig()
    assert (
        rig.client.post("/session", json=DECK, headers={"x-librarian-user": "u-9"}).status_code
        == 200
    )
    assert rig.plans[0].user_id == "u-9"


def test_opening_gives_the_broker_path_and_says_where_speech_runs() -> None:
    rig = Rig()
    body = rig.client.post("/session", json=INTERVIEW).json()
    assert body["offer"] == f"/api/voice/session/{body['sessionId']}/offer"
    assert (body["mode"], body["localOnly"], body["stt"], body["tts"]) == (
        "interview",
        True,
        "local",
        "local",
    )


@pytest.mark.parametrize(
    "state, word",
    [
        ({"stt": "failed"}, "failed"),
        ({"stt": "loading"}, "loading"),
        ({"tts": "failed"}, "failed"),
        ({"tts": "loading"}, "loading"),
    ],
)
@pytest.mark.parametrize("body", [INTERVIEW, DECK])
def test_no_local_model_no_session(state: dict, word: str, body: dict) -> None:
    """Fails closed, with the hosted key set and hosted configured: there is no fallback path."""
    rig = Rig(VoiceConfig(hosted_key_set=True), **state)
    res = rig.client.post("/session", json=body)
    assert res.status_code == 503
    assert word in res.json()["detail"]
    assert rig.lives == []


def test_hosted_opt_in_does_not_wait_for_local_models_it_will_not_use() -> None:
    cfg = VoiceConfig(stt_provider="openai", tts_provider="openai", hosted_key_set=True)
    rig = Rig(cfg, stt="failed", tts="failed")
    assert rig.client.post("/session", json=DECK).json()["stt"] == "openai"


def test_interviewing_with_hosted_configured_and_local_failed_still_refuses() -> None:
    cfg = VoiceConfig(stt_provider="openai", tts_provider="openai", hosted_key_set=True)
    rig = Rig(cfg, stt="failed")
    res = rig.client.post("/session", json=INTERVIEW)
    assert res.status_code == 503
    assert "rather than sending" in res.json()["detail"]
    assert rig.lives == []


def test_a_crafted_provider_field_is_refused() -> None:
    res = Rig().client.post("/session", json={**INTERVIEW, "stt": "openai"})
    assert res.status_code == 422


def test_a_missing_api_key_refuses_before_a_session_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    rig = Rig()
    res = rig.client.post("/session", json=DECK)
    assert res.status_code == 503
    assert "ANTHROPIC_API_KEY" in res.json()["detail"]
    assert rig.lives == []


def test_one_session_at_a_time_and_ending_frees_the_slot() -> None:
    rig = Rig()
    first = rig.client.post("/session", json=DECK).json()["sessionId"]
    assert rig.client.post("/session", json=DECK).status_code == 409
    assert rig.client.delete(f"/session/{first}").json() == {"ended": True}
    assert rig.lives[0].closed == 1
    assert rig.client.post("/session", json=DECK).status_code == 200


def test_ending_twice_or_with_a_stale_id_touches_nothing_else() -> None:
    rig = Rig()
    session = rig.client.post("/session", json=DECK).json()["sessionId"]
    assert rig.client.delete("/session/not-this-one").status_code == 200
    assert rig.lives[0].closed == 0
    rig.client.delete(f"/session/{session}")
    rig.client.delete(f"/session/{session}")
    assert rig.lives[0].closed == 1


def test_a_session_ending_by_itself_frees_the_slot() -> None:
    rig = Rig()
    rig.client.post("/session", json=DECK)
    rig.ends[0]()
    assert rig.client.get("/status").json()["sessionActive"] is False


def test_an_abandoned_reservation_gives_way_after_the_timeout() -> None:
    rig = Rig(VoiceConfig(offer_timeout_s=30))
    rig.client.post("/session", json=DECK)
    rig.clock = 29.0
    assert rig.client.post("/session", json=DECK).status_code == 409
    rig.clock = 31.0
    assert rig.client.post("/session", json=DECK).status_code == 200
    assert rig.lives[0].closed == 1


def test_a_connected_session_is_not_treated_as_abandoned() -> None:
    rig = Rig(VoiceConfig(offer_timeout_s=30))
    session = rig.client.post("/session", json=DECK).json()["sessionId"]
    assert rig.client.post(f"/session/{session}/offer", json={"sdp": "x"}).status_code == 200
    rig.clock = 1000.0
    assert rig.client.post("/session", json=DECK).status_code == 409


def test_a_second_offer_cannot_take_over_but_a_restart_can() -> None:
    rig = Rig()
    session = rig.client.post("/session", json=DECK).json()["sessionId"]
    url = f"/session/{session}/offer"
    assert rig.client.post(url, json={"sdp": "x"}).json()["sdp"] == "answer"
    assert rig.client.post(url, json={"sdp": "evil"}).status_code == 409
    assert (
        rig.client.post(url, json={"sdp": "x", "restart_pc": True, "pc_id": "pc"}).status_code
        == 200
    )


def test_an_offer_for_another_session_is_not_found() -> None:
    rig = Rig()
    rig.client.post("/session", json=DECK)
    assert rig.client.post("/session/guess/offer", json={"sdp": "x"}).status_code == 404
    assert rig.client.patch("/session/guess/offer", json={}).status_code == 404


def test_a_refused_offer_closes_the_session_and_frees_the_slot() -> None:
    from librarian.voice.policy import Refusal

    rig = Rig()
    session = rig.client.post("/session", json=DECK).json()["sessionId"]
    rig.lives[0].offer_error = Refusal(503, "no speech models")
    res = rig.client.post(f"/session/{session}/offer", json={"sdp": "x"})
    assert (res.status_code, res.json()["detail"]) == (503, "no speech models")
    assert rig.lives[0].closed == 1
    assert rig.client.get("/status").json()["sessionActive"] is False


@pytest.mark.parametrize(
    "headers, status",
    [
        ({"origin": ORIGIN}, 200),
        ({"origin": "http://127.0.0.1:5173"}, 200),
        ({"origin": "http://evil.test"}, 403),
        ({"origin": "http://localhost:9999"}, 403),
        ({"origin": "null"}, 403),
        ({"host": "evil.test"}, 403),
        ({"host": "localhost.evil.test:8200"}, 403),
        ({"host": "localhost:8200"}, 200),
        ({"host": "127.0.0.1:8200"}, 200),
    ],
)
def test_only_this_machine_and_the_apps_own_origin(headers: dict, status: int) -> None:
    rig = Rig()
    assert rig.client.get("/status", headers=headers).status_code == status
    res = rig.client.post("/session", json=DECK, headers=headers)
    assert res.status_code == status
    assert bool(rig.lives) == (status == 200)


@pytest.mark.parametrize("host", [None, "", "evil.test", "localhost@evil.test"])
def test_host_allowed_rejects(host: str | None) -> None:
    assert not host_allowed(host)


def test_the_server_binds_loopback_only() -> None:
    from librarian.voice import config

    assert config.HOST == "127.0.0.1"


# ── The broker, in the API ───────────────────────────────────────────────────


def _broker_client() -> TestClient:
    app = FastAPI()
    app.include_router(voice_broker.router)
    app.dependency_overrides[require_user] = lambda: SimpleNamespace(id="user-7")
    return TestClient(app, base_url="http://localhost")


def _dead_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VOICE_URL", "http://127.0.0.1:1")


@pytest.mark.parametrize(
    "method, path",
    [
        ("GET", "/api/voice/status"),
        ("POST", "/api/voice/session"),
        ("POST", "/api/voice/session/abc/offer"),
        ("PATCH", "/api/voice/session/abc/offer"),
        ("DELETE", "/api/voice/session/abc"),
    ],
)
def test_voice_not_running_is_one_clear_503(
    method: str, path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    _dead_port(monkeypatch)
    kwargs = {"json": DECK} if method in {"POST", "PATCH"} else {}
    res = _broker_client().request(method, path, **kwargs)
    assert res.status_code == 503
    assert res.json() == {"detail": "voice server not running, start with make voice"}


@pytest.mark.parametrize(
    "headers",
    [
        {"origin": "http://evil.test"},
        {"origin": "null"},
        {"host": "evil.test"},
        {"host": "localhost.evil.test"},
    ],
)
def test_the_broker_refuses_a_foreign_page_before_forwarding(
    headers: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[httpx.Request] = []
    _patch_voice(monkeypatch, calls, 200, {})
    res = _broker_client().post("/api/voice/session", json=DECK, headers=headers)
    assert res.status_code == 403
    assert calls == []


def _patch_voice(
    monkeypatch: pytest.MonkeyPatch, calls: list[httpx.Request], status: int, payload: object
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(status, json=payload)

    real = httpx.AsyncClient

    def fake(**kwargs: float) -> httpx.AsyncClient:
        return real(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(voice_broker.httpx, "AsyncClient", fake)


def test_the_broker_passes_refusals_through_and_sends_no_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[httpx.Request] = []
    _patch_voice(monkeypatch, calls, 422, {"detail": "that drill is not recognised"})
    res = _broker_client().post("/api/voice/session", json=DECK, headers={"origin": ORIGIN})
    assert res.status_code == 422
    assert res.json()["detail"] == "that drill is not recognised"
    assert json.loads(calls[0].content) == DECK
    assert "origin" not in calls[0].headers
    assert str(calls[0].url).endswith("/session")


def test_the_broker_tells_the_voice_server_who_is_signed_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[httpx.Request] = []
    _patch_voice(monkeypatch, calls, 200, {"session_id": "s"})
    _broker_client().post("/api/voice/session", json=DECK, headers={"origin": ORIGIN})
    assert calls[0].headers["x-librarian-user"] == "user-7"


def test_the_real_api_routes_the_broker(monkeypatch: pytest.MonkeyPatch) -> None:
    from librarian.api.main import app

    _dead_port(monkeypatch)
    client = TestClient(app, base_url="http://localhost")
    assert (
        client.post("/api/voice/session", json=DECK).status_code == 503
    )  # open mode: the owner is signed in


def test_importing_the_api_loads_neither_the_voice_process_nor_pipecat() -> None:
    code = (
        "import sys, librarian.api.main; "
        "bad = [m for m in sys.modules if m.startswith(('librarian.voice', 'pipecat', 'faster_whisper'))];"
        "sys.exit(repr(bad) if bad else 0)"
    )
    root = Path(__file__).resolve().parents[2]
    env = {**os.environ, "LIBRARIAN_SKIP_WARMUP": "1"}
    done = subprocess.run(
        [sys.executable, "-c", code], cwd=root, env=env, capture_output=True, text=True, timeout=120
    )
    assert done.returncode == 0, done.stderr[-2000:]
