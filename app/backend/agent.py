from __future__ import annotations

import asyncio
import json
import os
import re
import time
from collections.abc import AsyncGenerator, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import anthropic

from app.mcp_server import server
from shared.log_config import get_logger

log = get_logger(__name__)

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
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

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    """Lazily build the default client from the environment.

    Only used when run_agent_stream is called without an injected client.
    """
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. "
                "Add it to your .env file or export it before starting the server."
            )
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text, count=1).lstrip()


def _search_wiki(query: str) -> str:
    # data/wiki/private/ is never searched — Buyi confidentiality invariant, clause (b).
    # The server's search core indexes only public pages, so the agent inherits the
    # exclusion (and retrieval telemetry) from the single implementation.
    rows, degraded = server._search_rows(query, domain="", limit=8, tool="agent_search")
    # The chat agent sees the same degradation notice the MCP tool emits — it is
    # the signal that a thin result set reflects the retrieval path, not the wiki.
    warning = server._degraded_notice(degraded)
    if not rows:
        return warning + "No pages found matching that query."

    parts = []
    for path, title, _tags, summary, content, _backlinks, _score in rows:
        page_id = Path(path).stem
        excerpt = _strip_frontmatter(content)[:200].replace("\n", " ")
        parts.append(f"**{title}** (id: `{page_id}`)\nSummary: {summary}\nExcerpt: {excerpt}...")

    return warning + "\n\n---\n\n".join(parts)


def _read_page(page_id: str) -> str:
    # Private pages are unreachable by ID and by title alike — the server core
    # applies the same predicate on every lookup path.
    return server._read_page_text(page_id)


_TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_wiki",
        "description": (
            "Search wiki pages for content matching the query. "
            "Returns page IDs, summaries, and excerpts for the top matches."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query using key terms from the question",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_page",
        "description": "Read the full content of a wiki page by its ID (kebab-case filename without .md).",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Page ID as shown in search results, e.g. 'langgraph-crag-pipeline'",
                }
            },
            "required": ["page_id"],
        },
    },
]

_SYSTEM = """You are a discerning research analyst for a personal agent engineering knowledge base.
Your job is not to recite documentation — it is to weigh evidence, surface trade-offs, flag gaps,
and help the user think clearly about design decisions.

## Process
1. Use search_wiki to find relevant pages
2. Use read_page on the 2–4 most relevant pages (prioritise concept and comparison pages over decision pages)
3. Synthesise a critical, grounded answer

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

    Same contract as server._log_retrieval: never raises — telemetry must not break a
    chat answer. The path is derived from server.LOGS_DIR at call time, so anything
    that redirects retrieval telemetry (the test autouse fixture) redirects this too.
    The answer text is deliberately not logged — only its shape.
    """
    try:
        server.LOGS_DIR.mkdir(exist_ok=True)
        entry = {"ts": datetime.now(UTC).isoformat(), **fields}
        with (server.LOGS_DIR / AGENT_LOG_NAME).open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log.warning("agent.telemetry_failed", error=str(e))


async def run_agent_stream(
    query: str,
    history: Sequence[dict[str, str]] | None = None,
    *,
    client: anthropic.AsyncAnthropic | None = None,
    model: str = MODEL,
    source: str = "chat",
) -> AsyncGenerator[dict[str, Any], None]:
    """Run the tool-use loop and yield SSE-ready events.

    Events: token* → grounding → highlight? → done. Grounding is emitted even after an
    error, over whatever was read. `history` is prior text-only user/assistant turns
    (validated at the API boundary, trimmed here). `client` is injectable so tests and
    the eval harness can drive the loop without the env.
    `source` tags the telemetry line so eval traffic can be filtered from chat.
    """
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

    try:
        client = client or _get_client()
        async with asyncio.timeout(300):  # 5-minute wall-clock bound (#33)
            for _ in range(MAX_TURNS):
                turns += 1
                # Stream every turn: unlike Gemini, tool_use arrives as its own block
                # type, so text deltas are never ambiguous with a pending call. Text on
                # a tool-calling turn is preamble and is streamed as it comes.
                async with client.messages.stream(
                    model=model,
                    max_tokens=MAX_TOKENS,
                    system=_SYSTEM,
                    tools=_TOOLS,
                    messages=messages,
                ) as stream:
                    async for event in stream:
                        if event.type == "content_block_delta" and event.delta.type == "text_delta":
                            answer_parts.append(event.delta.text)
                            yield {"type": "token", "content": event.delta.text}
                    response = await stream.get_final_message()

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

                tool_results: list[dict[str, Any]] = []
                for block in tool_uses:
                    args: dict[str, Any] = dict(block.input or {})
                    arg = str(args.get("query" if block.name == "search_wiki" else "page_id", ""))
                    tool_calls.append({"tool": block.name, "arg": arg})
                    if block.name == "search_wiki":
                        result = _search_wiki(args.get("query", ""))
                        for m in re.finditer(r"\(id: `([^`]+)`\)", result):
                            referenced_pages.add(m.group(1))
                    elif block.name == "read_page":
                        page_id = args.get("page_id", "")
                        result = _read_page(page_id)
                        if not result.startswith(("Page not found:", "Multiple pages match")):
                            referenced_pages.add(page_id)
                            if page_id not in pages_read:
                                pages_read.append(page_id)
                    else:
                        result = "Unknown tool."

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

                messages.append({"role": "user", "content": tool_results})
    except TimeoutError:
        stop_reason = "timeout"
        error = True
        log.error("agent.stream.timeout", turns=turns)
        yield {"type": "token", "content": "\n\n[The request timed out. Please try again.]"}
    except Exception as exc:
        stop_reason = "error"
        error = True
        log.error("agent.stream.failed", error=str(exc), error_type=type(exc).__name__)
        yield {"type": "token", "content": "\n\n[An error occurred. Please try again.]"}

    # Grounding is checked per answer: a citation counts only if that page was read in
    # this run. Before this, "never invent content" was a prompt line with no check.
    cited = extract_citations("".join(answer_parts))
    ungrounded = [c for c in cited if c not in pages_read]
    yield {"type": "grounding", "cited": cited, "pages_read": pages_read, "ungrounded": ungrounded}

    # Highlight stays sourced from tool results only — a cited id is never added, so a
    # hallucinated citation cannot light up a graph node.
    valid_pages = {p for p in referenced_pages if next(server.WIKI_DIR.rglob(f"{p}.md"), None)}
    if valid_pages:
        yield {"type": "highlight", "pages": sorted(valid_pages)}

    _log_answer(
        source=source,
        model=model,
        query=query,
        n_history=len(prior),
        turns=turns,
        tool_calls=tool_calls,
        pages_read=pages_read,
        cited=cited,
        ungrounded=ungrounded,
        latency_ms=round((time.monotonic() - started) * 1000),
        stop_reason=stop_reason,
        error=error,
    )
    yield {"type": "done"}
