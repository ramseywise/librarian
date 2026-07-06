---
name: rag_research
description: "Research a RAG system design decision. Covers retrieval strategies, chunking, embedding models, reranking options, evaluation frameworks, observability, and multi-agent architecture patterns. Use when designing or extending a RAG pipeline and needing a structured trade-off analysis before committing to an approach."
---

Research the following RAG design question: $ARGUMENTS

## Before starting

Identify which layer the question touches. Most RAG decisions fall into one of:
1. **Ingestion** — chunking strategy, metadata schema, completeness gates
2. **Retrieval** — embedding model, vector store, hybrid search, BM25 configuration
3. **Reranking** — cross-encoder vs LLM-listwise, n-candidates, confidence scoring
4. **Planning / routing** — intent classification, query rewriting, multi-query expansion
5. **Generation** — prompt design, response style, citation enforcement, confidence gate
6. **Evaluation** — golden dataset construction, ragas vs deepeval, tracing/observability
7. **Architecture** — single graph vs multi-agent supervisor, registry pattern, state design

Research the relevant layer(s) deeply. Do not produce generic outputs — every finding must be grounded in concrete benchmarks, known failure modes, or prior implementation experience.

---

## Research structure

### Context
- What decision is being made?
- What is already implemented or decided?
- What failure mode or gap is this research addressing?

### Options
For each option, cover:
- **Mechanism**: how it works
- **Latency**: quantified if possible (ms at typical corpus/request size)
- **Quality impact**: benchmark numbers if available (hit rate, precision@k, MRR, faithfulness)
- **Operational cost**: GPU, API cost, infra requirements
- **Data residency / GDPR implications**: if data leaves the system
- **When it degrades**: failure conditions (small corpus, non-English, high-latency budget)

### Known benchmarks to cite (when relevant)
- RAPTOR v1 (German market, dense-only): 43% hit rate, 13% precision@5, 48% hallucination rate
- Hybrid + cross-encoder reranker: 68% hit rate, 0.28 precision@5
- Dense-only vs hybrid vs hybrid+reranker retrieval comparison (see research doc section 13)
- Reranker degrades at <1K chunks (small corpus overfit)
- BM25 with English stemmer silent-fails on Danish morphology

### Decision
- **Recommended approach** with rationale
- **Conditions under which to switch**: what would make you choose the alternative?
- **What to validate**: what to measure in the eval suite to confirm the choice

### Open questions
Questions that can't be answered without running experiments or waiting on external decisions.

---

## Quality rules

- Latency numbers must be realistic — cite typical hardware (CPU vs GPU, request size)
- "Best practice" claims require a source or benchmark
- If a technique requires GPU and GPU availability is unknown, flag this as a day-one blocker
- Danish/multilingual requirements must be treated as hard constraints, not nice-to-haves
- Don't recommend an approach without stating when it breaks down
