"""Retrieval over the compiled wiki and the course lessons: one index, one ranking, one API.

Callers (the MCP server, the chat agent, the eval harness) use only the names exported here.

    search(query, domain, limit, expand)  rendered results, as the `search_wiki` tool returns
    search_rows(...)                      ranked rows plus the degradation reasons they ran under
    degraded_notice(reasons)              the warning line to put in front of a model
    read_page(path_or_title)              one page or lesson, private pages excluded
    list_domain(domain), list_pages(...)  listings; domain_briefing(domain) concatenates a domain
    open_index(), rebuild_index()         index lifecycle (refresh-on-open, forced rebuild)
    index_is_built()                      the index file is current-schema (probe; builds nothing)
    embeddings_unavailable()              the rerank cannot run: no extra, or the model failed
    embeddings_ready()                    the model is loaded, or the rerank is off (readiness probe)
    disabled("fts", "embeddings")         switch BM25 / the semantic rerank off, for the evals

Modules: `corpus` (locations, privacy, telemetry), `index` (build, refresh, open), `ranking`
(BM25 + semantic blend, typed-edge expansion), `format` (rendering), `pages` (read and list),
`graph_expansion` (one-hop typed neighbours), `embeddings` (the model, vectors and caches).
"""

from librarian.retrieval.embeddings import embeddings_ready, embeddings_unavailable
from librarian.retrieval.format import degraded_notice
from librarian.retrieval.format import search_text as search
from librarian.retrieval.index import IndexBusyError, index_is_built, open_index, rebuild_index
from librarian.retrieval.pages import domain_briefing, list_domain, list_pages, read_page
from librarian.retrieval.ranking import disabled, search_rows

__all__ = [
    "IndexBusyError",
    "degraded_notice",
    "disabled",
    "domain_briefing",
    "embeddings_ready",
    "embeddings_unavailable",
    "index_is_built",
    "list_domain",
    "list_pages",
    "open_index",
    "read_page",
    "rebuild_index",
    "search",
    "search_rows",
]
