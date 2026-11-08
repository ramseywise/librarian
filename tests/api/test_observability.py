"""Traces (spans), Sentry and the release value: off by default, correct when on.

Spans are checked with an in-memory exporter; nothing here touches the network.
"""

# ruff: noqa: ANN401 -- OTel spans and the fake client are untyped test doubles

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import structlog

from librarian import observability as obs
from librarian.agent import loop as agent
from librarian.config import get_release
from librarian.log_config import configure_logging
from librarian.pricing import TokenUsage
from librarian.retrieval import corpus, embeddings
from librarian.retrieval.ranking import search_rows

exporter_mod = pytest.importorskip("opentelemetry.sdk.trace.export.in_memory_span_exporter")

PAGE = "---\ntitle: {t}\ntags: [rag, concept]\nsummary: {t} summary\nupdated: 2026-07-20\n---\n\n# {t}\n\n{t} body.\n"


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "private").mkdir(parents=True)
    (wiki_dir / "rag" / "chunking.md").write_text(PAGE.format(t="Chunking"))
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    return wiki_dir


@pytest.fixture()
def spans(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    """Tracing on, exporting to memory; yields the exporter."""
    monkeypatch.setenv("LIBRARIAN_RELEASE", "test-rel")
    monkeypatch.setenv("LIBRARIAN_EXPERIMENT", "")
    monkeypatch.delenv("LIBRARIAN_TRACE_CONTENT", raising=False)
    get_release.cache_clear()
    memory = exporter_mod.InMemorySpanExporter()
    assert obs.configure_tracing(exporter=memory)
    yield memory
    obs.shutdown_tracing()
    get_release.cache_clear()


def _by_name(memory: Any, name: str) -> list[Any]:
    return [s for s in memory.get_finished_spans() if s.name == name]


async def _run(client: Any, query: str = "what is chunking?", **kw: Any) -> list[dict[str, Any]]:
    return [e async for e in agent.run_agent_stream(query, client=client, **kw)]


# -- off by default ---------------------------------------------------------


def test_span_is_a_noop_when_tracing_is_not_configured() -> None:
    assert not obs.tracing_enabled()
    with obs.span("anything", a=1) as s:
        s.set_attribute("k", "v")
    assert isinstance(obs.start_span("x"), obs.NoopSpan)


def test_configure_tracing_stays_off_without_an_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    assert obs.configure_tracing() is False
    assert not obs.tracing_enabled()


# -- search -----------------------------------------------------------------


@pytest.mark.unit
def test_search_span_has_shape_but_not_the_query(wiki: Path, spans: Any) -> None:
    rows, _ = search_rows("chunking", limit=3)
    (s,) = _by_name(spans, "search")
    attrs = dict(s.attributes)
    assert attrs["search.query_length"] == len("chunking")
    assert attrs["search.limit"] == 3
    assert attrs["search.result_count"] == len(rows)
    assert attrs["latency_ms"] >= 0
    assert attrs["release"] == "test-rel"
    assert attrs["experiment"] == ""
    assert "chunking" not in json.dumps({k: str(v) for k, v in attrs.items() if k != "search.tool"})


# -- agent loop -------------------------------------------------------------


def _turn_with_usage(turn: Any, **usage: int) -> Any:
    from types import SimpleNamespace

    turn.usage = SimpleNamespace(**usage)
    turn.model = "claude-test-model"
    return turn


@pytest.mark.unit
async def test_agent_loop_emits_turn_model_and_tool_spans(
    wiki: Path, spans: Any, fake_anthropic: type
) -> None:
    first = _turn_with_usage(
        fake_anthropic.tool_turn(("search_wiki", {"query": "chunking"})),
        input_tokens=10,
        output_tokens=5,
        cache_read_input_tokens=100,
        cache_creation_input_tokens=7,
    )
    second = _turn_with_usage(fake_anthropic.text_turn("Done."), input_tokens=3, output_tokens=2)
    client = fake_anthropic([first, second])
    seen: list[TokenUsage] = []
    await _run(client, model="claude-test-model", on_usage=seen.append)

    assert seen[0] == TokenUsage(10, 5, 100, 7)
    turns = _by_name(spans, "agent.turn")
    models = _by_name(spans, "gen_ai.chat")
    (tool,) = _by_name(spans, "agent.tool")
    assert len(turns) == 2 and len(models) == 2

    m = sorted(models, key=lambda s: s.start_time)[0].attributes
    assert m["gen_ai.request.model"] == "claude-test-model"
    assert m["gen_ai.usage.input_tokens"] == 10
    assert m["gen_ai.usage.output_tokens"] == 5
    assert m["gen_ai.usage.cache_read.input_tokens"] == 100
    assert m["gen_ai.usage.cache_creation.input_tokens"] == 7
    assert tuple(m["gen_ai.response.finish_reasons"]) == ("tool_use",)

    assert tool.attributes["gen_ai.tool.name"] == "search_wiki"
    assert tool.attributes["is_error"] is False
    assert tool.attributes["result_size"] > 0
    assert tool.attributes["latency_ms"] >= 0

    # Nesting: the tool and the model call sit under their turn; the search under the tool.
    turn_ids = {t.context.span_id for t in turns}
    assert tool.parent.span_id in turn_ids
    assert all(x.parent.span_id in turn_ids for x in models)
    (search,) = _by_name(spans, "search")
    assert search.parent.span_id == tool.context.span_id

    for s in [*turns, *models, tool, search]:
        assert s.attributes["release"] == "test-rel"
        assert s.attributes["experiment"] == ""


@pytest.mark.unit
async def test_agent_spans_carry_no_text_by_default(
    wiki: Path, spans: Any, fake_anthropic: type
) -> None:
    client = fake_anthropic([fake_anthropic.text_turn("the secret answer")])
    await _run(client, query="the secret question")
    blob = json.dumps([dict(s.attributes) for s in spans.get_finished_spans()], default=str)
    assert "secret" not in blob


@pytest.mark.unit
async def test_content_is_captured_only_with_the_flag(
    wiki: Path, spans: Any, fake_anthropic: type, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_TRACE_CONTENT", "1")
    client = fake_anthropic([fake_anthropic.text_turn("the secret answer")])
    await _run(client, query="the secret question")
    (turn,) = _by_name(spans, "agent.turn")
    assert turn.attributes["gen_ai.prompt"] == "the secret question"
    assert turn.attributes["gen_ai.completion"] == "the secret answer"


@pytest.mark.unit
async def test_agent_error_marks_the_turn(wiki: Path, spans: Any, fake_anthropic: type) -> None:
    client = fake_anthropic([])
    client.raise_on_stream = RuntimeError("boom")
    await _run(client)
    (turn,) = _by_name(spans, "agent.turn")
    assert turn.attributes["is_error"] is True
    (model,) = _by_name(spans, "gen_ai.chat")
    assert any(e.name == "exception" for e in model.events)


@pytest.mark.unit
async def test_agent_runs_unchanged_with_tracing_off(wiki: Path, fake_anthropic: type) -> None:
    events = await _run(fake_anthropic([fake_anthropic.text_turn("Hi.")]))
    assert events[-1]["type"] == "done" and len(events[-1]["answer_id"]) == 32


# -- Sentry -----------------------------------------------------------------


def test_sentry_is_skipped_without_a_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    sentry = pytest.importorskip("sentry_sdk")
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    called: list[object] = []
    monkeypatch.setattr(sentry, "init", lambda *a, **k: called.append(k))
    assert obs.init_sentry() is False
    assert called == []


def test_sentry_init_passes_release_and_no_pii(monkeypatch: pytest.MonkeyPatch) -> None:
    sentry = pytest.importorskip("sentry_sdk")
    monkeypatch.setenv("SENTRY_DSN", "https://key@example.invalid/1")
    monkeypatch.setenv("LIBRARIAN_RELEASE", "rel-9")
    get_release.cache_clear()
    called: list[dict[str, Any]] = []
    monkeypatch.setattr(sentry, "init", lambda *a, **k: called.append(k))
    try:
        assert obs.init_sentry() is True
    finally:
        get_release.cache_clear()
    (kw,) = called
    assert kw["release"] == "rel-9"
    assert kw["send_default_pii"] is False
    assert kw["before_send"] is obs._scrub_event


def test_sentry_scrubs_the_authorization_header() -> None:
    event = {
        "request": {
            "headers": {"Authorization": "Bearer abc", "X-Api-Key": "k", "Accept": "json"},
            "cookies": {"s": "1"},
        }
    }
    out = obs._scrub_event(event, None)
    assert out["request"]["headers"]["Authorization"] == "[Filtered]"
    assert out["request"]["headers"]["X-Api-Key"] == "[Filtered]"
    assert out["request"]["headers"]["Accept"] == "json"
    assert "cookies" not in out["request"]


# -- release ----------------------------------------------------------------


def test_release_env_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_RELEASE", "abc123")
    get_release.cache_clear()
    try:
        assert get_release() == "abc123"
    finally:
        get_release.cache_clear()


def test_release_falls_back_to_dev_without_env_or_repo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("LIBRARIAN_RELEASE", raising=False)
    monkeypatch.setenv("LIBRARIAN_ROOT", str(tmp_path))  # not a repo: the sha lookup fails
    get_release.cache_clear()
    try:
        assert get_release() == "dev"
    finally:
        get_release.cache_clear()


def test_every_log_line_carries_the_release(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LIBRARIAN_RELEASE", "log-rel")
    get_release.cache_clear()
    try:
        configure_logging(render_json=True)
        structlog.get_logger("t").info("test.event", n=1)
        line = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    finally:
        get_release.cache_clear()
        structlog.reset_defaults()
    assert line["release"] == "log-rel"
    assert line["event"] == "test.event"
