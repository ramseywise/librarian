---
title: "FollowIR Instruction-Following Retrieval Benchmark"
tags: [eval, reference]
summary: "FollowIR re-annotates three TREC collections with long instructions and measures with p-MRR whether retrievers change their ranking when an instruction changes; most embedders scored near or below zero (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-weller-2024-followir.md
---

# FollowIR Instruction-Following Retrieval Benchmark

FollowIR builds on Robust04, News21 and Core17. Instructions run 40 to 75 words against 12 to 17 for queries. Annotators altered instructions so that some documents change relevance, and the final query counts are 32 for News21, 20 for Core17 and 52 for Robust04. The paper's metric, p-MRR, compares a document's rank before and after the instruction changes: scores run from -100 to 100, and 0 marks no change in behaviour.

## Results (self-reported)

- Average p-MRR for embedders was at or below zero: BM25 at -2.1, E5-base-v2 at -3.9, Contriever at -3.8 and OpenAI v3 Large at -2.7. Two more were E5-mistral (-3.5) and TART-Contriever (-5.0).
- Models with positive p-MRR were Mistral-7B-instruct (+10.1), FollowIR-7B (+12.2) and MonoT5-3B (+2.5).
- FollowIR-7B was fine-tuned on 1,836 synthetic instances. It gained 6.0% relative on standard IR metrics and 20.8% relative on p-MRR (the standard-metric average went from 23.4 to 24.8).
- Giving the long instruction on the full Robust04 collection changed MAP by -7.0 (E5-base-v2), -7.7 (Contriever) and -10.1 (TART-Contriever).
- On InstructIR Robustness@10, FollowIR-7B scored 71.5 against 26.9 for BM25.

## Limits

- The extraction notes that the paper calls the InstructIR comparison a figure although it is a table.
- Query counts are small (20 to 52 per collection). The tuned model's gain is relative, from small absolute bases.

## See Also
- [[Reciprocal Rank Fusion (RRF)]] — related
- [[RAG Reranking]] — related
- [[RAG Evaluation]] — prerequisite-for
- [[AgentIR Reasoning-Aware Retrieval]] — related
