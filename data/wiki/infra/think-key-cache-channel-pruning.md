---
title: ThinK Key Cache Channel Pruning
tags: [infra, concept]
summary: "ThinK prunes the channel dimension of the key cache, keeping the channels with the highest query-key score per head; pruning 40% of key channels cut total KV memory 20% with LongBench accuracy kept or raised on top of H2O or SnapKV (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xu-2024-think.md
---

# ThinK Key Cache Channel Pruning

Most KV-cache reduction works along the token axis (evict tokens) or the precision axis (quantize). ThinK (Xu et al., 2024, ICLR 2025) works along the channel axis of the key cache. For each head, each channel j gets a score, the Frobenius norm of the outer product of that channel in the queries and keys, computed over a recent observation window of queries (as in SnapKV). The top T = floor((1-λ)D) channels are kept and a binary mask is stored with the pruned keys. At decode, the query is masked the same way for the pruned keys, while recent and new keys use the full query, and the two products are concatenated.

The motivating observations: the attention matrix is low-rank (top 50 singular values hold over 90% of the energy in LLaMA-2-7B), and key channel magnitudes are uneven while value magnitudes are uniform. Plain l1 or l2 magnitude pruning held at 30% but lost accuracy at 40%.

## Results (self-reported)

- λ=0.4 removes 40% of key channels, a 20% cut in total KV memory. Setup: LongBench with the 8B and 70B LLaMA-3 Instruct models and Mistral-7B-Instruct v0.2, with KV budgets 128 to 2048, layered on H2O or SnapKV, A100.
- LLaMA-3-8B-Instruct at KV size 2048 with SnapKV: 41.91 with ThinK(0.4) against 41.86 for the full cache.
- With KIVI quantization on LLaMA-2-7B (prompt 160, output 338): 2.8x peak memory reduction, and a batch-size gain from 4x (KIVI alone) to 5x. Throughput rose from 5,168 to 5,518 tokens/s at batch 300, while time to first token went from 7.0 to 10.4 ms.
- Against SVD-based compression on LongBench: about 0.12% loss against 5.21% for ASVD (LLaMA-2-7B-Chat).
- Keeping the 32 most recent keys unpruned mattered (SnapKV+ThinK(0.4), Mistral: 40.76 with none, 42.27 with 32).

## Limits

- Time to first token rises, as the paper concedes, because channel scores are computed during prefill; value-cache pruning is left open (Mistral lost accuracy).
- λ of 0.5 or more hurt at small KV sizes; many LongBench differences are below one point and no variance or seed counts are given.
- Throughput numbers use short synthetic workloads, not long-context serving; evaluation is LongBench and Needle-in-a-Haystack on LLaMA and Mistral only.
- The 20% saving is half of λ because only keys are pruned; the kernel path was still being optimised and no paged-serving integration is reported.

## See Also
- [[KV Cache Reduction Methods]] — prerequisite-for (token, precision and channel axes of KV reduction)
- [[LLM Inference Economics]] — prerequisite-for (why decode memory matters)
- [[Prefix Caching]] — related (the other KV-cache lever)
- [[SparseGPT and Wanda Post-Training Pruning]] — related
- [[Multi-Query and Grouped-Query Attention]] — related
