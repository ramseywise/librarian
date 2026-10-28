---
title: Freshness Key Blind to Content Semantics
tags: [rag, infra, pattern]
summary: "A persisted index whose freshness check keys only on schema version and source mtimes never notices a code change to what gets stored, or a runtime flag that changes it. Rebuilding is skipped and queries quietly run against a degraded index. Bump the schema version whenever stored semantics change, and never let a rebuild fire while a degrading flag is set."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--CHANGELOG.md
---

# Freshness Key Blind to Content Semantics

Librarian's MCP server keeps its search index in a DuckDB file and rebuilds it only when
the freshness check fails. That check compares a `SCHEMA_VERSION` constant and the wiki
files' mtimes. Neither one notices when the *code* that decides what gets stored changes,
or when a runtime flag changes it. The changelog records the same trap at least four
times.

## Instances

| Change | What would have happened without a bump | Outcome |
|---|---|---|
| Index starts skipping `_`-prefixed files | Old index keeps `_index.md` etc., inflating backlinks | Version 2→3 forces rebuild |
| Stored paths become absolute; a BM25 full-text index is added | Existing DB never rebuilds; full-text missing, so search silently falls back to tokenized LIKE (live hit rate 0.58 vs 1.00) | Version 3→4, added as a deviation from the plan, which had not asked for it |
| Typed-edges table materialized at build | Expansion reads a table that does not exist | Version 5→6 |
| Eval "lexical arm" flips `HAS_EMBEDDINGS=False` | Index rebuilt *after* the flip and persisted without embeddings. Later semantic and graph arms would rank against it with nothing in the freshness key to notice | Caught in smoke test; damaged index deleted; lex arm now builds the index *before* flipping the flag |

The fallback is the dangerous part. A missing full-text index or a missing embedding column
does not raise. The search core degrades to a weaker path and still returns plausible
results, so the defect shows up as a quality drop, not an error.

## The rules

1. **Any change to what `build_index` writes is a schema change.** That covers which files
   are included, path format, new tables, new columns, and new derived indexes. Bump the
   version in the same commit. Plans tend to miss this, because the plan snippet describes
   the feature, not the persistence consequence.
2. **Runtime flags that change what gets built must never be live during a build.** Force
   the build first, then flip the flag. Better still, put the flag into the freshness key.
3. **Make the fallback visible.** Log which retrieval path actually ran (BM25 vs LIKE,
   embeddings vs none), so a degraded index shows up in telemetry instead of only in an eval.
4. **A content hash beats mtime** for detecting source change. It does not replace the
   semantic version. Hashes catch *input* drift. Only the version catches *builder* drift.

## See Also
- [[Name-Only Sync Guards Miss Content Drift]] — extends (a guard that checks presence, not content)
- [[Fixture Eval Blind to the Swapped Component]] — extends (a gate that cannot see the component that changed)
- [[Silent Failure Catalogue]] — instance-of
- [[Knowledge Base Recompile Stage]] — extends (the tombstone filter is another builder-semantics change)
