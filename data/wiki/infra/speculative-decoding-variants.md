---
title: Speculative Decoding Variants
tags: [infra, concept]
summary: "Speculative decoding drafts several tokens cheaply and verifies them with the target model in one pass; the sources list draft-model, EAGLE, Medusa, self-speculative and consistency variants with speedups quoted from other work."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch15-multinode-inference-parallelism-decoding.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch09-inference-optimization.md
---

# Speculative Decoding Variants

Decode is memory-bandwidth-bound, so the GPU has spare compute while it generates one token at a time. Speculative decoding spends that spare compute: a cheap drafter proposes k tokens, and the target model checks them together. Huyen advises it when decode is bandwidth-bound and says it makes less sense when utilisation is already maxed out.

## Variants

- Two-model draft and target: Huyen's example is a 4B draft for Chinchilla-70B, 1.8 ms per token against 14.1 ms, with response latency cut by more than half and no quality loss (reported from the cited work; a similar gain for T5-XXL). The Fregly chapter says drafts should be about 4x faster than the target or more to pay off, and that the theoretical k-times speedup is about 2x in practice, with 1.5-2.5x common in vLLM, SGLang and TensorRT-LLM (reported, no workload).
- EAGLE family: EAGLE up to about 3.5x with a 4-token draft, EAGLE-2 20-40% faster than EAGLE, EAGLE-3 up to 6.5x over unoptimised baselines and as much as 1.4x beyond EAGLE-2 (all as quoted).
- Medusa heads: extra decoding heads on the target; 2.2-3.6x in published experiments and 2-3x in practice, with retraining required (reported). NVIDIA is quoted by Huyen as claiming up to 1.9x for Llama 3.1 on HGX H200.
- Self-speculative: the target drafts with half its layers, about 2x (reported).
- Consistency decoding: one model trained to generate and validate several tokens, about 3x without a drafter (reported; the source is not named).
- Inference with reference: draft tokens copied from the input, about 2x where context and output overlap heavily, such as retrieval, coding and multi-turn chat (reported).
- A PyTorch case study applied compilation, INT8, INT4 and then speculative decoding in sequence to Llama-7B on one A100; its gains appear only in a figure and the quality effect is unclear.

## Limits

- No experiment of the chapters' own: every speedup is quoted without a setup or with the cited paper's setup.
- Chapter 15 describes verification both token by token and as one batched pass, and gives the 3.5x figure to EAGLE-2 in its takeaways but to EAGLE in its body (the extraction's notes).
- "Non-optimized baseline variants" for EAGLE-3 is undefined, and the cited papers carry no references in the chapter text.
- The PyTorch case study gives no quality data.

## See Also
- [[Medusa Decoding Heads]] — instance-of
- [[LLM Inference Economics]] — prerequisite-for
- [[Goodput and Inference Metrics]] — related
- [[Multi-Head Latent Attention]] — related
- [[Speculative Decoding]] — related (concept page with the survey's speedups and drafter-free variants)
