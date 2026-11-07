"""Ranked retrieval over the index: BM25 candidates, semantic rerank, typed-edge expansion.

Shared by the MCP tool, the chat agent and the eval harness. Search blends BM25 and cosine
similarity equally; backlinks are deliberately not a ranking signal. Ranking changes must clear
`make eval-gate` on all four arms (see CLAUDE.md, "Retrieval evals").
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import duckdb

from librarian.log_config import get_logger
from librarian.observability import timed
from librarian.retrieval import corpus, embeddings, index
from librarian.retrieval.graph_expansion import expand_one_hop

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Candidate retrieval
# ---------------------------------------------------------------------------


def domain_filter(domain: str) -> tuple[str, list]:
    """SQL fragment + params scoping a query to a domain (directory OR tag).

    Match on directory OR domain tag, not either/or: a page can live in one
    subject directory while carrying another domain's tag (e.g. an interview
    guide filed under foundations/ but tagged `interview`). Filtering by path
    alone silently drops those from a --domain search.
    """
    if not domain:
        return "", []
    domain_dir = corpus.resolve_domain_dir(domain)
    if domain_dir:
        return (
            "AND (path LIKE ? OR lower(tags) LIKE '%' || lower(?) || '%')",
            [str(domain_dir) + "/%", domain],
        )
    return "AND lower(tags) LIKE '%' || lower(?) || '%'", [domain]


_QUERY_PUNCTUATION = "?!.,:;\"'()"


def _like_candidates(
    con: duckdb.DuckDBPyConnection,
    query: str,
    tag_filter: str,
    tag_params: list,
    limit: int,
    table: str = "pages",
) -> list[tuple]:
    """Tokenized per-term OR LIKE fallback when fts is unavailable or matches nothing.

    Each whitespace-separated term matches independently, so a multi-word query
    like "compaction strategies" still finds "strategies for compacting context"
    — the old whole-phrase LIKE required the exact phrase to appear verbatim.
    Pages matching the most terms come first: OR on words like "what" matches nearly every
    page, so sorting on backlinks alone fills the candidate cap with the best-linked pages.
    """
    terms = [t.strip(_QUERY_PUNCTUATION) for t in query.lower().split()]
    terms = [t for t in terms if t] or [query.lower()]
    term_match = "(lower(content) LIKE ? OR lower(title) LIKE ? OR lower(summary) LIKE ?)"
    term_cond = " OR ".join([term_match] * len(terms))
    terms_matched = " + ".join([f"CASE WHEN {term_match} THEN 1 ELSE 0 END"] * len(terms))
    title_cond = " OR ".join(["lower(title) LIKE ?"] * len(terms))
    like_params: list = []
    for t in terms:
        like_params += [f"%{t}%"] * 3
    sql = f"""
        SELECT path, title, tags, summary, content, backlinks, embedding, NULL AS score
        FROM {table}
        WHERE ({term_cond})
        {tag_filter}
        ORDER BY
            {terms_matched} DESC,
            CASE WHEN ({title_cond}) THEN 0 ELSE 1 END,
            backlinks DESC,
            updated DESC
        LIMIT ?
    """
    params = like_params + tag_params + like_params + [f"%{t}%" for t in terms] + [limit * 3]
    return con.execute(sql, params).fetchall()


# ---------------------------------------------------------------------------
# Reranking
# ---------------------------------------------------------------------------

# Measured 2026-11-05 on four golden sets. This blend beat or tied RRF on all of them, and RRF
# with a backlink channel scored MRR 0.547 on questions about uniformly sampled pages (0.767 here).
TEXT_WEIGHT = 0.5
SEMANTIC_WEIGHT = 0.5


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb + 1e-9)


def rerank(query: str, rows: list[tuple], limit: int) -> list[tuple]:
    """Blend text relevance and semantic similarity, best first.

    rows are 8-tuples (path, title, tags, summary, content, backlinks, embedding,
    score); returns 7-tuples with the blended score in place of the embedding.
    BM25 rows carry a real relevance score (normalised against the max), which keeps
    how far ahead the best match is; fallback rows have score NULL, so position in the
    SQL ordering stands in. A row with no embedding scores 0 on similarity.

    Backlinks are deliberately not a signal. They say how central a page is, not whether
    it answers this query, so they buried specific pages under hubs. A golden set whose
    answers are mostly hubs will read that as an improvement: see evals/run_eval.py.
    """
    raw_scores = [r[7] for r in rows]
    max_bm25 = max((s for s in raw_scores if s is not None), default=0.0)

    def text_score(i: int) -> float:
        s = raw_scores[i]
        if s is not None and max_bm25 > 0:
            return s / max_bm25
        return 1.0 - (i / len(rows))

    if embeddings.HAS_EMBEDDINGS and len(rows) > 1:
        try:
            q_vec = embeddings.encode([query])[0].tolist()
            scored = [
                (
                    TEXT_WEIGHT * text_score(i)
                    + SEMANTIC_WEIGHT
                    * (_cosine(q_vec, embeddings.blob_to_floats(row[6])) if row[6] else 0.0),
                    i,
                    row,
                )
                for i, row in enumerate(rows)
            ]
            # Sort on (score, -original index) so equal-scoring rows keep candidate order.
            scored.sort(key=lambda t: (t[0], -t[1]), reverse=True)
            return [(*row[:6], score) for score, _, row in scored[:limit]]
        except Exception as e:
            log.warning("hybrid_rerank_failed", error=str(e))

    return [(*row[:6], text_score(i)) for i, row in enumerate(rows[:limit])]


# ---------------------------------------------------------------------------
# Search core
# ---------------------------------------------------------------------------


def degradation_reasons(
    con: duckdb.DuckDBPyConnection, *, has_fts: bool, check_stale: bool = True
) -> list[str]:
    """Names of the retrieval capabilities currently missing, best-effort.

    `index.open_index()` refreshes the index, so a stale one normally self-heals before
    any search. It stays stale only when that refresh failed (unreadable page,
    write error) — which is exactly the case worth surfacing, because results
    are then served from content that no longer matches disk. `check_stale=False` skips that
    probe for a caller that has just refreshed the index: one freshness pass per request.
    `embeddings_unavailable` means the model failed to load, so ranking is text only.
    """
    reasons: list[str] = []
    if not has_fts:
        reasons.append("no_fts")
    if embeddings.LOAD_ERROR:
        reasons.append("embeddings_unavailable")
    try:
        if check_stale and (index.stale_pages(con) or index.has_deleted_pages(con)):
            reasons.append("stale_index")
    except Exception as e:  # never let a health probe break retrieval
        log.warning("degradation_probe_failed", error=str(e))
    return reasons


def search_rows(
    query: str, domain: str = "", limit: int = 10, tool: str = "search_wiki", expand: bool = False
) -> tuple[list[tuple], list[str]]:
    """Ranked search (see `_search_rows`), inside a `search` span.

    The span records the query's length, never its text.
    """
    with timed(
        "search", **{"search.query_length": len(query), "search.limit": limit, "search.tool": tool}
    ) as sp:
        rows, degraded = _search_rows(query, domain, limit, tool, expand)
        sp.set_attribute("search.result_count", len(rows))
        sp.set_attribute("search.degraded", ",".join(degraded))
        return rows, degraded


def _search_rows(
    query: str, domain: str, limit: int, tool: str, expand: bool
) -> tuple[list[tuple], list[str]]:
    """Ranked search returning raw rows — the single search core.

    An empty `domain` searches the wiki only, as does any wiki directory or tag.
    `course` or `course/<subject>` searches lessons only. The corpora have separate
    BM25 statistics, so their scores are not comparable and are never merged here.

    Returns `(rows, degraded)`: up to `limit` 7-tuples (path, title, tags,
    summary, content, backlinks, score) best first, plus the names of any
    retrieval capabilities that were unavailable for this query (`no_fts`,
    `stale_index`) — empty when the pipeline ran at full strength. Callers that
    surface results to a model or a human are expected to pass that list on;
    silently serving LIKE-fallback results as if they were BM25-ranked is what
    this second element exists to prevent.

    Candidates come from BM25 (DuckDB fts); falls back to a tokenized per-term
    LIKE match when fts is unavailable or matches nothing. Logs retrieval
    telemetry under `tool`.

    expand=True additionally merges pages one typed hop from the results into
    the ranked rows (LIB-114 Step 2). Default off — production `search_wiki`
    keeps its prose expansion section; this path is exercised by the eval.
    """
    table = "pages"
    if corpus.is_course_domain(domain):
        table = "course_pages"
        course_dir = corpus.resolve_course_dir(domain)
        if course_dir is None:
            corpus.log_retrieval(
                tool, query=query, domain=domain, n_results=0, top_paths=[], degraded=[]
            )
            return [], []
        tag_filter, tag_params = "AND starts_with(path, ?)", [f"{course_dir.as_posix()}/"]
    else:
        tag_filter, tag_params = domain_filter(domain)

    con = index.open_index()
    try:
        rows: list[tuple] = []
        fts_ok = index.ensure_fts(con)
        degraded = degradation_reasons(con, has_fts=fts_ok, check_stale=False)
        if fts_ok:
            # A subquery, not an alias in WHERE: duckdb 2.0 rejects that form because
            # match_bm25 has side effects.
            sql = f"""
                SELECT * FROM (
                    SELECT path, title, tags, summary, content, backlinks, embedding,
                           fts_main_{table}.match_bm25(path, ?) AS score
                    FROM {table}
                    WHERE TRUE {tag_filter}
                )
                WHERE score IS NOT NULL
                ORDER BY score DESC
                LIMIT ?
            """
            try:
                rows = con.execute(sql, [query, *tag_params, limit * 3]).fetchall()
            except Exception as e:
                # fts loaded but the query failed — results are about to come
                # from LIKE, so this is the same degradation as no fts at all.
                log.warning("fts_query_failed", error=str(e))
                rows = []
                if "no_fts" not in degraded:
                    degraded.append("no_fts")

        if not rows:
            rows = _like_candidates(con, query, tag_filter, tag_params, limit, table)
    finally:
        con.close()

    if degraded:
        log.warning("retrieval_degraded", tool=tool, reasons=degraded)

    if not rows:
        corpus.log_retrieval(
            tool, query=query, domain=domain, n_results=0, top_paths=[], degraded=degraded
        )
        return [], degraded

    ranked = rerank(query, rows, limit)
    expansion_edges: list[tuple[str, str, str]] = []
    if expand:
        ranked, expansion_edges = _expand_rows(ranked, limit)
    extra = {"expansion_edges": expansion_edges} if expansion_edges else {}
    corpus.log_retrieval(
        tool,
        query=query,
        domain=domain,
        n_results=len(ranked),
        top_paths=[r[0] for r in ranked[:5]],
        degraded=degraded,
        **extra,
    )
    return ranked, degraded


# Score multiplier for expanded pages relative to the best seed that reached
# them. Pre-registered at 0.5 (plan LIB-114, Open Question 4); the eval's
# sensitivity check overrides the module global, so read at call time.
EXPANSION_DECAY = 0.5


def _expand_rows(ranked: list[tuple], limit: int) -> tuple[list[tuple], list[tuple[str, str, str]]]:
    """Merge one-hop typed neighbours into ranked rows (LIB-114 Step 2).

    Each neighbour scores EXPANSION_DECAY × the best score among the seeds that
    reached it. The merge is a stable sort by score with direct rows first, so
    an expanded page never displaces a direct hit whose score meets or exceeds
    its own — it fills ranks after the last such hit. Returns the re-capped
    rows plus the fired edges as (seed, neighbour, relationship) triples.
    """
    seed_scores = {r[0]: r[6] for r in ranked}
    con = index.connect()  # the search just refreshed the index; one freshness pass per request
    try:
        edges = con.execute("SELECT source_path, target_path, relationship FROM edges").fetchall()
        neighbours = expand_one_hop(list(seed_scores), edges, max_expansions=limit)
        if not neighbours:
            return ranked, []
        placeholders = ", ".join("?" for _ in neighbours)
        nb_rows = {
            row[0]: row
            for row in con.execute(
                f"SELECT path, title, tags, summary, content, backlinks FROM pages "
                f"WHERE path IN ({placeholders})",
                [path for path, _, _ in neighbours],
            ).fetchall()
        }
    finally:
        con.close()

    expanded: list[tuple] = []
    fired: list[tuple[str, str, str]] = []
    for nb_path, rel, seeds in neighbours:
        nb_row = nb_rows.get(nb_path)
        if nb_row is None:
            continue
        expanded.append((*nb_row, EXPANSION_DECAY * max(seed_scores[s] for s in seeds)))
        fired.extend((seed, nb_path, rel) for seed in sorted(seeds))

    # Stable sort: equal scores keep direct-before-expanded order, and expanded
    # rows keep expand_one_hop's distinct-seed-count ordering among themselves.
    merged = ranked + expanded
    merged.sort(key=lambda r: r[6], reverse=True)
    return merged[:limit], fired


@contextmanager
def disabled(*capabilities: str) -> Iterator[None]:
    """Run a block with `"fts"` (BM25) and/or `"embeddings"` (semantic rerank) switched off.

    The eval harness's `nofts` and `lex` arms.

    The index is built first, while both still work: a rebuild triggered inside the block
    would persist an embedding-less index that later arms silently rank against, and the arm
    would measure a degraded index instead of degraded retrieval.
    """
    index.open_index().close()
    saved_fts, saved_emb = index.ensure_fts, embeddings.HAS_EMBEDDINGS
    unknown = set(capabilities) - {"fts", "embeddings"}
    if unknown:
        raise ValueError(f"unknown retrieval capability: {sorted(unknown)}")
    if "fts" in capabilities:
        index.ensure_fts = lambda con: False
    if "embeddings" in capabilities:
        embeddings.HAS_EMBEDDINGS = False
    try:
        yield
    finally:
        index.ensure_fts = saved_fts
        embeddings.HAS_EMBEDDINGS = saved_emb
