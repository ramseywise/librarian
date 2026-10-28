---
title: Per-Row Content Hash Misses Cross-Row State
tags: [rag, infra, pattern]
summary: "Turning a full rebuild into a content-hash-gated incremental update correctly detects which rows changed. It does not detect derived values that depend on other rows (backlink counts), on inputs outside the row (embedding model version), or on indexes with no row-level update (FTS). Each of those needs its own invalidation rule, or the incremental index slowly diverges from what a full rebuild would produce."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20-librarian-incremental-index.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20-librarian-incremental-index.md
---

# Per-Row Content Hash Misses Cross-Row State

From the librarian incremental-index plan (LIB-124). The MCP server dropped the whole
search index and re-embedded the corpus whenever **any** page was newer than the index's
`built_at`, and it checked on every connection. The fix: store a per-page
`content_hash`, re-embed only pages whose hash changed, and upsert instead of
DROP + recreate. A content-hash embedding cache already existed in the repo. It had been
built for a different consumer (semantic edges) and was never wired into the index path.

The hash answers "did this row's own bytes change?" and nothing else. The plan's risk
section lists every way that falls short:

| Derived state | Why the row hash misses it | Rule |
|---|---|---|
| **Backlink count** on page B | Editing A to *remove* a link to B changes B's count, but B's bytes and hash are unchanged | Recompute backlinks over the full corpus (cheap, no embedding) and upsert every row whose count changed, not only the stale rows |
| **Embedding vector** | The hash covers content, not the model that embedded it. A model change leaves old blobs mixed with new | Record `embedding_model` in the index meta; on mismatch, force a full rebuild, as the embedding cache already did |
| **Full-text index** | DuckDB FTS has no row-level update | Re-run the full FTS pragma on every incremental pass. Accept the cost, and set a revisit trigger (>1 s) |
| **Interrupted update** | Some rows are upserted while `built_at` is not yet bumped | Wrap the upsert and the FTS rebuild in one transaction. If the pragma cannot run inside one, commit the rows first and rebuild FTS separately |
| **Deleted pages** | No file means no hash to compare | Enumerate indexed paths missing from disk |

The general rule: before making a rebuild incremental, list every derived value and ask
what it is a function of. If the answer is "this row's bytes", the row hash gates it.
If it is "other rows", "a config value" or "the whole table", it needs a separate
invalidation key or a cheap full recompute.

## Sequencing: defer when the substrate is being replaced

The plan's verdict was **defer**. A planned migration to Postgres would replace the
whole DuckDB index path. Writes there are row-level, `tsvector` updates per row, and the
"rebuild" concept disappears. Work done now would be thrown away. The plan named
concrete triggers to proceed anyway: the migration stalls, the corpus passes ~500 pages
and rebuild latency becomes user-visible, or the index has to deploy independently. It
kept the steps self-contained so they would not conflict with the port (compare
[[Deferred Decision Status]]).

## See Also
- [[Cached Derivation Without a Recompute Path]] — extends (backlink counts are cached derivations; the incremental path must recompute them)
- [[Embedding Side Table]] — related (keying embeddings by model and recipe makes model drift a separate version axis)
- [[Code Retrieval: Structural Index and Agentic Search]] — related (content-hash incremental re-indexing for code)
- [[Upgrade-Invariant Retrieval Contract]] — related (re-embedding skips unchanged docs by content hash)
- [[Deferred Decision Status]] — instance-of (deferral with named reopen triggers)
