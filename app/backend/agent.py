from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import anthropic

from app.mcp_server import server

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5")
MAX_TOKENS = 8192

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
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
    rows = server._search_rows(query, domain="", limit=8, tool="agent_search")
    if not rows:
        return "No pages found matching that query."

    parts = []
    for path, title, _tags, summary, content, _backlinks, _score in rows:
        page_id = Path(path).stem
        excerpt = _strip_frontmatter(content)[:200].replace("\n", " ")
        parts.append(f"**{title}** (id: `{page_id}`)\nSummary: {summary}\nExcerpt: {excerpt}...")

    return "\n\n---\n\n".join(parts)


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


async def run_agent_stream(query: str) -> AsyncGenerator[dict[str, Any], None]:
    client = _get_client()
    messages: list[dict[str, Any]] = [{"role": "user", "content": query}]
    referenced_pages: set[str] = set()

    try:
        async with asyncio.timeout(300):  # 5-minute wall-clock bound (#33)
            for _ in range(8):
                # Stream every turn: unlike Gemini, tool_use arrives as its own block
                # type, so text deltas are never ambiguous with a pending call. Text on
                # a tool-calling turn is preamble and is streamed as it comes.
                async with client.messages.stream(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=_SYSTEM,
                    tools=_TOOLS,
                    messages=messages,
                ) as stream:
                    async for event in stream:
                        if event.type == "content_block_delta" and event.delta.type == "text_delta":
                            yield {"type": "token", "content": event.delta.text}
                    response = await stream.get_final_message()

                if response.stop_reason == "refusal":
                    yield {
                        "type": "token",
                        "content": "\n\n[The model declined to answer this request.]",
                    }
                    break

                tool_uses = [b for b in response.content if b.type == "tool_use"]
                if not tool_uses:
                    break  # final answer turn — text already streamed above

                messages.append({"role": "assistant", "content": response.content})

                tool_results: list[dict[str, Any]] = []
                for block in tool_uses:
                    args: dict[str, Any] = dict(block.input or {})
                    if block.name == "search_wiki":
                        result = _search_wiki(args.get("query", ""))
                        for m in re.finditer(r"\(id: `([^`]+)`\)", result):
                            referenced_pages.add(m.group(1))
                    elif block.name == "read_page":
                        page_id = args.get("page_id", "")
                        result = _read_page(page_id)
                        if not result.startswith(("Page not found:", "Multiple pages match")):
                            referenced_pages.add(page_id)
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

            valid_pages = {
                p for p in referenced_pages if next(server.WIKI_DIR.rglob(f"{p}.md"), None)
            }
            if valid_pages:
                yield {"type": "highlight", "pages": list(valid_pages)}
    except Exception as exc:
        import logging

        logging.getLogger(__name__).exception("Agent stream error: %s", exc)
        yield {"type": "token", "content": "\n\n[An error occurred. Please try again.]"}

    yield {"type": "done"}
