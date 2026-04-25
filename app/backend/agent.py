from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, AsyncGenerator

import frontmatter
from google import genai
from google.genai import types

WIKI_DIR = Path(__file__).parent.parent.parent / "wiki"
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
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


_TOOLS = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="search_wiki",
        description=(
            "Search wiki pages for content matching the query. "
            "Returns page IDs, summaries, and excerpts for the top matches."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "query": types.Schema(
                    type=types.Type.STRING,
                    description="Search query using key terms from the question",
                )
            },
            required=["query"],
        ),
    ),
    types.FunctionDeclaration(
        name="read_page",
        description="Read the full content of a wiki page by its ID (kebab-case filename without .md).",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "page_id": types.Schema(
                    type=types.Type.STRING,
                    description="Page ID as shown in search results, e.g. 'langgraph-crag-pipeline'",
                )
            },
            required=["page_id"],
        ),
    ),
])

_SYSTEM = """You are a knowledge base agent for an agent engineering wiki.
Answer questions about LangGraph, RAG, ADK, MCP, memory patterns, eval, and related topics.

Steps:
1. Use search_wiki to find relevant pages
2. Use read_page to get full content on the most relevant pages (up to 4)
3. Synthesise a grounded, concise answer from what the wiki actually says

Be direct. Stay grounded in the wiki — do not invent content."""

_CONFIG = types.GenerateContentConfig(
    system_instruction=_SYSTEM,
    tools=[_TOOLS],
)


async def run_agent_stream(query: str) -> AsyncGenerator[dict[str, Any], None]:
    client = _get_client()
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=query)])
    ]
    referenced_pages: set[str] = set()

    for _ in range(8):
        # Collect a full response turn (Gemini streams text but tool calls arrive whole)
        full_text = ""
        function_calls: list[types.FunctionCall] = []

        async for chunk in await client.aio.models.generate_content_stream(
            model=MODEL,
            contents=contents,
            config=_CONFIG,
        ):
            if chunk.text:
                full_text += chunk.text
                yield {"type": "token", "content": chunk.text}
            for part in chunk.candidates[0].content.parts if chunk.candidates else []:
                if part.function_call and part.function_call.name:
                    function_calls.append(part.function_call)

        if not function_calls:
            break

        # Add model turn to history
        model_parts: list[types.Part] = []
        if full_text:
            model_parts.append(types.Part(text=full_text))
        model_parts.extend(types.Part(function_call=fc) for fc in function_calls)
        contents.append(types.Content(role="model", parts=model_parts))

        # Execute tools and build function response turn
        response_parts: list[types.Part] = []
        for fc in function_calls:
            args: dict[str, Any] = dict(fc.args or {})
            if fc.name == "search_wiki":
                result = _search_wiki(args.get("query", ""))
                for m in re.finditer(r"\(id: `([^`]+)`\)", result):
                    referenced_pages.add(m.group(1))
            elif fc.name == "read_page":
                page_id = args.get("page_id", "")
                result = _read_page(page_id)
                if not result.startswith("Page '"):
                    referenced_pages.add(page_id)
            else:
                result = "Unknown tool."

            response_parts.append(types.Part(
                function_response=types.FunctionResponse(
                    name=fc.name,
                    response={"result": result},
                )
            ))

        contents.append(types.Content(role="user", parts=response_parts))

    valid_pages = {p for p in referenced_pages if next(WIKI_DIR.rglob(f"{p}.md"), None)}
    if valid_pages:
        yield {"type": "highlight", "pages": list(valid_pages)}

    yield {"type": "done"}
