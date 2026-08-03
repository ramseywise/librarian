from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import anthropic
import frontmatter

from app.mcp_server.server import is_under_private

WIKI_DIR = Path(__file__).parent.parent.parent / "data" / "wiki"
PRIVATE_DIR = WIKI_DIR / "private"


def _is_private(path: Path | str) -> bool:
    """True if path lies under this module's data/wiki/private/ — never served to the agent.

    Shares the server's resolution logic (../ traversal, absolute and unresolvable
    paths) but anchors on PRIVATE_DIR above. The server anchors on a relative
    Path("data/wiki"), so under `make api` (cwd=app/) its own PRIVATE_DIR resolves to a
    nonexistent app/data/wiki/private — binding to that would produce a filter that reads
    as correct and excludes nothing. Read at call time so tests can repoint it.
    """
    return is_under_private(path, PRIVATE_DIR)


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


def _search_wiki(query: str) -> str:
    results: list[tuple[int, str, str, str, str]] = []
    query_lower = query.lower()

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        # data/wiki/private/ is never searched — Buyi confidentiality invariant, clause (b).
        # The agent reaches the same pages the MCP server does, so it enforces the
        # same exclusion, via the same predicate.
        if md_file.name.startswith("_") or _is_private(md_file):
            continue
        post = frontmatter.load(md_file)
        title = str(post.get("title") or md_file.stem)
        summary = str(post.get("summary") or "")
        content = post.content

        score = 0
        for term in query_lower.split():
            if len(term) < 3:
                continue
            if term in title.lower():
                score += 3
            if term in summary.lower():
                score += 2
            if term in content.lower():
                score += 1

        if score > 0:
            results.append((score, title, summary, md_file.stem, content))

    if not results:
        return "No pages found matching that query."

    results.sort(reverse=True, key=lambda x: x[0])
    parts = []
    for _, title, summary, page_id, content in results[:8]:
        excerpt = content[:200].replace("\n", " ")
        parts.append(f"**{title}** (id: `{page_id}`)\nSummary: {summary}\nExcerpt: {excerpt}...")

    return "\n\n---\n\n".join(parts)


def _read_page(page_id: str) -> str:
    # Both lookup paths are filtered: a private page must be unreachable by ID and
    # by title alike, or the title fallback becomes the way around the ID check.
    md_file = next(
        (p for p in WIKI_DIR.rglob(f"{page_id}.md") if not _is_private(p)),
        None,
    )
    if not md_file:
        target = page_id.lower().replace("-", " ")
        for f in WIKI_DIR.rglob("*.md"):
            if f.name.startswith("_") or _is_private(f):
                continue
            post = frontmatter.load(f)
            title = str(post.get("title") or f.stem)
            if title.lower() == target:
                md_file = f
                break

    if not md_file:
        return f"Page '{page_id}' not found. Check ID with search_wiki first."

    post = frontmatter.load(md_file)
    title = post.get("title") or md_file.stem
    summary = post.get("summary") or ""
    return f"# {title}\n\nSummary: {summary}\n\n{post.content}"


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
                        if not result.startswith("Page '"):
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

            valid_pages = {p for p in referenced_pages if next(WIKI_DIR.rglob(f"{p}.md"), None)}
            if valid_pages:
                yield {"type": "highlight", "pages": list(valid_pages)}
    except Exception as exc:
        import logging

        logging.getLogger(__name__).exception("Agent stream error: %s", exc)
        yield {"type": "token", "content": "\n\n[An error occurred. Please try again.]"}

    yield {"type": "done"}
