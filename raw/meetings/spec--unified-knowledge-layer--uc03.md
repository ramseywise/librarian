---
source: notion
source_id: 36cf148b-3ab7-81bb-9bce-f558f63b8a21
source_url: https://app.notion.com/p/36cf148b3ab781bb9bcef558f63b8a21
type: product_spec
date: 2026-06-29
tags: [knowledge-layer, rag, vector-search, bedrock, opensearch, claude, ai-engineering, uc-03]
status: needs_discovery
priority: high
owner: AI Engineering
uc_id: UC-03
---

# Unified Knowledge Layer — UC-03

## Problem

Knowledge at Shine/sevdesk is fragmented across Confluence, Google Drive, internal back-office systems, market-specific wikis, and agent tribal knowledge. Agents handling second/third-level tickets must search across multiple sources. Problem gets worse during the product migration as agents must simultaneously handle legacy and new product knowledge.

## Solution

Build a **Unified Knowledge Layer** — a single natural language interface agents can query to get answers about products, processes, and guidelines across all markets.

## Core Architecture

1. **Ingestion**: Index content from Confluence, Google Drive, internal docs, and other sources
2. **Vector search**: Chunked + embedded documents in vector DB (OpenSearch on AWS — already used in RAPTOR)
3. **Retrieval**: Hybrid search (keyword + semantic) + cross-encoder reranking
4. **LLM response generation**: Claude Haiku (security-approved)
5. **Interface**: Chat-style UI (Intercom app panel, internal tool, or Slack bot)

### Localization
Same knowledge base, market-specific retrieval filters. German agents get DE-regulations context; French agents get FR-specific context.

## MVP Scope
- Focus: 1–2 products (Shine Banking FR or sevdesk DE)
- Content: product knowledge + key process documentation
- Success metric: reduction in time-to-answer for second-level tickets + agent satisfaction

## Technical Considerations

From RAPTOR learnings:
- Best chunking: Recursive (score 0.88)
- Best retrieval: Hybrid + Cross-encoder reranker (68% hit rate)
- Vector DB: OpenSearch on AWS
- LLM: Claude Haiku (security-approved)
- Evaluation: RAGAS + DeepEval

Long-term: foundation for UC-06 (Proactive Agent Copilot) and agent onboarding.

## Strategic Value

Rouven's (Head of Global CS Ops) #1 priority. Migration-safe and cross-market by design. Investment pays dividends across multiple future use cases.

## Open Questions

- Which knowledge sources for MVP? (Confluence, Google Drive, which back-office docs?)
- Auth mechanisms / access rights per source — who approves?
- Which market/product as MVP? (Shine Banking FR or sevdesk DE?)
- Interface: Intercom App Panel, Slack Bot, or internal tool?
