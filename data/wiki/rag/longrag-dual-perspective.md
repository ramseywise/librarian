---
title: "LongRAG Dual-Perspective Extractor and Filter"
tags: [rag, pattern]
summary: "A different paper from the long-retrieval-units LongRAG: this one retrieves chunks, maps them back to source paragraphs, then runs an extractor and a chain-of-thought filter; on LongBench multi-hop sets GLM-4 averaged 52.56 F1 against 45.96 for vanilla RAG (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhao-2024-longrag.md
---

# LongRAG Dual-Perspective Extractor and Filter

This page covers the LongRAG of arXiv 2410.18050 (preprint). It shares a name with the long-retrieval-units paper but is a separate method. The pipeline retrieves 200-word chunks, maps them to their source paragraphs to give a longer context, then applies two components: an extractor that summarises global information from the long context, and a CoT-guided filter that marks which retrieved chunks are useful. The reader sees the long context, the global information and the filtered chunks. Evaluation uses LongBench HotpotQA, 2WikiMQA and MuSiQue (200 questions each), F1, top 7 chunks.

## Results (self-reported)

- With GLM-4, average F1 is 52.56; vanilla RAG gets 45.96.
- A ChatGLM3-6B model fine-tuned on 2,600 samples scored 47.93, against 46.79 for GPT-3.5-Turbo.
- Ablation on 2Wiki F1 (ChatGLM3-6B SFT): retrieved chunks alone (R&B) 46.61, chunks mapped to the long context (R&L) 44.83, extractor alone 52.53, filter alone 48.83, both 54.85.
- Feeding the long context to the reader uses about 5 times more tokens (10669 against 2181 on HotpotQA).

## Limits

- One-time retrieval only. Fine-tuning data is self-generated, which can bias the fine-tuned model.
- No latency or cost reported. Three sets of 200 questions; each question's corpus is assembled from its own paragraphs; no variance across runs.

## See Also
- [[LongRAG Long Retrieval Units]] — related (a different paper with a similar name)
- [[RAG Retrieval Strategies]] — related
- [[FILCO Sentence-Level Context Filtering]] — alternative-to
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
