---
title: Contextual Retrieval
tags: [rag, context, pattern]
summary: "Have an LLM write a short situating prefix for every chunk at index time and index prefix + chunk — it repairs the context chunking cut away for both BM25 and embeddings (reported top-20 failures −49%, −67% with a reranker), and prompt caching of the parent document makes indexing cheap."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-huyen-ai-engineering-ch06-rag-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--04-retrieval.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--06-memory.md
  - data/raw/papers/2026-11-08-lakshmanan-hapke-genai-design-patterns-ch03-adding-knowledge-bass.md
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

## Second-hand account in a design-patterns book

Lakshmanan and Hapke (ch. 3) describe having an LLM write a short situating note for every chunk, prepended before both embedding and BM25 indexing, with the full document cached in the prompt to keep the cost down. They quote a 67% reduction in incorrect retrievals, attributed to Anthropic (self-reported: a vendor's claim about its own technique, not the book authors' experiment); and baseline and metric are not defined in the chapter.

Limits of this section:
- The 67% figure is quoted without a reference in the chapter.

## Figures quoted in a second book

An AI-engineering text describes the technique as prepending a context of 50 to 100 tokens to each chunk, and repeats Anthropic's guidance that a corpus below 200,000 tokens, roughly 500 pages, can simply sit in the prompt with no retrieval. It adds an arithmetic illustration: at 95% accuracy per step, a 10-step agent is right about 60% of the time and a 100-step one about 0.6%.

## See Also
- [[RAG Retrieval Strategies]] — extends
- [[RAG Knowledge Preparation]] — instance-of (an index-time enrichment step)
- [[Reciprocal Rank Fusion (RRF)]] — prerequisite-for
- [[Context-Aware Compression]] — alternative-to
- [[Index-Time Distillation]] — alternative-to
- [[BM25 and the Lexical Gap]] — prerequisite-for
- [[LongRAG Long Retrieval Units]] — alternative-to (enlarges the retrieval unit instead of adding context to small chunks)
- [[HtmlRAG HTML as Retrieval Format]] — related (keeps document structure in retrieved text)
