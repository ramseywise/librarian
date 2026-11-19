"""A Gemini client in the shape the agent loop uses from `anthropic.AsyncAnthropic`.

`client.messages.create(...)` and `async with client.messages.stream(...) as s` take the
Anthropic wire shape (system blocks, `tool_use` / `tool_result` content, `input_schema` tools),
call Gemini's REST API with `httpx`, and give back Anthropic-shaped events and messages, so
`librarian.agent.loop`, `agent.support.judge` and the intake route run unchanged on
LIBRARIAN_CHAT_PROVIDER=gemini. Only what those callers read is mapped: text deltas, `tool_use`
blocks, `stop_reason`, `usage` and `model`. `cache_control` is dropped (Gemini caches implicitly).
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

import httpx

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Gemini finish reasons the loop treats as a refusal; everything else not listed is end_turn.
_REFUSALS = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "RECITATION"}


@dataclass
class TextBlock:
    text: str
    type: str = "text"


@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
    # Gemini 2.5+ signs its function calls; the signature must go back with the call.
    thought_signature: str | None = None
    type: str = "tool_use"


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class Message:
    content: list[TextBlock | ToolUseBlock]
    stop_reason: str
    model: str
    usage: Usage = field(default_factory=Usage)


@dataclass
class _Delta:
    text: str
    type: str = "text_delta"


@dataclass
class _Event:
    delta: _Delta
    type: str = "content_block_delta"


def _field(block: object, name: str, default: object = None) -> Any:  # noqa: ANN401
    """`block.name` for SDK-style objects, `block[name]` for dicts."""
    if isinstance(block, Mapping):
        return block.get(name, default)
    return getattr(block, name, default)


def _system_text(system: str | Iterable[Any] | None) -> str:
    if not system:
        return ""
    if isinstance(system, str):
        return system
    return "\n\n".join(_field(b, "text", "") for b in system)


def _contents(messages: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Anthropic messages as Gemini `contents`. A tool_result names its call by id only, so the
    function name is looked up from the assistant turn that made the call."""
    names: dict[str, str] = {}
    out: list[dict[str, Any]] = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        content = m["content"]
        if isinstance(content, str):
            out.append({"role": role, "parts": [{"text": content}]})
            continue
        parts: list[dict[str, Any]] = []
        for b in content:
            kind = _field(b, "type")
            if kind == "text":
                parts.append({"text": _field(b, "text", "")})
            elif kind == "tool_use":
                names[_field(b, "id")] = _field(b, "name")
                part: dict[str, Any] = {
                    "functionCall": {"name": _field(b, "name"), "args": _field(b, "input") or {}}
                }
                if sig := _field(b, "thought_signature"):
                    part["thoughtSignature"] = sig
                parts.append(part)
            elif kind == "tool_result":
                result = _field(b, "content", "")
                key = "error" if _field(b, "is_error") else "result"
                parts.append(
                    {
                        "functionResponse": {
                            "name": names.get(_field(b, "tool_use_id"), "unknown"),
                            "response": {key: result},
                        }
                    }
                )
        out.append({"role": role, "parts": parts})
    return out


def _body(
    *,
    max_tokens: int,
    messages: Iterable[Mapping[str, Any]],
    system: str | Iterable[Any] | None = None,
    tools: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "contents": _contents(messages),
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    if text := _system_text(system):
        body["systemInstruction"] = {"parts": [{"text": text}]}
    decls = [
        {
            "name": t["name"],
            "description": t.get("description", ""),
            # Full JSON Schema; `parameters` takes only Gemini's OpenAPI subset.
            "parametersJsonSchema": t["input_schema"],
        }
        for t in tools or []
    ]
    if decls:
        body["tools"] = [{"functionDeclarations": decls}]
    return body


class _Accumulator:
    """Folds Gemini response chunks into one Anthropic-shaped `Message`."""

    def __init__(self, model: str) -> None:
        self.model = model
        self.text: list[str] = []
        self.calls: list[ToolUseBlock] = []
        self.finish: str | None = None
        self.usage = Usage()

    def add(self, chunk: Mapping[str, Any]) -> str:
        """Take one chunk; returns the text it carried."""
        if meta := chunk.get("usageMetadata"):
            cached = meta.get("cachedContentTokenCount", 0)
            self.usage = Usage(
                input_tokens=meta.get("promptTokenCount", 0) - cached,
                output_tokens=meta.get("candidatesTokenCount", 0)
                + meta.get("thoughtsTokenCount", 0),
                cache_read_input_tokens=cached,
            )
        self.model = chunk.get("modelVersion") or self.model
        if (feedback := chunk.get("promptFeedback")) and feedback.get("blockReason"):
            self.finish = "SAFETY"
        text = ""
        for cand in chunk.get("candidates", [])[:1]:
            self.finish = cand.get("finishReason") or self.finish
            for part in cand.get("content", {}).get("parts", []):
                if part.get("thought"):
                    continue
                if "functionCall" in part:
                    call = part["functionCall"]
                    self.calls.append(
                        ToolUseBlock(
                            id=f"toolu_{uuid.uuid4().hex[:24]}",
                            name=call["name"],
                            input=dict(call.get("args") or {}),
                            thought_signature=part.get("thoughtSignature"),
                        )
                    )
                elif "text" in part:
                    text += part["text"]
        if text:
            self.text.append(text)
        return text

    def message(self) -> Message:
        content: list[TextBlock | ToolUseBlock] = []
        if self.text:
            content.append(TextBlock("".join(self.text)))
        content.extend(self.calls)
        if self.finish in _REFUSALS:
            stop = "refusal"
        elif self.calls:
            stop = "tool_use"
        elif self.finish == "MAX_TOKENS":
            stop = "max_tokens"
        else:
            stop = "end_turn"
        return Message(content=content, stop_reason=stop, model=self.model, usage=self.usage)


class _Stream:
    def __init__(self, http: httpx.AsyncClient, model: str, body: dict[str, Any]) -> None:
        self._http, self._body = http, body
        self._acc = _Accumulator(model)
        self._response: httpx.Response | None = None
        self._cm: Any = None
        self._done = False

    async def __aenter__(self) -> _Stream:
        url = f"/models/{self._acc.model}:streamGenerateContent"
        self._cm = self._http.stream("POST", url, params={"alt": "sse"}, json=self._body)
        self._response = response = await self._cm.__aenter__()
        if response.is_error:
            await response.aread()
            response.raise_for_status()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._cm.__aexit__(*exc)

    async def __aiter__(self) -> AsyncIterator[_Event]:
        assert self._response is not None
        async for line in self._response.aiter_lines():
            if not line.startswith("data:"):
                continue
            if text := self._acc.add(json.loads(line[5:])):
                yield _Event(_Delta(text))
        self._done = True

    async def get_final_message(self) -> Message:
        if not self._done:
            async for _ in self:
                pass
        return self._acc.message()


class _Messages:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def create(self, *, model: str, **kwargs: Any) -> Message:  # noqa: ANN401 (Anthropic call shape)
        resp = await self._http.post(f"/models/{model}:generateContent", json=_body(**kwargs))
        resp.raise_for_status()
        acc = _Accumulator(model)
        acc.add(resp.json())
        return acc.message()

    def stream(self, *, model: str, **kwargs: Any) -> _Stream:  # noqa: ANN401 (Anthropic call shape)
        return _Stream(self._http, model, _body(**kwargs))


class AsyncGemini:
    """Stands in for `anthropic.AsyncAnthropic` where only `.messages` is used."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"x-goog-api-key": api_key},
            timeout=httpx.Timeout(120, connect=10),
            transport=transport,
        )
        self.messages = _Messages(self._http)
