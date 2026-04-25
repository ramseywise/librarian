from __future__ import annotations

import re
from pathlib import Path
from typing import Any, AsyncGenerator

import frontmatter
from anthropic import AsyncAnthropic

WIKI_DIR = Path(__file__).parent.parent.parent / "wiki"

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic()
    return _client


def _search_wiki(query: str) -> str:
    results: list[tuple[int, str, str, str, str]] = []
    query_lower = query.lower()

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name.startswith("_"):
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
    md_file = next(WIKI_DIR.rglob(f"{page_id}.md"), None)
    if not md_file:
        target = page_id.lower().replace("-", " ")
        for f in WIKI_DIR.rglob("*.md"):
            if f.name.startswith("_"):
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

_SYSTEM = """You are a knowledge base agent for an agent engineering wiki.
Answer questions about LangGraph, RAG, ADK, MCP, memory patterns, eval, and related topics.

Steps:
1. Use search_wiki to find relevant pages
2. Use read_page to get full content on the most relevant pages (up to 4)
3. Synthesise a grounded, concise answer from what the wiki actually says

Be direct. Stay grounded in the wiki — do not invent content."""


async def run_agent_stream(query: str) -> AsyncGenerator[dict[str, Any], None]:
    client = _get_client()
    messages: list[dict[str, Any]] = [{"role": "user", "content": query}]
    referenced_pages: set[str] = set()

    for _ in range(8):
        async with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=_SYSTEM,
            tools=_TOOLS,  # type: ignore[arg-type]
            messages=messages,  # type: ignore[arg-type]
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    delta = event.delta
                    if hasattr(delta, "type") and delta.type == "text_delta" and delta.text:
                        yield {"type": "token", "content": delta.text}

            response = await stream.get_final_message()

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            messages.append({
                "role": "assistant",
                "content": [b.model_dump() for b in response.content],
            })
            tool_results: list[dict[str, Any]] = []

            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name == "search_wiki":
                    result = _search_wiki(block.input["query"])  # type: ignore[index]
                    for m in re.finditer(r"\(id: `([^`]+)`\)", result):
                        referenced_pages.add(m.group(1))
                elif block.name == "read_page":
                    page_id = block.input["page_id"]  # type: ignore[index]
                    result = _read_page(page_id)
                    if not result.startswith("Page '"):
                        referenced_pages.add(page_id)
                else:
                    result = "Unknown tool."

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    valid_pages = {p for p in referenced_pages if next(WIKI_DIR.rglob(f"{p}.md"), None)}
    if valid_pages:
        yield {"type": "highlight", "pages": list(valid_pages)}

    yield {"type": "done"}
