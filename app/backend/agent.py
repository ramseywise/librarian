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

    try:
        # Tool-call turns: use non-streaming so chunk.text ambiguity with function_call
        # parts doesn't swallow the response text. Stream only the final text turn.
        for _ in range(8):
            response = await client.aio.models.generate_content(
                model=MODEL,
                contents=contents,
                config=_CONFIG,
            )
            candidate = response.candidates[0] if response.candidates else None
            parts: list[types.Part] = (
                candidate.content.parts
                if candidate and candidate.content and candidate.content.parts
                else []
            )
            function_calls = [p.function_call for p in parts if p.function_call and p.function_call.name]

            if not function_calls:
                # Final answer turn — stream it for real UX
                async for chunk in await client.aio.models.generate_content_stream(
                    model=MODEL,
                    contents=contents,
                    config=_CONFIG,
                ):
                    if chunk.text:
                        yield {"type": "token", "content": chunk.text}
                break

            # Execute tool calls and append to history
            model_parts: list[types.Part] = [types.Part(function_call=fc) for fc in function_calls]
            contents.append(types.Content(role="model", parts=model_parts))

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
    except Exception as exc:
        yield {"type": "token", "content": f"\n\n[Error: {exc}]"}

    yield {"type": "done"}
