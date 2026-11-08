"""GET /metrics, the request histograms, the chat first-token metric and GET /api/admin/spend."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from collections.abc import AsyncIterator, Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian import accounts
from librarian.api import prom_env
from librarian.api.routers import chat as chat_router
from librarian.api.security import chat_limiter
from librarian.config import get_settings
from librarian.db import get_engine
from librarian.pricing import TokenUsage

TOKEN = "bootstrap-token-0123456789abcdef"
METRICS = "metrics-token-0123456789abcdef"
ADMIN = {"Authorization": f"Bearer {TOKEN}"}
SCRAPE = {"Authorization": f"Bearer {METRICS}"}


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    monkeypatch.setenv("LIBRARIAN_METRICS_TOKEN", METRICS)
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")  # $10 per million output tokens
    monkeypatch.setenv("LIBRARIAN_OWNER_EMAIL", "owner@example.com")
    get_settings.cache_clear()
    chat_limiter.reset()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()
    chat_limiter.reset()


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(main_module.app) as c:
        yield c


def _scrape(client: TestClient) -> str:
    r = client.get("/metrics", headers=SCRAPE)
    assert r.status_code == 200, r.text
    return r.text


def _sample(text: str, prefix: str) -> float:
    """The value of the first sample line starting with `prefix` (name and labels)."""
    for line in text.splitlines():
        if line.startswith(prefix):
            return float(line.rsplit(" ", 1)[1])
    raise AssertionError(f"no sample {prefix!r} in:\n{text}")


def test_metrics_is_404_without_a_configured_token(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_METRICS_TOKEN", "")
    get_settings.cache_clear()
    assert client.get("/metrics", headers=SCRAPE).status_code == 404


def test_metrics_needs_the_metrics_token_not_a_user_credential(client: TestClient) -> None:
    assert client.get("/metrics").status_code == 401
    assert client.get("/metrics", headers={"Authorization": "Bearer nope"}).status_code == 401
    # The bootstrap (owner) token is not the scraper's token.
    assert client.get("/metrics", headers=ADMIN).status_code == 401
    assert client.get("/metrics", headers=SCRAPE).status_code == 200


def test_requests_are_counted_by_route_template_not_raw_path(client: TestClient) -> None:
    before = _scrape(client)
    client.get("/api/courses/lessons/no/such/lesson", headers=ADMIN)  # 404 through the router
    client.get("/api/courses/lessons/another/missing", headers=ADMIN)
    client.get("/healthz")
    text = _scrape(client)
    route = 'route="/api/courses/lessons/{lesson_id:path}"'
    assert "no/such" not in text
    key = f'librarian_http_requests_total{{method="GET",{route},status="404"}}'
    assert _sample(text, key) - (_sample(before, key) if key in before else 0) == 2
    assert 'route="/healthz"' in text
    assert "/metrics" not in text.replace("librarian_", "")  # the scrape itself is not counted
    assert f'librarian_http_request_duration_seconds_bucket{{le="0.5",method="GET",{route}' in text


def test_search_latency_histogram_counts_search_requests(client: TestClient) -> None:
    before = _sample(_scrape(client), "librarian_search_duration_seconds_count")
    assert client.get("/api/courses/search?q=retrieval", headers=ADMIN).status_code == 200
    after = _sample(_scrape(client), "librarian_search_duration_seconds_count")
    assert after == before + 1


def test_gauges_report_readiness_release_spend_cap_and_disk(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_CHAT_DAILY_BUDGET_USD", "5")
    monkeypatch.setenv("LIBRARIAN_RELEASE", "sha-test123")
    get_settings.cache_clear()
    from librarian.config import get_release

    get_release.cache_clear()
    chat_limiter.record_usage(get_settings(), TokenUsage(output=100_000))  # $1.00 on Sonnet 5.5
    text = _scrape(client)
    assert _sample(text, "librarian_ready ") in (0.0, 1.0)
    assert _sample(text, 'librarian_chat_spend_usd{window="today"}') == pytest.approx(1.0)
    assert _sample(text, 'librarian_chat_spend_usd{window="30d"}') == pytest.approx(1.0)
    assert _sample(text, 'librarian_chat_spend_cap_usd{scope="global_daily"}') == 5.0
    assert 'librarian_release_info{content="",release="sha-test123"} 1.0' in text
    assert 0.0 < _sample(text, "librarian_state_disk_free_ratio") <= 1.0
    get_release.cache_clear()


def _stream_stub(monkeypatch: pytest.MonkeyPatch, events: list[dict[str, Any]]) -> None:
    async def run(
        query: str, history: list[Any], on_usage: Callable[[TokenUsage], None], **_: object
    ) -> AsyncIterator[dict[str, Any]]:
        for e in events:
            yield e

    monkeypatch.setattr(chat_router, "run_agent_stream", run)


def test_chat_first_token_is_observed_once_per_stream(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stream_stub(
        monkeypatch,
        [{"type": "token", "content": "a"}, {"type": "token", "content": "b"}, {"type": "done"}],
    )
    before = _sample(_scrape(client), "librarian_chat_first_token_seconds_count")
    r = client.post("/api/chat/stream", json={"query": "hi"}, headers=ADMIN)
    assert r.status_code == 200
    text = _scrape(client)
    assert _sample(text, "librarian_chat_first_token_seconds_count") == before + 1
    assert 'librarian_chat_streams_total{outcome="token"}' in text


def test_a_stream_with_no_token_is_counted_as_such(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stream_stub(monkeypatch, [{"type": "done"}])
    client.post("/api/chat/stream", json={"query": "hi"}, headers=ADMIN)
    assert 'librarian_chat_streams_total{outcome="no_token"}' in _scrape(client)


def test_prepare_sets_up_an_empty_directory_only_for_several_workers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_STATE_DIR", str(tmp_path))
    monkeypatch.delenv(prom_env.ENV_VAR, raising=False)
    get_settings.cache_clear()
    settings = get_settings()
    assert prom_env.prepare(settings, 1) is None
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    stale = tmp_path / "librarian-prometheus"
    stale.mkdir()
    (stale / "counter_1.db").write_bytes(b"old")
    path = prom_env.prepare(settings, 2)
    assert path == stale and os.environ[prom_env.ENV_VAR] == str(stale)
    assert list(stale.iterdir()) == []
    monkeypatch.delenv(prom_env.ENV_VAR)  # prepare() set it for this process
    monkeypatch.setenv("LIBRARIAN_METRICS_TOKEN", "")
    get_settings.cache_clear()
    assert prom_env.prepare(get_settings(), 4) is None


def test_two_processes_are_summed_in_multiprocess_mode(tmp_path: Path) -> None:
    """The reason for multiprocess mode: one scrape sees the requests of every worker."""
    script = textwrap.dedent(
        """
        import sys
        from librarian.api import prom
        prom.HTTP_REQUESTS.labels("GET", "/x", "200").inc(int(sys.argv[1]))
        """
    )
    env = {**os.environ, prom_env.ENV_VAR: str(tmp_path)}
    for n in ("2", "3"):
        subprocess.run([sys.executable, "-c", script, n], env=env, check=True)
    probe = "from librarian.api import prom; print(prom.render().decode())"
    out = subprocess.run(
        [sys.executable, "-c", probe], env=env, check=True, capture_output=True, text=True
    ).stdout
    assert (
        _sample(out, 'librarian_http_requests_total{method="GET",route="/x",status="200"}') == 5.0
    )


# ── GET /api/admin/spend ───────────────────────────────────────────────────


def test_admin_spend_lists_users_by_id_and_name_never_email(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_CHAT_DAILY_BUDGET_USD", "4")
    get_settings.cache_clear()
    engine = get_engine()
    accounts.add_user(engine, "ada@example.com", name="Ada")
    ada = accounts.get_user(engine, "ada@example.com")
    assert ada is not None
    chat_limiter.record_usage(get_settings(), TokenUsage(output=100_000), ada.id)  # $1.00
    chat_limiter.record_usage(get_settings(), TokenUsage(output=10_000), None)  # $0.10, no user
    r = client.get("/api/admin/spend", headers=ADMIN)
    assert r.status_code == 200
    body = r.json()
    assert "@" not in r.text
    assert body["global"]["today_usd"] == pytest.approx(1.1)
    assert body["global"]["last_30d_usd"] == pytest.approx(1.1)
    assert body["global"]["daily_cap_usd"] == 4.0
    assert body["global"]["today_fraction_of_cap"] == pytest.approx(0.275)
    assert body["users"][0] == {
        "user_id": ada.id,
        "name": "Ada",
        "today_usd": 1.0,
        "last_30d_usd": 1.0,
        "requests_30d": 1,
    }
    assert body["users"][1]["user_id"] is None
    assert body["configured_model"] == get_settings().anthropic_model
    assert body["models"]["source"] == "logs/agent.jsonl"


def test_admin_spend_is_for_admins_only(client: TestClient) -> None:
    engine = get_engine()
    accounts.add_user(engine, "bob@example.com", name="Bob")
    key = accounts.create_key(engine, "bob@example.com", scopes="read")[1]
    assert (
        client.get("/api/admin/spend", headers={"Authorization": f"Bearer {key}"}).status_code
        == 403
    )
    assert client.get("/api/admin/spend").status_code == 401


def test_spend_by_model_reads_the_agent_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json
    from datetime import UTC, datetime

    from librarian import spend
    from librarian.retrieval import corpus

    monkeypatch.setattr(corpus, "LOGS_DIR", tmp_path)
    now = datetime.now(UTC).isoformat()
    rows = [
        {"ts": now, "model": "claude-sonnet-5-5", "cost_usd": 0.5},
        {"ts": now, "model": "claude-sonnet-5-5", "cost_usd": 0.25},
        {"ts": now, "model": "claude-haiku-5-5"},
    ]
    (tmp_path / "agent.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    got = spend.by_model()["models"]
    assert got["claude-sonnet-5-5"] == {"answers": 2, "usd": 0.75, "answers_without_cost": 0}
    assert got["claude-haiku-5-5"]["answers_without_cost"] == 1
