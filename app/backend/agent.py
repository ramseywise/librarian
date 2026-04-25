from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, AsyncGenerator

import frontmatter
import ollama

WIKI_DIR = Path(__file__).parent.parent.parent / "wiki"
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

_client: ollama.AsyncClient | None = None


def _get_client() -> ollama.AsyncClient:
    global _client
    if _client is None:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        _client = ollama.AsyncClient(host=host)
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
        "type": "function",
        "function": {
            "name": "search_wiki",
            "description": (
                "Search wiki pages for content matching the query. "
                "Returns page IDs, summaries, and excerpts for the top matches."
            ),
            "parameters": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "read_page",
            "description": "Read the full content of a wiki page by its ID (kebab-case filename without .md).",
            "parameters": {
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
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": query},
    ]
    referenced_pages: set[str] = set()

    for _ in range(8):
        full_content = ""
        tool_calls: list[Any] | None = None

        async for chunk in await client.chat(
            model=MODEL,
            messages=messages,
            tools=_TOOLS,
            stream=True,
        ):
            if chunk.message.content:
                full_content += chunk.message.content
                yield {"type": "token", "content": chunk.message.content}
            if chunk.message.tool_calls:
                tool_calls = chunk.message.tool_calls

        if not tool_calls:
            break

        messages.append({
            "role": "assistant",
            "content": full_content,
            "tool_calls": [
                {"function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in tool_calls
            ],
        })

        for tc in tool_calls:
            name = tc.function.name
            args: dict[str, Any] = tc.function.arguments

            if name == "search_wiki":
                result = _search_wiki(args["query"])
                for m in re.finditer(r"\(id: `([^`]+)`\)", result):
                    referenced_pages.add(m.group(1))
            elif name == "read_page":
                page_id = args["page_id"]
                result = _read_page(page_id)
                if not result.startswith("Page '"):
                    referenced_pages.add(page_id)
            else:
                result = "Unknown tool."

            messages.append({"role": "tool", "content": result})

    valid_pages = {p for p in referenced_pages if next(WIKI_DIR.rglob(f"{p}.md"), None)}
    if valid_pages:
        yield {"type": "highlight", "pages": list(valid_pages)}

    yield {"type": "done"}
