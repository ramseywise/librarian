---
title: Lookahead Sparse Attention
tags: [infra, concept]
summary: "Lookahead Sparse Attention (FlashMemory-DeepSeek-V4) keeps only the compressed KV chunks a small Memory Indexer predicts will be needed over the next 64 decode steps on the GPU and mirrors the rest in CPU memory; GPU KV fell to 13.5% of full with average accuracy 77.5 against 76.9 on DeepSeek-V4-Flash (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-wang-2026-flashmemory-deepseek-v4.md
---

# Lookahead Sparse Attention

Wang et al. (Tencent and university labs, preprint 2026) add LSA to DeepSeek-V4-Flash. The model's CSA layers normally need every compressed KV chunk resident. A standalone Memory Indexer, a dual encoder trained on the query side only with frozen historical index keys, predicts which chunks the next tau decode steps need (tau = 64). Recalled chunks reach the GPU at step t+1 with no decode stall. A cold mirror of the full KV sits in host pinned memory, so the GPU footprint scales with the retained set, not the context.

Labels come from the frozen backbone by cross-layer majority voting (an entry counts if at least 3 of 21 CSA layers select it). The chosen indexer ensembles three layers (10, 12 and 20) with an OR-union at threshold 0.5; an eight-layer version pulled in 30% to 49% of the history. Training took about one H20 GPU hour, using roughly 10,000 documents between 16K and 512K tokens long.

## Results (self-reported)

- Averaged over LongBench-v2, LongMemEval and RULER rows: 77.5 against 76.9 for the full-KV baseline, with GPU KV 0.10 GB against 0.93 GB (13.5%). Recency Only scored 33.3 and Random 10% 38.7. RULER at 128K and 256K was lower than baseline (93.2 against 94.3, 88.2 against 90.5).
- At 1M context on an 8xH20 server (sglang logs): GPU KV 3.73 to 0.37 GB and decode compute 118.9 to 35.4 GFLOP per token (0.30x).
- The abstract further claims 2.8 times the aggregate throughput and 2.7 times the concurrency under disaggregated serving on 8xH20.

## Limits

- The 2.8x and 2.7x serving claims have no body table, batch size, baseline configuration or latency numbers.
- Tables give single numbers without variance, and the 0.6-point average gain is smaller than several of the per-row differences.
- Table 1 counts GPU-resident KV only. The CPU holds the full mirror and recall traffic cost is not quantified, so total memory is not reduced.
- The 1M-context efficiency figures sit past the 512K training range; the paper says the indexer generalises only to about 2x its training length, reports no 1M accuracy, and calls above that untested.
- Failures reported: MRCR fell from 76.0% to 48.0%; on context-independent queries the retained volume grew about 2.5x from 125K to 500K.
- tau = 64 and the 0.5 threshold were never ablated; the project is suspended; the method applies only to DeepSeek-V4-Flash. The "attention denoiser" reading is the authors' interpretation, not tested.
- The over-90% figure (requests over 64K resolved from the last 8K tokens) cites unnamed real-world logs.

## See Also
- [[KV Cache Reduction Methods]] — prerequisite-for (the family LSA belongs to)
- [[MiniMax Sparse Attention]] — alternative-to
- [[LLM Inference Economics]] — prerequisite-for (memory-bound long-context serving)
