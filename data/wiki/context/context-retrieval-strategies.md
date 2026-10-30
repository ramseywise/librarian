---
title: Context Retrieval Strategies
tags: [context, rag, llm, agents, concept]
summary: The shift from pre-computed retrieval (decide relevance before inference) to just-in-time context (agent loads what it needs during inference) — with the hybrid default and the pre-retrieval pipeline ordering.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--04-retrieval.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--03-retrieval-strategies.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--reliable-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--reliable-agents.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--reliable-agents.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--context-engineering.md
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

### A Tuned Production Pipeline

A production search platform over decades of scientific study reports shows the same
pipeline after quality plateaued, with numbers filled in:

1. Keyword extraction and **metadata-filter generation** (few-shot) run concurrently.
2. A small fast model **expands the query to 5 variants**.
3. The filter is applied **inside** the vector query — millions of vectors to hundreds.
4. Each variant runs **hybrid search weighted 0.7 dense / 0.3 keyword** — an empirical,
   corpus-specific split; for a new corpus, measure rather than copy.
5. Union across variants, scoring each chunk by its **max** weighted score; keep ~20.
6. **Cross-encoder rerank 20 → 7**, scored against the *original* question.

What generalises: **expansion multiplies retrieval, so the filter must come first**;
**max-score aggregation is a dedup policy** (multi-retrieval rewarded without letting a
chunk win by weak ubiquity); **rerank against the original query**, because expansion is a
recall device and reranking a rewrite compounds its drift.

### Text-to-SQL Is a Retrieval Strategy

Embedding similarity does not count, sum or compare, so filtering and aggregation questions
route to a Text-to-SQL tool, with the same context moves: **schema subsetting** (inject only
the relevant tables), **dynamic few-shot** retrieved from a growable collection of
(question → SQL) pairs, and **deterministic validation** (SELECT-only) — an LLM review step
was removed because it flagged valid queries too often. A retrieval layer spanning
structured and unstructured data needs a **router**, not one index.

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

## RAG Architectures

| Architecture | Shape | Use when |
|---|---|---|
| Naive | embed → top-k → stuff | One-hop facts over a clean corpus |
| Modular | Swappable rewrite → retrieve → rerank → compress → generate | Tune or replace one stage alone |
| Agentic | Model decides whether/what/when to retrieve, loops until enough | Multi-step questions — just-in-time retrieval |
| Graph-enhanced | Retrieval walks extracted entities/relations | Multi-hop, "how is X related to Y" ([[Knowledge Graph Retrieval]]) |

Agentic RAG is ReAct applied to retrieval and the hardest to evaluate, since the path
differs per run. In a side-by-side on legal Q&A, a simple question scored the same either
way (single-pass was faster); a compound one (sentencing given intoxication *and* an
unrelated prior conviction) separated them — the agent searched the sub-questions in
parallel, noticed the missing join (recidivism) and ran a targeted second round. **Use
agentic RAG when questions decompose.** See [[Agentic RAG — Advanced Patterns]].

## Chunking

| Strategy | Splits on | Trade-off |
|---|---|---|
| Fixed + overlap | Token count (e.g. 512, 10–20% overlap) | Simple; cuts across meaning |
| Structural | Headings, functions, table rows | Respects document units; needs format-aware parsing |
| Semantic | Embedding-similarity breakpoints | Coherent; slower ingest, variable size |
| Hierarchical | Small chunks to match, parent sections returned | Precision *and* context; more plumbing |

Chunk size is a recall/precision dial; "retrieve small, return big" sidesteps most of it.
Every chunk loses its surrounding context — [[Contextual Retrieval]] restores it at index
time. When questions need aggregation or rule induction rather than passage lookup, no
chunking fixes it: see [[Index-Time Distillation]].

## Hybrid Retrieval, Stage by Stage

- **Sparse** — BM25's `k1` saturates term frequency, `b` normalises document length, IDF
  makes rare terms dominate. Learned sparse models (SPLADE, BGE-M3's sparse head) learn
  term weights and can add related terms while staying inspectable.
- **Dense** — cosine compares direction, not magnitude; contextual encoders give "bank" a
  per-sentence vector. ANN index: **HNSW** (incremental inserts, more memory, very high
  recall) for live corpora; **ANNOY** (fast build, low memory, full rebuild on change) for
  static ones.
- **Fusion** — dense (~0–1) and BM25 (0 to tens) scores don't share a scale.
  [[Reciprocal Rank Fusion (RRF)]] (`Σ 1/(60 + rank)`) fuses ranks — robust but discards
  signal; normalise-and-weight keeps scores but is hard to tune.
- **Rerank** — a cross-encoder reads query and candidate together; too slow for the
  corpus, so it reranks the fused top ~50. It refines fusion, not replaces it
  ([[RAG Reranking]]).

**Measure each stage, and check metric definitions.** recall@k is closest to what RAG
needs, but many reports mean **hit rate** (≥1 relevant in top k); "retrieval failure rate"
is usually 1 − hit rate@20. MRR measures the first hit's rank; nDCG grades the whole list.
See [[Evaluating Context]].

## Multimodal Ingestion

Native multimodal keeps layout and charts at the highest cost; extract-to-text (OCR,
transcription) is cheap and cacheable but loses anything visual; **extract plus an analysis
tool** (`analyze_image`, `analyze_pdf`) answers most questions from text and returns to the
original only when needed.

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

Prompt caching comes in two vendor shapes: **implicit** (automatic prefix reuse or a
breakpoint marker) and **explicit** (a named cache object with a TTL, referenced by name).
Explicit caches suit "upload a corpus once, ask many questions" — a cheap alternative to
RAG when the whole corpus fits in the window. See [[Cache-Stable Context Layout]].

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

**Governance pushes these checks into the index:**
- **Expiry** — tag chunks with version and effective/expiry dates and filter at query
  time; a superseded policy left in the index is retrieved alongside its replacement.
- **Permissions at the retrieval layer, not after** — once an unauthorised document is in
  context, nothing guarantees it stays out of the answer. Multi-tenant systems isolate
  indexes and metadata per tenant.
- **Retrieved text is the main indirect-injection channel** — tag its source, and never
  let retrieved content alone trigger a side-effecting action; those need their own
  authorisation ([[Prompt Injection]]). Knowledge poisoning is the same attack made before
  indexing.

## Framing Retrieved Content

Wrap retrieved documents in tags carrying `id`, `source` and `updated`, instruct "answer
using only the documents above, cite ids", and add **"if the documents don't contain the
answer, say so"** — the cheapest hallucination guard there is. Source and date metadata
let the model resolve conflicts.

## See Also
- [[Agentic Workflow Patterns]] <!-- auto-linked -->
- [[Context Engineering]] — related (part of)
- [[RAG Retrieval Strategies]] — related
- [[RAG Reranking]] — prerequisite-for
- [[Context Compaction]] — extends
- [[Contextual Retrieval]] — extends
- [[Index-Time Distillation]] — extends
- [[Knowledge Graph Retrieval]] — extends
- [[Evaluating Context]] — prerequisite-for
