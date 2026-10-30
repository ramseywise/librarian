---
title: Pure Derivation Is a Generated Column
tags: [patterns, infra, rag, decision]
summary: "Whether a derived index belongs in a side table or a generated column depends on whether the derivation is pure SQL over the same row: an embedding (external model call, many recipes per row) earns a side table with hash-gated backfill, a tsvector/trigram index does not — GENERATED ALWAYS ... STORED keeps it in sync with zero application code and no backfill, provided every function in the expression is IMMUTABLE."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
---

# Pure Derivation Is a Generated Column

From adding a lexical retrieval arm (`tsvector` in German and English, plus a trigram
index) next to an existing semantic arm in an events-discovery product (repo akira,
2026-09-25). The first sketch copied the semantic arm's shape: a polymorphic side table
plus a backfill CLI. The refine pass dropped it.

## The decision rule

Ask two questions about the derived value:

1. **Can the database compute it from columns already on the row?**
2. **Does a row need more than one version of it at once?**

An embedding fails both. It comes from an external model call, and the comparison work
needs several `(model, recipe)` vectors per row. That earns a side table with
`input_text_hash`-gated backfill (see [[Embedding Side Table, Not Column]]).

A `to_tsvector()` or trigram derivation passes both. It is deterministic SQL over
`descriptors` and `description`, and one version is enough. So the index becomes two
`GENERATED ALWAYS AS (...) STORED` columns directly on the enrichment table:

- Every existing row is populated when the migration runs. **There is no backfill step**,
  and nothing to mirror from the embedding backfill's mapper/shell/CLI shape.
- Every later insert or update from the existing writeback populates them for free.
- Both arms index the **same input text** (the SQL form of the embedding recipe), so they
  stay comparable: same text, two match mechanisms.

The trade-off was stated openly: the lexical index is tied to one table instead of the
polymorphic `content_kind` shape. Widening to other content kinds later means repeating
the columns per table. That was accepted because the wider slice was unscheduled, and a
shared table with no non-venue readers would be a column with no reader (see
[[Every Column Names Its Reader]]).

## The IMMUTABLE trap

A generated column only accepts IMMUTABLE functions. The plan's SQL did not apply.

- `array_to_string(anyarray, text)` is **STABLE**, even for a `text[]` argument, because
  the polymorphic signature is tagged conservatively.
- `to_tsvector(regconfig, text)` is **IMMUTABLE**. A regconfig literal like `'german'`
  folds to a constant at parse time.

The first build session misread the error and wrapped both functions in hand-declared
IMMUTABLE SQL wrappers. Its explanatory comment had the reasoning backwards. A second
session checked `pg_proc.provolatile` directly, found only `array_to_string` was STABLE,
removed the needless `to_tsvector` wrapper, and kept one wrapper,
`immutable_array_to_string(text[], text)`. Postgres trusts a SQL function's declared
volatility without verifying it. That is safe here because the inputs are row-owned
columns and two built-in configs. Each wrapper gets the same named-role
`revoke ... from public, anon, authenticated` as any other function.

**Look up volatility in the catalog (`pg_proc.provolatile`). Don't infer it from the error
message.**

## Costs to price before repeating it

- `ALTER TABLE ... ADD COLUMN ... GENERATED ALWAYS ... STORED` **rewrites the whole
  table** under an `ACCESS EXCLUSIVE` lock. On a pilot table of a few hundred rows that
  takes under a second. A production-scale table needs re-costing first.
- These were the schema's first GIN and trigram indexes. A schema-diff check confirms
  they exist as written, not just that the migration ran (see
  [[Migration Done Means Pushed and Probed]]).

## See Also
- [[Embedding Side Table, Not Column]] — alternative-to (the impure, multi-version case that does need a side table)
- [[Reciprocal Rank Fusion (RRF)]] — prerequisite-for (fuses this lexical arm with the semantic arm)
- [[Every Column Names Its Reader]] — extends (why no shared polymorphic lexical table)
- [[Migration Done Means Pushed and Probed]] — related (verifying the index exists as written)
- [[Kiez Project]] — instance-of
- [[SQL Indexes and Query Plans]] — prerequisite-for (expression indexes, and why a leading-wildcard LIKE needs trigram)
