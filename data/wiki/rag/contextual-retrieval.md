---
title: Contextual Retrieval
tags: [rag, context, pattern]
summary: "Have an LLM write a short situating prefix for every chunk at index time and index prefix + chunk — it repairs the context chunking cut away for both BM25 and embeddings (reported top-20 failures −49%, −67% with a reranker), and prompt caching of the parent document makes indexing cheap."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--04-retrieval.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--06-memory.md
---

# Contextual Retrieval

Every chunking strategy cuts a fragment off from its context: "Revenue grew 3% in the
quarter" — which company, which year? **Contextual retrieval** (Anthropic) has an LLM
write a short prefix for each chunk **at index time** ("From the KPI section of the
company's 2025 Q2 financial report") and indexes prefix + chunk.

## Why One Step Helps Both Retrieval Paths

- **BM25** gains exact keywords that were never in the chunk (the company name, "2025 Q2").
- **The embedding** gains the missing situating context.

Reported results: top-20 retrieval failures fall **49%** with contextual embeddings +
contextual BM25, and **67%** once a reranker is added. ("Failure rate" here is 1 − hit
rate@20; check definitions before comparing — see [[Evaluating Context]].)

**Cost:** with [[Prefix Caching]], every chunk of one document shares the document as a
cached prefix, putting indexing at roughly  per million document tokens.

## Not the Same as Contextual Compression

| | Contextual retrieval | Contextual compression |
|---|---|---|
| When | Index time | Query time |
| Effect | **Adds** context to each chunk | **Removes** content irrelevant to the query |

See [[Context-Aware Compression]].

## Applied to Conversational Memory

The same prefixes fix multi-session user memory. Raw conversation chunks recording an
instruction set by one person, changed by another, then changed back look like three
contradictory instructions; with *who, when and intent* in each prefix, the latest valid
one is clear. This is the retrieved tier of the two-tier memory design in
[[Memory as Context]].

## Place in the Pipeline

Contextual retrieval improves the inputs to the standard hybrid stack — BM25 + dense,
fused with [[Reciprocal Rank Fusion (RRF)]], then cross-encoder reranking ([[RAG Reranking]]).
It is an ingestion-side fix, consistent with *ingestion sets the ceiling*
([[RAG Knowledge Preparation]]).

## See Also
- [[RAG Retrieval Strategies]] — extends
- [[RAG Knowledge Preparation]] — instance-of (an index-time enrichment step)
- [[Reciprocal Rank Fusion (RRF)]] — prerequisite-for
- [[Context-Aware Compression]] — alternative-to
- [[Index-Time Distillation]] — alternative-to
