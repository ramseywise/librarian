from __future__ import annotations

import importlib
import json
from typing import Any

import pytest

from tools.presenter._client import parse_json_response

# Every module under tools/presenter/. presenter was copied in from a repo with a
# core/ package that has never existed here (see _settings.py / _client.py), so a
# plain import is a real regression guard, not a formality.
PRESENTER_MODULES = [
    "tools.presenter",
    "tools.presenter.__main__",
    "tools.presenter._client",
    "tools.presenter._settings",
    "tools.presenter.image_fetcher",
    "tools.presenter.intake",
    "tools.presenter.models",
    "tools.presenter.outline",
    "tools.presenter.providers",
    "tools.presenter.renderer",
    "tools.presenter.slide_writer",
    "tools.presenter.viz_classifier",
]


@pytest.mark.unit
@pytest.mark.parametrize("module_name", PRESENTER_MODULES)
def test_presenter_module_imports(module_name: str) -> None:
    if module_name == "tools.presenter.renderer":
        # python-pptx ships in the opt-in `presenter` extra, which bare `uv run`
        # does not install. Run `make install-presenter` to cover this module.
        pytest.importorskip("pptx", reason="needs the presenter extra (make install-presenter)")
    # providers.py imports replicate lazily inside the constructor, so it imports
    # fine without the extra — no guard needed here.
    importlib.import_module(module_name)


@pytest.mark.unit
def test_cli_parser_builds() -> None:
    """main() builds its parser before doing any work — --help must not need an API key."""
    from tools.presenter.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


@pytest.mark.unit
def test_cli_parser_rejects_unknown_provider() -> None:
    from tools.presenter.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main(["--provider", "midjourney"])
    assert exc.value.code == 2


# ---------------------------------------------------------------------------
# parse_json_response
# ---------------------------------------------------------------------------


class _StubContent:
    def __init__(self, text: str) -> None:
        self.text = text


class _StubMessages:
    def __init__(self, replies: list[str]) -> None:
        self._replies = list(replies)
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:  # noqa: ANN401 — mirrors the SDK's own signature
        self.calls.append(kwargs)
        if not self._replies:
            raise AssertionError("client.messages.create called more times than expected")
        return type("_Reply", (), {"content": [_StubContent(self._replies.pop(0))]})()


class _StubClient:
    """Stands in for anthropic.Anthropic — only .messages.create is ever touched."""

    def __init__(self, *replies: str) -> None:
        self.messages = _StubMessages(list(replies))


@pytest.mark.unit
def test_parse_json_response_valid_json_makes_no_repair_call() -> None:
    client = _StubClient()
    result = parse_json_response(client, '{"title": "Deck"}', "claude-opus-4-8", "sys")
    assert result == {"title": "Deck"}
    assert client.messages.calls == []


@pytest.mark.unit
def test_parse_json_response_strips_code_fence() -> None:
    client = _StubClient()
    fenced = '```json\n{"slides": [1, 2]}\n```'
    assert parse_json_response(client, fenced, "claude-opus-4-8", "sys") == {"slides": [1, 2]}
    assert client.messages.calls == []


@pytest.mark.unit
def test_parse_json_response_repairs_malformed_once() -> None:
    client = _StubClient('{"title": "Deck"}')
    result = parse_json_response(client, '{"title": "Deck"', "claude-opus-4-8", "sys")
    assert result == {"title": "Deck"}
    # The repair round-trip carries the model/system it was given and echoes the
    # bad text back — that is the whole reason the signature takes them.
    assert len(client.messages.calls) == 1
    call = client.messages.calls[0]
    assert call["model"] == "claude-opus-4-8"
    assert call["system"] == "sys"
    assert '{"title": "Deck"' in call["messages"][0]["content"]


@pytest.mark.unit
def test_parse_json_response_repaired_reply_may_be_fenced() -> None:
    client = _StubClient('```json\n{"ok": true}\n```')
    assert parse_json_response(client, "not json", "claude-opus-4-8", "sys") == {"ok": True}


@pytest.mark.unit
def test_parse_json_response_raises_after_second_failure() -> None:
    client = _StubClient("still not json")
    with pytest.raises(ValueError, match="after one repair attempt"):
        parse_json_response(client, "not json", "claude-opus-4-8", "sys")
    # Exactly one repair attempt — no unbounded retry loop inside a deck run.
    assert len(client.messages.calls) == 1


@pytest.mark.unit
def test_parse_json_response_returns_list_when_prompt_asked_for_one() -> None:
    client = _StubClient()
    assert parse_json_response(client, json.dumps([{"n": 1}]), "claude-opus-4-8", "sys") == [
        {"n": 1}
    ]
