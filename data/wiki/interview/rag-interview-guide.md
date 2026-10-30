---
title: RAG Interview Study Guide
tags: [rag, interview, reference]
summary: Exam-prep reference for RAG architecture questions — component choices, architecture variants, production judgment, measured benchmarks, and terminology traps.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--3-rag--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--rag.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--rag.md
  - data/raw/repos/sisyphus/interviewing--guides--3-rag--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--3-rag--00-overview.md
---

# RAG Interview Study Guide

The default enterprise GenAI pattern and the most likely deep-dive topic in AIE/FDE loops. Interviewers probe three levels: component choices, architecture selection, and production judgment.

## Core Pipeline

Ingest: chunk → embed → index. Query: (rewrite) → retrieve → (rerank) → generate → (verify).

**Chunking** — structure-first (headings), then recursive paragraph/sentence splits to ~512-token budget with ~64-token overlap. Parent/child chunking helps long documents. Silent failure: `min_tokens` filter drops short-but-valid FAQ answers from the index entirely.

**Embeddings** — multilingual corpora need multilingual models (`multilingual-e5-large`). E5-family gotcha: the `"query: "` / `"passage: "` prefix rule is mandatory — violating it silently degrades recall ~15–20%. Small English-only models fail silently on non-English text.

**Vector stores** — ChromaDB/DuckDB for dev; pgvector/OpenSearch for production multi-tenant. See [[Vector Database Comparison]].

**Hybrid search** — vector-only misses exact tokens; BM25-only misses paraphrases. Fuse with [[Reciprocal Rank Fusion (RRF)]]: `1/(k+rank_bm25) + 1/(k+rank_vec)`, k=60. RRF beats score-weighting because BM25 and cosine scores have incomparable distributions.

**Reranking** — cross-encoder rerank of top-N is the single highest-leverage add-on. Production benchmark: dense-only 45% → hybrid RRF 58% → hybrid + cross-encoder 68% hit rate. Cite numbers. See [[RAG Reranking]].

## Architecture Menu

| Pattern | Mechanism | Use when |
|---|---|---|
| Standard RAG | retrieve top-k → prompt → generate | baseline; always implement first |
| Conversational RAG | + dialogue state, query condensation | chat products |
| [[CRAG Retry Logic\|CRAG]] | confidence-gate → retry/fallback | accuracy-critical |
| Self-RAG | LLM emits reflection tokens mid-generation | retrieval is expensive, many queries don't need it |
| Adaptive RAG | router → simple/complex pipelines | mixed workloads, cost control |
| HyDE | LLM writes hypothetical answer, embed that for search | vague queries vs dense docs |
| Agentic RAG | retrieval as tool in planner → executor loop | multi-step reasoning |
| GraphRAG | KG traversal + vector search | relationship queries |

**Terminology trap:** Some blogs use "Self-RAG" for LLM query expansion. The canonical Self-RAG (Asai et al.) is reflection-token generation — the model emits `[Retrieve]`, `[IsRel]`, `[IsSup]` tokens mid-stream. If an interviewer's definition differs, surface the ambiguity — that scores.

**CRAG vs Self-RAG in one line:** CRAG decides in the graph topology before generation; Self-RAG decides inside the LLM during generation.

## Eval

- Offline: precision@k, recall@k, MRR on golden dataset
- Runtime: faithfulness (is the answer grounded?), contextual relevance (are retrieved chunks relevant?)
- The retriever quality ceiling: a better LLM cannot compensate for poor retrieval

## Production Failure Modes

- Silent chunking drop (min_tokens filter)
- E5 prefix violation → silent recall degradation
- Stale index → retrieval returns outdated facts
- Hallucination with citation — the model cites a real source for a wrong claim

## Follow-ups on memory and retrieval design (answer sketches)

*Provisional:* condensed from the reference answers to the chapter questions in *AI Agents in Depth* (Li), which the book itself flags as AI-drafted with light human review. Treat these as answer shapes to check, not settled claims.

- **Two different home addresses across sessions.** Extract → compare → decide: retrieve similar
  memories and let an LLM choose add / update / delete / no-op (the Mem0 shape). Address-type facts keep
  the latest version with a timestamp; history-type facts keep every version.
- **Source documents contradict each other.** Put version, effective/expiry dates and source in chunk
  metadata; filter or flag expired content; fold authority and freshness into the reranker; flag
  inter-chunk contradictions at index time.
- **The model never searches because it does not know what it does not know.** Make "is this enough?"
  an explicit step (retrieve sub-questions, find the missing link, search again) and keep a lightweight
  overview of the store resident so the agent knows what exists.
- **Does long context make chunking obsolete?** Partly — chunk tuning matters less. But attention is
  soft retrieval that cannot aggregate across a corpus, and freshness, tenant isolation, audit and cost
  do not depend on the model.
- **RAPTOR or GraphRAG?** RAPTOR for overview-to-detail drill-down across summary levels; GraphRAG for
  multi-hop relations, entity disambiguation and corpus themes via community summaries.
- **When does a file-system knowledge base beat a vector store?** When humans and agents maintain it
  together: readable, editable, versioned, agent-writable, with tiered progressive disclosure saving
  tokens. It needs index pages and cross-links or retrieval degrades as it grows — the shape of this
  wiki.

## See Also
- [[Durable vs Performative Knowledge Split]] <!-- auto-linked -->
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Agentic RAG — Advanced Patterns]] — extends
- [[RAG Evaluation]] — instance-of
- [[Reciprocal Rank Fusion (RRF)]] — instance-of
- [[Agents Interview Study Guide]] — extends
- [[Situation-Indexed Decision Tree]] — extends (the RAG spine links down into this guide)
- [[AIE Code-Test Flaw Taxonomy]] — instance-of (where this knowledge is graded as shipped code)
- [[AI Engineering Field Question Bank]] — related (cold-recall questions for this pillar)
