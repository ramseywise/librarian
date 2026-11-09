---
title: "TURA Tool-Augmented Unified Retrieval Agent"
tags: [mcp, pattern]
summary: "TURA routes a query to MCP servers using an index enriched with synthetic queries, decomposes it into a DAG of tool calls and runs a distilled Qwen3-4B executor; on MCP-Bench Recall@5 rose from 0.4187 to 0.8289 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhao-2025-tura.md
---

# TURA Tool-Augmented Unified Retrieval Agent

TURA (2025 preprint) treats picking the right MCP server as a retrieval problem. Each server's index entry is augmented with about 20 synthetic queries. A query is decomposed into sub-intents, a DAG planner schedules independent tool calls in parallel, and a distilled Qwen3-4B model executes the calls. The paper reports it as deployed since May 2025 (the authors' own claim).

## Results (self-reported)

- MCP-Bench, 61 servers and 10,683 queries: Recall@5 0.4187 to 0.8289 and Precision@5 0.5505 to 0.9190. Without decomposition Recall@5 is 0.4530. A single-vector index scored 0.7721 against 0.8289 for multi-vector.
- DAG planner: latency 1,650 ms to 920 ms (-44.2%) with success 88.9% to 89.1%.
- End-to-end human rating: accuracy 87.5% against 65.3% for an LLM plus RAG baseline, faithfulness 96.2% against 72.4%.
- Distilled Qwen3-4B: tool-calling accuracy 70.1% to 88.3% at 750 ms P80.
- Online A/B over 103 queries: session success 55.1% to 64.0%.

## Limits

- Internal inconsistencies: the text says Table 1 shows latency but it has none; the A/B result is described as significant with no test given.
- Baseline configurations are the authors' own, and the Tool-Agent baseline lacks any MCP retrieval step. 95.02% of queries are single-intent, so the decomposition benefit applies to few.

## See Also
- [[MCP Protocol]] — prerequisite-for
- [[Tool Design as Context Engineering]] — related
- [[RAG Retrieval Strategies]] — related
- [[UniversalRAG Modality and Granularity Routing]] — related
