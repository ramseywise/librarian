from __future__ import annotations

import copy
import os
from collections.abc import AsyncIterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: end-to-end tests requiring live servers")
    config.addinivalue_line("markers", "unit: fast unit tests, no servers needed")
    # TestClient-as-context-manager runs the app lifespan; don't build the real course
    # catalog or load the embedding model there.
    os.environ.setdefault("LIBRARIAN_SKIP_WARMUP", "1")


@pytest.fixture(autouse=True)
def _isolate_retrieval_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep test traffic out of the real retrieval telemetry (LIB-114 F10).

    logs/retrieval.jsonl feeds /compact-wiki's evidence pass — pytest queries
    polluting it skew which pages look retrieval-hot. Per-test patches in
    tests/app/ remain but are now redundant.
    """
    from app.mcp_server import server

    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")


# ---------------------------------------------------------------------------
# Fake Anthropic client — drives the agent loop and the judge with no network.
# ---------------------------------------------------------------------------


class _FakeStream:
    """Stands in for the SDK's MessageStream: async CM, async-iterable, final message."""

    def __init__(self, turn: SimpleNamespace) -> None:
        self._turn = turn

    async def __aenter__(self) -> _FakeStream:
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    def __aiter__(self) -> AsyncIterator[SimpleNamespace]:
        return self._events()

    async def _events(self) -> AsyncIterator[SimpleNamespace]:
        for block in self._turn.content:
            if block.type == "text":
                yield SimpleNamespace(
                    type="content_block_delta",
                    delta=SimpleNamespace(type="text_delta", text=block.text),
                )

    async def get_final_message(self) -> SimpleNamespace:
        return self._turn


class FakeAnthropic:
    """Scripted AsyncAnthropic. `turns` feed messages.stream; `replies` feed messages.create.

    Every call's kwargs are recorded (messages deep-copied as sent) so tests can assert
    on what the agent actually put on the wire. Set `raise_on_stream` to simulate an API
    failure.
    """

    def __init__(
        self, turns: list[SimpleNamespace] | None = None, replies: list[str] | None = None
    ) -> None:
        self.turns = list(turns or [])
        self.replies = list(replies or [])
        self.stream_calls: list[dict[str, Any]] = []
        self.create_calls: list[dict[str, Any]] = []
        self.raise_on_stream: Exception | None = None
        self.messages = SimpleNamespace(stream=self._stream, create=self._create)

    def _stream(self, **kwargs: Any) -> _FakeStream:  # noqa: ANN401 — mirrors SDK kwargs
        self.stream_calls.append({**kwargs, "messages": copy.deepcopy(kwargs["messages"])})
        if self.raise_on_stream is not None:
            raise self.raise_on_stream
        return _FakeStream(self.turns.pop(0))

    async def _create(self, **kwargs: Any) -> SimpleNamespace:  # noqa: ANN401
        self.create_calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.replies.pop(0))])


def text_turn(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    """A final model turn that streams `text`."""
    return SimpleNamespace(
        stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)]
    )


def tool_turn(*calls: tuple[str, dict[str, Any]], preamble: str = "") -> SimpleNamespace:
    """A model turn requesting tools: each call is (name, input)."""
    content: list[SimpleNamespace] = []
    if preamble:
        content.append(SimpleNamespace(type="text", text=preamble))
    for i, (name, inp) in enumerate(calls):
        content.append(SimpleNamespace(type="tool_use", id=f"toolu_{i}", name=name, input=inp))
    return SimpleNamespace(stop_reason="tool_use", content=content)


FakeAnthropic.text_turn = staticmethod(text_turn)  # type: ignore[attr-defined]
FakeAnthropic.tool_turn = staticmethod(tool_turn)  # type: ignore[attr-defined]


@pytest.fixture()
def fake_anthropic() -> type[FakeAnthropic]:
    """The FakeAnthropic class (with .text_turn/.tool_turn); construct with scripted turns."""
    return FakeAnthropic
