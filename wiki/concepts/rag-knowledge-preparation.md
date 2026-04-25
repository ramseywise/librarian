---
title: RAG Knowledge Preparation
tags: [rag, infra, concept]
summary: The process of transforming human-readable documentation into machine-retrievable knowledge units — chunking, metadata tagging, rewriting for self-containment, and enforcing consistency.
updated: 2026-04-25
sources:
  - raw/notion/2026-04-07-support-knowledge-agent.md
  - raw/notion/2026-04-13-rag-pipeline-requirements.md
---

# RAG Knowledge Preparation

Existing documentation is typically written for human reading, not machine retrieval. Before content can serve as a reliable RAG knowledge source, it must be restructured.

This is an operational discipline distinct from chunking strategy (which is a retrieval engineering concern) — knowledge preparation happens before ingestion and involves editorial decisions about content quality and structure.

---

## Core Preparation Steps

### 1. Chunk Long Articles Into Smaller Knowledge Units

Long articles written for sequential reading contain multiple topics, introductory context, and caveats that become noise in retrieval. Split into topic-scoped units where each unit answers exactly one type of question.

Rule of thumb: if a chunk requires prior context to understand, it is not self-contained.

### 2. Remove Redundant and Outdated Content

Duplicate coverage of the same topic across multiple articles leads to conflicting retrieval results. Outdated articles create factual errors — the retriever doesn't know the content is stale.

### 3. Rewrite Sections for Self-Containment

Each knowledge unit should stand alone as an answer. A section like "As described above, the VAT rate is..." fails when retrieved without the article context. Rewrite to: "The VAT rate for [scenario] is..."

### 4. Attach Structured Metadata

Metadata is critical for retrieval accuracy. Without it, the system may retrieve technically correct information that is irrelevant to the user's context.

**Key metadata fields:**
- `product_area` — which product domain (invoices, expenses, banking, etc.)
- `feature` — specific feature or workflow
- `market` — which country/regulatory market applies (Denmark, Germany, France, etc.)
- `language` — content language
- `object_type` — the system object being described (invoice, expense, transaction, etc.)

Metadata enables **runtime filtering** — retrieval can narrow to market-relevant content rather than returning globally similar chunks.

---

## The Market and Language Filtering Problem

In multi-market financial software, accounting rules differ significantly across jurisdictions:
- Chart of accounts varies by country
- VAT rules differ
- Regulatory reporting obligations differ

A retrieval system that ignores market context may return content that is factually correct for one market but incorrect for another. **For financial software, incorrect regulatory guidance is the highest-risk failure mode.**

Every knowledge unit must include explicit market and language metadata. At query time, the retriever must include the user's market context as a filter — not as a ranking preference.

---

## Documentation Consistency

Multiple articles describing the same process differently create conflicting explanations. When retrieved together, these produce ambiguous or contradictory answers.

Preparation should include a consistency pass:
- Identify articles covering the same topic
- Reconcile conflicting claims
- Flag genuine regulatory ambiguity explicitly (don't silently merge)

---

## Support Conversations as Knowledge Source

Support conversations are a rich signal for identifying knowledge gaps — they represent real user questions that the current documentation fails to answer. However, they are NOT ideal direct retrieval sources:

- Frequently contain partial explanations
- Include edge cases not representative of typical behavior
- Contain corrections made mid-conversation (earlier turns may be wrong)
- Use informal language not matching documentation style

**Use support conversations for:** identifying documentation gaps, improving existing articles, building golden eval datasets. NOT as direct retrieval chunks.

---

## When to Do Knowledge Preparation

Knowledge preparation is a prerequisite before loading content into a vector store. Skipping it doesn't make RAG fail immediately — it makes RAG fail in subtle ways:

- Inconsistent retrieval quality across question types
- High hallucination rate on market-specific questions
- Conflicting answers when multiple articles cover the same topic
- Low recall on specific question types (chunk too broad, splits dilute signal)

---

## See Also
- [[RAG Retrieval Strategies]]
- [[RAG Evaluation]]
- [[Shine Knowledge Agent]]
- [[LangGraph CRAG Pipeline]]
- [[PII Masking Approaches]]
