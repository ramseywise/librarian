---
title: Context Retrieval Strategies
tags: [llm, agents, rag, concept]
summary: The shift from pre-computed retrieval (decide relevance before inference) to just-in-time context (agent loads what it needs during inference) — with the hybrid default and the pre-retrieval pipeline ordering.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--03-retrieval-strategies.md
---

# Context Retrieval Strategies

How content gets into the window — the **Select** lever of [[Context Engineering]], and the
biggest architectural shift in the pillar.

## The Shift

**RAG-era assumption: retrieve before inference.** Embed the corpus, embed the query, pull
top-k chunks, stuff the window, generate. All retrieval happens before the model does
anything.

**Agentic assumption: retrieve during inference.** Give the model tools and lightweight
identifiers; let it decide what to load, when, based on what it has learned so far.
Anthropic calls this **just-in-time context**.

> The difference is **who decides relevance**. Pre-computed retrieval makes an
> embedding-similarity guess *before seeing the model's reasoning*. Just-in-time lets
> relevance be determined by an agent that has already read the first file and now knows
> which one it actually needs.

## Just-in-Time Context

Maintain **lightweight identifiers** and load at runtime: file paths, stored queries, web
links, record IDs, table names, search commands.

A file path costs ~10 tokens; the file costs 5,000. If the agent needs three of the fifty
files a pre-retrieval step would have loaded, identifiers spend ~500 tokens on the index
and 15,000 on the three files actually read — instead of 250,000 on all fifty.

**Progressive disclosure** is the behavioural pattern: the agent discovers context
incrementally through exploration, each read informing the next. It mirrors how a human
engineer approaches an unfamiliar codebase — `ls`, then `grep`, then read the three files
that matter. Nobody reads the repo front to back first.

**Metadata carries signal for free.** A path like `tests/integration/test_auth_retry.py`
tells the agent about scope, purpose, and relationship before a single byte is read.
*Naming conventions are a retrieval optimization.*

### Costs

- **Latency** — sequential tool calls are slower than one upfront retrieval; each
  exploration round-trip is a full inference.
- **Wandering** — the agent can explore unproductively, burning context on the search
  itself rather than the answer.
- **Non-determinism** — two runs may load different files, complicating evals and
  reproducibility.

## The Hybrid Default

Pre-load what is cheap and near-certainly needed; leave the long tail to runtime.

| Pre-load (fixed cost, high hit rate) | Just-in-time (variable, long tail) |
|---|---|
| Project conventions file | Any specific source file |
| Directory tree / file index | Full API reference sections |
| Schema summaries | Historical records |
| Recently touched files | Log output, test output |

**The design question that decides it:** *is this needed on ≥80% of turns?* Yes → pre-load.
No → identifier plus a tool to fetch it.

## Pre-Retrieval Pipeline

When you do retrieve upfront, stages compose in this order — **each narrows the candidate
set, so cheap filters go first**.

```
User Query
      ↓
Metadata Filtering       <- cheapest; drop by permission, date, source, tenant
      ↓
Vector Search            <- semantic top-k over what survived
      ↓
Context Ranking          <- rerank with a cross-encoder; send only top of rerank
      ↓
Deduplication            <- collapse near-identical chunks
      ↓
Compression              <- reduce each doc to what answers *this* query
      ↓
Memory Injection         <- add cross-session facts
      ↓
Structured Formatting    <- tag and delimit; never dump raw text
      ↓
LLM
```

- **Metadata filtering first.** Permission and freshness checks are near-free compared to
  embedding search. Push the filter *into* the vector query rather than applying it to
  results. Permission filtering here is a **security control**, not just an optimization.
- **Ranking ≠ retrieval.** Bi-encoder vector search is fast and approximate; a
  cross-encoder reranker is slow and accurate. *Retrieve wide, rerank, send narrow.* See
  [[RAG Reranking]].
- **Deduplication has a trap.** A chunk retrieved by multiple sub-queries is often the
  *most* relevant one, not redundant noise. Collapse duplicates but treat multi-retrieval
  as a **positive ranking signal**. See [[Reciprocal Rank Fusion (RRF)]].
- **Compression is query-conditional.** Reduce each document to the portion answering the
  *current* question — a generic summary discards the specific detail the query needed.
- **Structured formatting.** Wrap in tags with source attribution so the model can cite and
  so injected content stays distinguishable from instructions. See
  [[XML Prompt Structuring]].

## Dynamic Context Windows

Scale retrieval depth to task complexity rather than using a fixed k:

| Task shape | Chunks |
|---|---|
| Simple factual lookup | few — more is pure dilution |
| Comparison / synthesis across sources | more — needs breadth |
| Ambiguous or exploratory | retrieve wide, rerank hard, send narrow |

**Fixed k is a bug in both directions:** it over-fills simple queries (rot) and under-fills
complex ones (missing evidence).

## Hierarchical Retrieval

For large corpora, retrieve in tiers: search summaries or section headers first, fetch full
content only for matched sections. This is **just-in-time applied inside a pre-retrieval
pipeline** — the tier-1 index is the lightweight identifier.

## Ingestion Determines the Ceiling

**Retrieval can only return what parsing extracted.** A text-only parser over a PDF-heavy
corpus silently drops every chart, diagram, and table into nothing or garbled text. The
retrieval layer then *looks* broken — low recall, irrelevant chunks — when the actual
failure happened at ingestion.

> Check what the parser produced before tuning k, rerankers, or chunk size.

See [[RAG Knowledge Preparation]].

## Two Caches, Often Confused

- **Prompt caching** (inference-level) — caches prefill computation for a token prefix.
  Prefix-match only, so *ordering governs hit rate*. See [[Context Anatomy]].
- **Retrieval caching** (application-level) — caches the *results* of expensive retrieval
  keyed by query similarity. A near-duplicate query reuses the prior result set instead of
  re-running search. See [[Semantic Cache for RAG Agents]].

## Context Validation

Retrieved content is **not trustworthy by default**:

- Remove outdated documents (freshness threshold)
- Enforce permissions — never surface content the requester cannot access
- Detect conflicting information across sources; **surface the conflict rather than
  silently picking one**
- Verify citations resolve to real, retrievable sources

Conflict detection matters most: two retrieved documents contradicting each other, both
injected silently, is a reliable path to a confidently wrong answer. This is **context
clash** — see [[Context Failure Modes]].

## See Also
- [[Agentic Workflow Patterns]] <!-- auto-linked -->
- [[Context Engineering]] — part-of
- [[RAG Retrieval Strategies]] — implements
- [[RAG Reranking]] — depends-on
- [[Context Compaction]] — extends
