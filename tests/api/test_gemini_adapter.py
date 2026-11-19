"""The Gemini adapter (`librarian.agent.gemini`) under the real agent loop.

Gemini's REST API is an `httpx.MockTransport`: no test here touches the network.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from librarian.agent import loop as agent
from librarian.agent.gemini import AsyncGemini
from librarian.config import Settings
from tests.api.test_agent_loop import wiki  # noqa: F401  (fixture)


def _sse(*chunks: dict[str, Any]) -> str:
    return "".join(f"data: {json.dumps(c)}\r\n\r\n" for c in chunks)


def _gemini(replies: list[str], seen: list[dict[str, Any]]) -> AsyncGemini:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append({"url": str(request.url), "body": json.loads(request.content)})
        return httpx.Response(200, text=replies.pop(0))

    return AsyncGemini("test-key", transport=httpx.MockTransport(handler))


@pytest.mark.unit
async def test_tool_call_round_trip(wiki: Path) -> None:  # noqa: F811
    seen: list[dict[str, Any]] = []
    replies = [
        _sse(
            {
                "candidates": [
                    {
                        "content": {
                            "role": "model",
                            "parts": [
                                {
                                    "functionCall": {
                                        "name": "read_page",
                                        "args": {"page_id": "chunking"},
                                    },
                                    "thoughtSignature": "sig-1",
                                }
                            ],
                        },
                        "finishReason": "STOP",
                    }
                ],
                "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 5},
            }
        ),
        _sse(
            {"candidates": [{"content": {"parts": [{"text": "Chunk by "}]}}]},
            {
                "candidates": [
                    {
                        "content": {"parts": [{"text": "headings [page:chunking]."}]},
                        "finishReason": "STOP",
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 300,
                    "cachedContentTokenCount": 100,
                    "candidatesTokenCount": 12,
                },
            },
        ),
    ]
    events = [
        e
        async for e in agent.run_agent_stream(
            "How do I chunk?",
            client=_gemini(replies, seen),  # type: ignore[arg-type]
            model="gemini-2.5-flash-lite",
            tool_names=["read_page"],
        )
    ]

    tokens = "".join(e["content"] for e in events if e["type"] == "token")
    assert tokens == "Chunk by headings [page:chunking]."
    grounding = next(e for e in events if e["type"] == "grounding")
    assert grounding["pages_read"] == ["chunking"]
    assert grounding["ungrounded"] == []

    first, second = seen
    assert first["url"].endswith("/models/gemini-2.5-flash-lite:streamGenerateContent?alt=sse")
    assert first["body"]["tools"][0]["functionDeclarations"][0]["name"] == "read_page"
    assert "systemInstruction" in first["body"]
    call, response = second["body"]["contents"][1:3]
    assert call["role"] == "model"
    assert call["parts"][0]["thoughtSignature"] == "sig-1"
    fr = response["parts"][0]["functionResponse"]
    assert fr["name"] == "read_page"
    assert "Chunk by headings." in fr["response"]["result"]


@pytest.mark.unit
async def test_create_maps_text_usage_and_refusal() -> None:
    seen: list[dict[str, Any]] = []
    ok = {
        "candidates": [{"content": {"parts": [{"text": "1. yes"}]}, "finishReason": "STOP"}],
        "usageMetadata": {"promptTokenCount": 40, "candidatesTokenCount": 3},
        "modelVersion": "gemini-2.5-flash-lite",
    }
    blocked = {"promptFeedback": {"blockReason": "SAFETY"}}
    client = _gemini([json.dumps(ok), json.dumps(blocked)], seen)

    resp = await client.messages.create(
        model="gemini-2.5-flash-lite",
        max_tokens=256,
        system="judge",
        messages=[{"role": "user", "content": "claims"}],
    )
    assert [b.text for b in resp.content if b.type == "text"] == ["1. yes"]
    assert (resp.usage.input_tokens, resp.usage.output_tokens) == (40, 3)
    assert resp.stop_reason == "end_turn"
    assert seen[0]["body"]["generationConfig"] == {"maxOutputTokens": 256}

    refused = await client.messages.create(
        model="gemini-2.5-flash-lite", max_tokens=10, messages=[{"role": "user", "content": "x"}]
    )
    assert refused.stop_reason == "refusal"


@pytest.mark.unit
def test_provider_selects_model_and_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_CHAT_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "g-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    s = Settings()
    assert (s.chat_model, s.chat_api_key) == ("gemini-2.5-flash", "g-key")
