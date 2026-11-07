"""One registry of tools for every agent surface.

The chat agent (`librarian.agent.loop`, streamed by `librarian.api`) and the MCP server
(`librarian.mcp.server`) both build their tool lists from `TOOLS`, so a tool's name, parameters
and implementation are written once. A tool may have a variant per surface when the output has
to differ (the chat `search_wiki` returns short excerpts, the MCP one a full ranked listing);
variants share a name and are told apart by `surfaces`.

Parameters are a pydantic model: the JSON schema sent to the model is derived from it, so the
schema and the validation cannot drift. Every tool here is read-only; a tool that writes would
have to set `read_only=False`, and `tools_for` can filter on it.

Request context (a lesson or drill the user has open, a tutor persona) goes through
`ToolContext`: `run_agent_stream(..., context=ToolContext(...))` hands it to every tool call.
Nothing reads it yet; it is the seam a later "assistant in context" feature extends.

Implementations call only the public names of `librarian.retrieval`. Course lesson lookup is
left out on purpose: `librarian.courses.catalog.search_lessons` also returns private lessons,
which no agent surface may show.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, Field, ValidationError

from librarian import retrieval

CHAT: Final = "chat"
MCP: Final = "mcp"

MAX_BRIEFING_CHARS = 40_000


# Start of the text `Tool.run` returns for arguments that fail validation; the chat loop keys
# its `is_error` tool_result on it.
INVALID_ARGS_PREFIX = "Invalid arguments"


@dataclass(frozen=True)
class ToolContext:
    """What a request knows that a tool might need. Empty today; see the module docstring."""

    surface: str = CHAT
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Tool:
    """One tool: its model-facing contract plus the code behind it."""

    name: str
    description: str
    params: type[BaseModel]
    fn: Callable[[Any, ToolContext], str]
    surfaces: frozenset[str]
    read_only: bool = True
    # The parameter the telemetry line records for a call (logs/agent.jsonl `tool_calls`).
    log_arg: str = ""

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema for the parameters, derived from `params`."""
        return _clean(self.params.model_json_schema())

    def anthropic_spec(self) -> dict[str, Any]:
        """The tool in the Anthropic Messages API wire shape."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def run(self, args: Mapping[str, Any], ctx: ToolContext | None = None) -> str:
        """Validate `args` and call the implementation; bad arguments come back as text."""
        try:
            params = self.params.model_validate(dict(args))
        except ValidationError as exc:
            fields = ", ".join(str(e["loc"][0]) for e in exc.errors() if e["loc"])
            return f"{INVALID_ARGS_PREFIX} for {self.name}: {fields}."
        return self.fn(params, ctx or ToolContext())


def _clean(schema: dict[str, Any]) -> dict[str, Any]:
    """Drop pydantic's generated `title` keys: they only restate the field names."""
    props = schema.get("properties", {})
    return {
        **{k: v for k, v in schema.items() if k not in ("title", "properties")},
        "properties": {
            name: {k: v for k, v in spec.items() if k != "title"} for name, spec in props.items()
        },
    }


# --- chat implementations -------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_WIKI_PATH_RE = re.compile(r"\(`(/[^`]+\.md)`\)")


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text, count=1).lstrip()


def chat_search_wiki(query: str) -> str:
    # data/wiki/private/ is never searched — Buyi confidentiality invariant, clause (b).
    # The server's search core indexes only public pages, so the agent inherits the
    # exclusion (and retrieval telemetry) from the single implementation.
    rows, degraded = retrieval.search_rows(query, domain="", limit=8, tool="agent_search")
    # The chat agent sees the same degradation notice the MCP tool emits — it is
    # the signal that a thin result set reflects the retrieval path, not the wiki.
    warning = retrieval.degraded_notice(degraded)
    if not rows:
        return warning + "No pages found matching that query."

    parts = []
    for path, title, _tags, summary, content, _backlinks, _score in rows:
        page_id = Path(path).stem
        excerpt = _strip_frontmatter(content)[:200].replace("\n", " ")
        parts.append(f"**{title}** (id: `{page_id}`)\nSummary: {summary}\nExcerpt: {excerpt}...")

    return warning + "\n\n---\n\n".join(parts)


def chat_read_page(page_id: str) -> str:
    # Private pages are unreachable by ID and by title alike — the server core
    # applies the same predicate on every lookup path.
    return retrieval.read_page(page_id)


def chat_domain_briefing(domain: str) -> str:
    """Outline of a domain or course module: titles and summaries, not page bodies.

    The MCP tool of the same name concatenates every page, which is 230k characters for rag
    and 2.2M for patterns: too much for one chat turn. Private domains are refused by the
    server core, and the listing is sorted by backlinks, so a cut keeps the best-linked pages.
    """
    listing = retrieval.list_domain(domain)
    listing = _WIKI_PATH_RE.sub(lambda m: f"(id: `{Path(m.group(1)).stem}`)", listing)
    if len(listing) > MAX_BRIEFING_CHARS:
        cut = listing.rfind("\n- **", 0, MAX_BRIEFING_CHARS)
        listing = f"{listing[:cut]}\n\n[Listing cut to its best-linked pages.]"
    return listing


# --- parameter models -----------------------------------------------------------------------


class _ChatSearch(BaseModel):
    query: str = Field(description="Search query using key terms from the question")


class _ChatRead(BaseModel):
    page_id: str = Field(
        description="Page ID as shown in search results, e.g. 'langgraph-crag-pipeline'"
    )


class _ChatBriefing(BaseModel):
    domain: str = Field(
        description=(
            "A wiki directory such as 'rag', or a course module such as "
            "'course/data-analytics/02-probability-and-statistics'"
        )
    )


class _McpSearch(BaseModel):
    query: str = Field(description="Search terms")
    domain: str = Field(
        default="",
        description="Optional domain to scope the search — any directory under\n    data/wiki/ (e.g. 'rag', 'langgraph', 'patterns') or a domain tag.\n    'course' searches all course lessons, 'course/<subject>' one course\n    (e.g. 'course/ai-engineering'). Omitted: results are ranked wiki pages,\n    followed by a short separate list of the best-matching lessons.",
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max results (default 10, max 50)")
    expand: bool = Field(
        default=False,
        description='SPIKE — also return pages one typed relationship hop from the\n    results (`prerequisite-for` / `extends`). Answers "what else do\n    I need to understand these hits?" Off by default.',
    )


class _McpRead(BaseModel):
    path_or_title: str = Field(
        description="A relative path like 'data/wiki/rag/rag-retrieval-strategies.md',\n           a page title like 'RAG Retrieval Strategies', or a lesson as\n           'course/<subject>/<module>/<lesson>.md'. Titles resolve to wiki pages only."
    )


class _McpListDomain(BaseModel):
    domain: str = Field(
        description="Domain directory name — any directory under data/wiki/\n    (e.g. rag, langgraph, context, interview). 'course' lists the courses,\n    'course/<subject>' its modules, 'course/<subject>/<module>' its lessons."
    )


class _McpBriefing(BaseModel):
    domain: str = Field(
        description="Domain directory name — any directory under data/wiki/\n    (e.g. rag, langgraph, context, interview)\n\n    'course/<subject>/<module>' briefs one course module. Larger course scopes\n    are refused when they exceed COURSE_BRIEFING_MAX_CHARS."
    )


class _McpListPages(BaseModel):
    tag: str = Field(
        default="", description="Domain tag to filter (e.g. 'adk', 'langgraph', 'rag')"
    )
    directory: str = Field(
        default="",
        description="Subdirectory to list — any domain directory under data/wiki/\n       (e.g. rag, langgraph, context, interview), or 'course' or\n       'course/<subject>' for lessons. Omitted: the wiki, then all lessons.",
    )


# --- MCP tool descriptions, as the old @mcp.tool docstrings sent them (summary only; the
# argument text lives in the models above, where FastMCP used to lift it from "Args:"). ---


_MCP_SEARCH_DOC = inspect.cleandoc("""
    Search the wiki and course lessons using hybrid search (BM25 + semantic).

    Results are ranked by an equal blend of BM25 relevance and semantic closeness
    (if sentence-transformers is installed). Backlinks are not a ranking signal.
    """)

_MCP_READ_DOC = inspect.cleandoc("""
    Read a specific wiki page or course lesson by file path or title.
    """)

_MCP_LIST_DOMAIN_DOC = inspect.cleandoc("""
    List all pages in a domain directory, ordered by backlink count.

    This is an O(1) filesystem operation — no embedding or search needed.
    """)

_MCP_LIST_PAGES_DOC = inspect.cleandoc("""
    List wiki pages and course lessons, optionally filtered by tag or directory.
    """)

_MCP_BRIEFING_DOC = inspect.cleandoc("""
    Return a structured build briefing for a domain — all pages concatenated.

    Use this before starting work in a domain to load all accumulated patterns,
    decisions, and tradeoffs into context.
    """)

_ONLY_CHAT = frozenset({CHAT})
_ONLY_MCP = frozenset({MCP})

TOOLS: Final[tuple[Tool, ...]] = (
    Tool(
        name="search_wiki",
        description=(
            "Search wiki pages for content matching the query. "
            "Returns page IDs, summaries, and excerpts for the top matches."
        ),
        params=_ChatSearch,
        fn=lambda p, _ctx: chat_search_wiki(p.query),
        surfaces=_ONLY_CHAT,
        log_arg="query",
    ),
    Tool(
        name="read_page",
        description="Read the full content of a wiki page by its ID (kebab-case filename without .md).",
        params=_ChatRead,
        fn=lambda p, _ctx: chat_read_page(p.page_id),
        surfaces=_ONLY_CHAT,
        log_arg="page_id",
    ),
    Tool(
        name="get_domain_briefing",
        description=(
            "Outline a whole area: every page's title and summary, ready for read_page. "
            "Use it when asked to brief on a domain or course module."
        ),
        params=_ChatBriefing,
        fn=lambda p, _ctx: chat_domain_briefing(p.domain),
        surfaces=_ONLY_CHAT,
        log_arg="domain",
    ),
    Tool(
        name="search_wiki",
        description=_MCP_SEARCH_DOC,
        params=_McpSearch,
        fn=lambda p, _ctx: retrieval.search(
            p.query, domain=p.domain, limit=p.limit, expand=p.expand
        ),
        surfaces=_ONLY_MCP,
        log_arg="query",
    ),
    Tool(
        name="read_page",
        description=_MCP_READ_DOC,
        params=_McpRead,
        fn=lambda p, _ctx: retrieval.read_page(p.path_or_title),
        surfaces=_ONLY_MCP,
        log_arg="path_or_title",
    ),
    Tool(
        name="list_domain",
        description=_MCP_LIST_DOMAIN_DOC,
        params=_McpListDomain,
        fn=lambda p, _ctx: retrieval.list_domain(p.domain),
        surfaces=_ONLY_MCP,
        log_arg="domain",
    ),
    Tool(
        name="list_pages",
        description=_MCP_LIST_PAGES_DOC,
        params=_McpListPages,
        fn=lambda p, _ctx: retrieval.list_pages(tag=p.tag, directory=p.directory),
        surfaces=_ONLY_MCP,
        log_arg="directory",
    ),
    Tool(
        name="get_domain_briefing",
        description=_MCP_BRIEFING_DOC,
        params=_McpBriefing,
        fn=lambda p, _ctx: retrieval.domain_briefing(p.domain),
        surfaces=_ONLY_MCP,
        log_arg="domain",
    ),
)


def tools_for(surface: str, names: Sequence[str] | None = None) -> list[Tool]:
    """The tools a surface exposes, in registry order; `names` narrows (and checks) the set."""
    found = [t for t in TOOLS if surface in t.surfaces]
    if names is None:
        return found
    by_name = {t.name: t for t in found}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise KeyError(f"No {surface} tool named {', '.join(missing)}")
    return [by_name[n] for n in names]
