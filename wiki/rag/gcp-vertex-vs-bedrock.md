---
title: GCP Vertex AI Search vs AWS Bedrock KB
tags: [rag, infra, comparison]
summary: Head-to-head comparison of GCP Discovery Engine and AWS Bedrock Knowledge Bases as managed RAG backends — covering search semantics, session state, answer ownership, and when to consider switching.
updated: 2026-07-06
sources:
  - raw/claude-docs/project-g/docs/rag/gcp-vertex-vs-bedrock.md
---

# GCP Vertex AI Search vs AWS Bedrock KB

| | **AWS Bedrock KB** | **GCP Vertex AI Search (Discovery Engine)** |
|---|---|---|
| **Underlying store** | OpenSearch Serverless | Google proprietary search stack |
| **Indexing** | Data source sync (S3, web crawl…) | Data store ingestion (web crawl, Intercom, GCS…) |
| **Chunking** | Bedrock-managed hierarchical (leaf + parent) | Managed chunk mode — boundaries opaque |
| **Hybrid search** | Dense (HNSW) + BM25 — `HYBRID` hardcoded | Internal, not configurable |
| **Reranking** | `amazon.rerank-v1:0` — explicit config | Internal to `:answer` endpoint; not exposed in Search API |
| **Raw scores via API** | ✅ cosine similarity (0–1) fast; reranker score (0.05–0.35) | ✅ `relevance_score` per chunk result |
| **Grounding score** | Not returned | ✅ `answer.grounding_score` (`:answer` endpoint) |
| **Session management** | Stateless — caller owns session | ✅ Native session concept, persisted in Firestore for multi-replica |
| **Answer generation** | Caller sends passages to LLM | Optional: `:answer` endpoint generates answer internally |
| **EU data residency** | `eu-north-1`, `eu-central-1` | `eu` location endpoint |

---

## Architecture in Each Codebase

### Bedrock KB Architecture

```
User query
  │
  ├─ retrieve() — fast, cosine, top-5, no rerank      (AgentTool)
  └─ retrieve_reranking() — top-15, reranker pass      (Eval / complex)
        │
        └── Bedrock KB (OpenSearch HYBRID)
               ├── AMAZON_BEDROCK_TEXT_CHUNK  ← leaf match
               └── AMAZON_BEDROCK_TEXT         ← parent context → sent to LLM
```

### GCP Discovery Engine — Three Modes

```
Mode A — Local pgvector
  PostgreSQL + pgvector, Gemini embeddings, exact cosine search

Mode B — GCP Agentic RAG
  ADK agentic loop: classify → search → grade → rewrite → search
  GCP Discovery Engine does retrieval; Gemini grades + synthesizes

Mode C — GCP Built-in Answer (:answer endpoint)
  GCP owns retrieval + ranking + answer generation
  Thin wrapper: send query, stream tokens back
```

---

## Key Behavioural Differences

### Language Handling
- **Bedrock KB:** language-agnostic — retrieval returns whatever language the docs are in. LLM generates in query language.
- **GCP Discovery Engine:** defaults to corpus language (e.g. French for [client]) when user writes ASCII/English. Requires per-query preamble injection to override.

### Score Semantics

| Backend | Score field | Range | Meaning |
|---|---|---|---|
| Bedrock fast | `score` | 0–1 | Cosine similarity |
| Bedrock reranker | `score` | 0.05–0.35 typical | Reranker relevance |
| GCP Search | `relevance_score` | 0–1 | Internal relevance (not documented) |
| GCP `:answer` | `grounding_score` | 0–1 | Citation support confidence |

**Never compare scores across backends or modes** — they are calibrated on different scales.

### Session State
- **Bedrock:** stateless per-call — no session concept.
- **GCP `:answer`:** maintains a `Session` resource on GCP side. Persists GCP session name in Firestore so all replicas share session state without sticky routing.

### Answer Generation Ownership
- **Bedrock:** Bedrock retrieves passages; your LLM generates the answer. Full control.
- **GCP `:answer`:** GCP retrieves + generates internally. Get `answer_text` + grounding references back. Less control but simpler integration.
- **GCP Search (agentic mode):** GCP retrieves chunks; Gemini (via ADK) grades and synthesizes. Hybrid ownership.

---

## When to Consider Switching

**Bedrock → GCP Discovery Engine:** Only if entire infra moves to GCP. Bedrock's hybrid + reranker is genuinely strong; GCP's retrieval quality is comparable but the stack is opaque.

**GCP `:answer` → GCP agentic:** When you need CRAG-style correction loops or want to control answer synthesis. `:answer` is faster but you can't intercept or grade the retrieval step.

**Either → pgvector:** Only for local dev or if Postgres is already your stack. Loses hybrid search and managed reranking.

---

## Eval Comparison Axis

| Axis | System | Metric |
|---|---|---|
| Retrieval quality | Bedrock fast vs reranker | MRR, hit_rate, precision@5 |
| Retrieval quality | GCP Search vs pgvector | MRR, hit_rate |
| End-to-end quality | GCP `:answer` vs GCP agentic vs local agentic | GroundingGrader, AnswerQualityGrader |

Keep backends strictly separated in retrieval evals — never compare scores across modes.

---

## See Also
- [[Vector Database Comparison]]
- [[RAG Retrieval Strategies]]
- [[Bedrock KB vs LangGraph Decision]]
- [[Reciprocal Rank Fusion (RRF)]]
