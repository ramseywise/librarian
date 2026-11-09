---
title: "TableRAG and HeteQA"
tags: [rag, pattern]
summary: "TableRAG indexes tables both in SQL and as Markdown text and iterates decompose, retrieve, SQL, answer up to five times; HeteQA is the 304-question benchmark built for questions that span tables and text (self-reported results)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yu-2025-tablerag.md
---

# TableRAG and HeteQA

TableRAG (2025 preprint) handles documents that mix prose and tables. Offline, tables are stored in a MySQL database and also written out as Markdown for the text index. Online it loops at most 5 times: decompose the question, retrieve, run SQL where needed, and answer. Retrieval is BGE-M3: top 30 recalled, top 3 kept, chunks of 1000 tokens with 200 overlap. HeteQA is the accompanying benchmark of 304 questions, of which 82% use a single source.

## Results (self-reported)

LLM-judge accuracy with a Qwen-2.5-72B judge. Columns are Claude-3.5, DeepSeek-V3 and Qwen:

- HybridQA: 47.87, 47.87 and 48.52. HeteQA overall: 44.19, 44.85 and 38.82. WikiTQ: 84.62, 80.40 and 78.00.
- NaiveRAG with Claude: 20.28 on HybridQA, 82.60 on WikiTQ and 34.54 on HeteQA.
- Latency with Qwen-72B on HeteQA: 24.57 s total for ReAct and 45.65 s for TableRAG.

## Limits

- Internal inconsistencies: the HeteQA table count is 136 in section 4.2 and 155 in appendix A.1; domains are 9 in the text and 8 in the legend; the text says latency is lower than the baseline but the table shows 45.65 s against 24.57 s; the Claude and DeepSeek HybridQA rows both read 47.87.
- Needs high-capacity LLMs and English only. No cost or recall metrics.

## See Also
- [[Text-to-SQL as a Retrieval Strategy]] — related
- [[RAG Retrieval Strategies]] — related
- [[UniversalRAG Modality and Granularity Routing]] — related
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
