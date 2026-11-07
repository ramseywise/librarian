from __future__ import annotations

import asyncio
import json
import re
import time
from collections.abc import AsyncGenerator, Callable, Sequence
from datetime import UTC, datetime
from typing import Any, cast

import anthropic

from librarian.agent.tools import CHAT, INVALID_ARGS_PREFIX, Tool, ToolContext, tools_for
from librarian.config import get_settings
from librarian.log_config import get_logger
from librarian.observability import (
    NoopSpan,
    end_span,
    start_span,
    timed,
    trace_content_enabled,
)
from librarian.pricing import TokenUsage
from librarian.retrieval import corpus

log = get_logger(__name__)


def default_model() -> str:
    """The model used when a caller does not pass one (`Settings.anthropic_model`)."""
    return get_settings().anthropic_model


MAX_TOKENS = 8192
MAX_TURNS = 8

# History bounds. Prior turns are text only (no tool blocks), so these cap what a
# follow-up re-sends; the oldest turns go first. Trimmed here rather than in the API
# layer so the eval harness and any other caller get the same bounds.
MAX_HISTORY_TURNS = 10
MAX_HISTORY_CHARS = 24_000

# Inline citation form the system prompt asks for. Not [[...]]: wikilinks are
# title-keyed and appear inside the page bodies the agent quotes, so they would be
# indistinguishable from citations. "[page:" does not occur in the wiki.
CITATION_RE = re.compile(r"\[page:\s*([A-Za-z0-9][A-Za-z0-9_\-]*)\s*\]")

AGENT_LOG_NAME = "agent.jsonl"

# Prompt-cache breakpoint. Tools render before the system prompt, so one on the last tool and
# one on the system block cover the whole static prefix.
_CACHE = {"type": "ephemeral"}

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    """Lazily build the default client from the environment.

    Only used when run_agent_stream is called without an injected client.
    """
    global _client
    if _client is None:
        api_key = get_settings().anthropic_api_key
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. "
                "Add it to your .env file or export it before starting the server."
            )
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


_SYSTEM = """You are a discerning research analyst for a personal agent engineering knowledge base.
Your job is not to recite documentation — it is to weigh evidence, surface trade-offs, flag gaps,
and help the user think clearly about design decisions.

## Process
1. Use search_wiki to find relevant pages
2. Use read_page on the 2–4 most relevant pages (prioritise concept and comparison pages over decision pages)
3. Synthesise a critical, grounded answer

When asked to brief on a domain or course module, start with get_domain_briefing and read the
pages that matter most before summarising what the area covers and where it is thin.

## Response format
Always lead with a **headline** — one sentence that directly answers the question.
Follow with 2–4 bullets covering the key trade-offs, caveats, or evidence.
End with a one-line offer: "Want me to go deeper on [specific aspect]?"

Keep the initial response tight. The user can ask for depth.

## Citations
Cite the page behind each claim inline as [page:<page-id>], using the page id exactly as
search_wiki shows it, e.g. "RRF is parameter-free [page:rag-retrieval-strategies]".
Only cite pages you have read with read_page while answering the current message — a
search excerpt is not a reading. Earlier turns of the conversation are text only: you no
longer have the pages read for them, so read_page again before citing one.

## Analytical stance
- Weigh options: name what each approach is good at AND where it breaks down
- Flag contradictions: if wiki pages disagree, surface the conflict explicitly
- Distinguish evidence types:
  - concept/pattern pages → state as research fact
  - decision pages → frame as a documented project choice, not universal truth:
    "the wiki records a decision to use X because Y — this reflects [project] context as of [date]"
  - comparison pages → present trade-offs neutrally, let the user conclude
- Flag gaps: if the wiki covers a topic weakly or not at all, say so — don't paper over it
- Note what approaches do NOT solve; oversold claims should be called out

Never invent content. Ground everything in what the wiki actually says."""


def _trim_history(history: Sequence[dict[str, str]]) -> list[dict[str, str]]:
    """Bound prior turns by count, then by total characters, oldest first.

    A leading assistant turn left by the cut is dropped too, so the transcript the model
    sees still opens on a user turn.
    """
    turns = [{"role": t["role"], "content": t["content"]} for t in history][-MAX_HISTORY_TURNS:]
    while turns and sum(len(t["content"]) for t in turns) > MAX_HISTORY_CHARS:
        turns.pop(0)
    while turns and turns[0]["role"] != "user":
        turns.pop(0)
    return turns


def extract_citations(text: str) -> list[str]:
    """Page ids cited as [page:<id>], in first-seen order, deduplicated."""
    return list(dict.fromkeys(m.group(1) for m in CITATION_RE.finditer(text)))


def _log_answer(**fields: object) -> None:
    """Append one JSON line of answer telemetry to logs/agent.jsonl.

    Same contract as retrieval.corpus.log_retrieval: never raises — telemetry must not break a
    chat answer. The path is derived from corpus.LOGS_DIR at call time, so anything
    that redirects retrieval telemetry (the test autouse fixture) redirects this too.
    The answer text is deliberately not logged — only its shape.
    """
    try:
        corpus.LOGS_DIR.mkdir(exist_ok=True)
        entry = {"ts": datetime.now(UTC).isoformat(), **fields}
        with (corpus.LOGS_DIR / AGENT_LOG_NAME).open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log.warning("agent.telemetry_failed", error=str(e))


async def _run_tool(
    tool: Tool | None, name: str, args: dict[str, Any], ctx: ToolContext, parent: object = None
) -> tuple[str, bool]:
    """Run one tool call; returns (result text, is_error). Traced as an `agent.tool` span.

    A failing tool must not end the answer: the error goes back as an `is_error` tool_result
    so the model can recover (retry, try another tool, or say so).
    """
    with timed("agent.tool", parent=parent, **{"gen_ai.tool.name": name}) as sp:
        result, is_error = await _call_tool(tool, name, args, ctx)
        sp.set_attribute("result_size", len(result))
        sp.set_attribute("is_error", is_error)
    return result, is_error


async def _call_tool(
    tool: Tool | None, name: str, args: dict[str, Any], ctx: ToolContext
) -> tuple[str, bool]:
    if tool is None:
        return "Unknown tool.", True
    try:
        result = await asyncio.to_thread(tool.run, args, ctx)
    except Exception as exc:
        log.error("agent.tool.failed", tool=name, error=str(exc), error_type=type(exc).__name__)
        return f"Tool {name} failed: {type(exc).__name__}. Try a different approach.", True
    return result, result.startswith(INVALID_ARGS_PREFIX)


def _usage_tokens(response: object) -> TokenUsage:
    """Tokens a turn billed, split by rate: uncached input, output, cache read, cache write."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return TokenUsage()

    def n(name: str) -> int:
        value = getattr(usage, name, 0)
        return value if isinstance(value, int) else 0

    return TokenUsage(
        input=n("input_tokens"),
        output=n("output_tokens"),
        cache_read=n("cache_read_input_tokens"),
        cache_write=n("cache_creation_input_tokens"),
    )


async def run_agent_stream(
    query: str,
    history: Sequence[dict[str, str]] | None = None,
    *,
    client: anthropic.AsyncAnthropic | None = None,
    model: str | None = None,
    source: str = "chat",
    on_usage: Callable[[TokenUsage], None] | None = None,
    tool_names: Sequence[str] | None = None,
    context: ToolContext | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Run the tool-use loop and yield SSE-ready events.

    Events: token* → grounding → highlight? → done. Grounding is emitted even after an
    error, over whatever was read. `history` is prior text-only user/assistant turns
    (validated at the API boundary, trimmed here). `client` is injectable so tests and
    the eval harness can drive the loop without the env.
    `source` tags the telemetry line so eval traffic can be filtered from chat.
    `on_usage(TokenUsage)` is called after each model turn, so a spend cap sees the cost of a
    stream that is later cut off. Each turn is an `agent.turn` span holding a model-call span and
    one `agent.tool` span per tool call (`librarian.observability`; no-ops unless tracing is on).
    `tool_names` picks the registry tools offered to the model (default: every chat tool).
    `context` is handed to each tool call; it is the seam for request context (the lesson a
    user has open), and nothing reads it yet.
    """
    model = model or default_model()
    tools: dict[str, Tool] = {t.name: t for t in tools_for(CHAT, tool_names)}
    tool_specs = [t.anthropic_spec() for t in tools.values()]
    if tool_specs:
        tool_specs[-1] = {**tool_specs[-1], "cache_control": _CACHE}
    system = [{"type": "text", "text": _SYSTEM, "cache_control": _CACHE}]
    ctx = context or ToolContext(surface=CHAT)
    started = time.monotonic()
    prior = _trim_history(history or [])
    messages: list[dict[str, Any]] = [*prior, {"role": "user", "content": query}]
    referenced_pages: set[str] = set()
    pages_read: list[str] = []
    tool_calls: list[dict[str, str]] = []
    answer_parts: list[str] = []
    turns = 0
    stop_reason: str | None = None
    error = False
    # Spans stay open across the yields below, so they are started, not made current (a context
    # attached in one resume of this generator could detach in another). `end_span` is idempotent.
    turn_span: Any = NoopSpan()  # replaced each turn; whatever is open is ended in `finally`
    model_span: Any = turn_span

    def grounding() -> dict[str, Any]:
        cited = extract_citations("".join(answer_parts))
        return {
            "cited": cited,
            "pages_read": pages_read,
            "ungrounded": [c for c in cited if c not in pages_read],
        }

    answered = False  # the model loop is over (cleanly or on a handled error)
    try:
        try:
            client = client or _get_client()
            async with asyncio.timeout(300):  # 5-minute wall-clock bound (#33)
                for _ in range(MAX_TURNS):
                    turns += 1
                    end_span(model_span)
                    end_span(turn_span)
                    turn_span = start_span(
                        "agent.turn",
                        turn=turns,
                        source=source,
                        **{"gen_ai.request.model": model},
                    )
                    if turns == 1 and trace_content_enabled():
                        turn_span.set_attribute("gen_ai.prompt", query)
                    model_span = start_span(
                        "gen_ai.chat",
                        parent=turn_span,
                        **{
                            "gen_ai.operation.name": "chat",
                            "gen_ai.system": "anthropic",
                            "gen_ai.request.model": model,
                            "gen_ai.request.max_tokens": MAX_TOKENS,
                        },
                    )
                    model_started = time.monotonic()
                    # Stream every turn: unlike Gemini, tool_use arrives as its own block
                    # type, so text deltas are never ambiguous with a pending call. Text on
                    # a tool-calling turn is preamble and is streamed as it comes.
                    async with client.messages.stream(
                        model=model,
                        max_tokens=MAX_TOKENS,
                        system=cast("Any", system),
                        # Plain dicts in the API's wire shape; the SDK's TypedDict unions are not
                        # worth mirroring here.
                        tools=cast("Any", tool_specs),
                        messages=cast("Any", messages),
                    ) as stream:
                        async for event in stream:
                            if (
                                event.type == "content_block_delta"
                                and event.delta.type == "text_delta"
                            ):
                                answer_parts.append(event.delta.text)
                                yield {"type": "token", "content": event.delta.text}
                        response = await stream.get_final_message()

                    usage = _usage_tokens(response)
                    model_span.set_attributes(
                        {
                            "gen_ai.usage.input_tokens": usage.input,
                            "gen_ai.usage.output_tokens": usage.output,
                            "gen_ai.usage.cache_read.input_tokens": usage.cache_read,
                            "gen_ai.usage.cache_creation.input_tokens": usage.cache_write,
                            "latency_ms": round((time.monotonic() - model_started) * 1000),
                        }
                    )
                    if isinstance(response.stop_reason, str):
                        model_span.set_attribute(
                            "gen_ai.response.finish_reasons", [response.stop_reason]
                        )
                    if isinstance(getattr(response, "model", None), str):
                        model_span.set_attribute("gen_ai.response.model", response.model)
                    end_span(model_span)
                    if on_usage is not None:
                        on_usage(usage)

                    stop_reason = response.stop_reason
                    if response.stop_reason == "refusal":
                        yield {
                            "type": "token",
                            "content": "\n\n[The model declined to answer this request.]",
                        }
                        break

                    tool_uses = [b for b in response.content if b.type == "tool_use"]
                    if not tool_uses:
                        break  # final answer turn — text already streamed above
                    if turns == MAX_TURNS:
                        # Budget spent with calls still pending: say so rather than end on
                        # a preamble that reads like a truncated answer.
                        stop_reason = "max_turns"
                        yield {
                            "type": "token",
                            "content": "\n\n[Stopped after the maximum number of tool turns.]",
                        }
                        break

                    messages.append({"role": "assistant", "content": response.content})

                    # Calls in one turn run concurrently; results and the bookkeeping below
                    # follow block order, so they stay deterministic.
                    parsed = [(b, dict(b.input or {}), tools.get(b.name)) for b in tool_uses]
                    outcomes = await asyncio.gather(
                        *(_run_tool(tool, b.name, args, ctx, turn_span) for b, args, tool in parsed)
                    )
                    tool_results: list[dict[str, Any]] = []
                    for (block, args, tool), (result, is_error) in zip(
                        parsed, outcomes, strict=True
                    ):
                        arg = str(args.get(tool.log_arg if tool else "page_id", ""))
                        tool_calls.append({"tool": block.name, "arg": arg})
                        if block.name == "search_wiki" and not is_error:
                            for m in re.finditer(r"\(id: `([^`]+)`\)", result):
                                referenced_pages.add(m.group(1))
                        elif block.name == "read_page" and not is_error:
                            page_id = str(args.get("page_id", ""))
                            if not result.startswith(("Page not found:", "Multiple pages match")):
                                referenced_pages.add(page_id)
                                if page_id not in pages_read:
                                    pages_read.append(page_id)

                        tool_result: dict[str, Any] = {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                        if is_error:
                            tool_result["is_error"] = True
                        tool_results.append(tool_result)

                    messages.append({"role": "user", "content": tool_results})
        except TimeoutError:
            stop_reason = "timeout"
            error = True
            turn_span.set_attribute("is_error", True)
            log.error("agent.stream.timeout", turns=turns)
            yield {"type": "token", "content": "\n\n[The request timed out. Please try again.]"}
        except Exception as exc:
            stop_reason = "error"
            error = True
            turn_span.set_attribute("is_error", True)
            model_span.record_exception(exc)
            log.error("agent.stream.failed", error=str(exc), error_type=type(exc).__name__)
            yield {"type": "token", "content": "\n\n[An error occurred. Please try again.]"}
        answered = True

        # Grounding is checked per answer: a citation counts only if that page was read in
        # this run. Before this, "never invent content" was a prompt line with no check.
        yield {"type": "grounding", **grounding()}

        # Highlight stays sourced from tool results only — a cited id is never added, so a
        # hallucinated citation cannot light up a graph node.
        valid_pages = {p for p in referenced_pages if next(corpus.WIKI_DIR.rglob(f"{p}.md"), None)}
        if valid_pages:
            yield {"type": "highlight", "pages": sorted(valid_pages)}
        yield {"type": "done"}
    except (asyncio.CancelledError, GeneratorExit):
        # Client went away. No yield from here on; the finally below still logs.
        if not answered:
            stop_reason = "cancelled"
        log.info("agent.stream.cancelled", turns=turns, answered=answered)
        raise
    finally:
        # Runs on normal end, error and client disconnect alike, so every answer is logged once.
        turn_span.set_attribute("stop_reason", stop_reason or "")
        if trace_content_enabled():
            turn_span.set_attribute("gen_ai.completion", "".join(answer_parts))
        end_span(model_span)
        end_span(turn_span)
        checked = grounding()
        _log_answer(
            source=source,
            model=model,
            query=query,
            n_history=len(prior),
            turns=turns,
            tool_calls=tool_calls,
            pages_read=pages_read,
            cited=checked["cited"],
            ungrounded=checked["ungrounded"],
            latency_ms=round((time.monotonic() - started) * 1000),
            stop_reason=stop_reason,
            error=error,
        )
