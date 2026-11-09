---
title: MoE Expert Offloading
tags: [infra, concept]
summary: "Running Mixtral-8x7B on a 12-16 GB GPU by keeping an LRU cache of experts on the GPU, prefetching with the next layer's gate, and quantizing experts harder than attention; 2.1-3.1 tok/s with 2-bit experts at batch 1 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-eliseev-2023-fast-inference-mixture-experts-language.md
---

# MoE Expert Offloading

Eliseev and Mazur (arXiv 2312.17238, preprint, 2023) run Mixtral-8x7B on consumer hardware. The experts hold 96.6% of the model's parameters (45.1B of 46.7B), and only a few fire per token, so most of the model can wait in host memory.

## Mechanism

- **LRU expert cache.** Each layer keeps k experts on the GPU (k=2 on 12 GB cards, k=4 on 16 GB) with LRU eviction.
- **Speculative loading.** The next layer's gate is applied to the current layer's hidden states to guess which experts it will need, and one or two are prefetched while the current layer computes. This changes the load order, not the outputs.
- **Mixed quantization.** Because experts are almost all the parameters, they are quantized harder than the shared attention layers. The paper uses HQQ with 2- or 3-bit experts and 4-bit attention.

## Reported results

Setup: batch size 1, OpenAssistant conversations, with T4, RTX 3060, RTX 3080 Mobile and A100 hardware. The full algorithm reaches 2.092 to 3.061 tokens per second with 2-bit experts and 1.603 to 2.845 with 3-bit experts (self-reported). Naive offloading gives 0.661 tokens per second on a T4 with 2-bit experts.

Quality (Table 1, base model, MMLU 5-shot): FP16 70.51%, 4-bit attention with 2-bit experts 65.58%, and 3-bit experts 68.47% (self-reported).

## Limits

- One model family, batch size 1, plain LRU eviction; the text gives no cache hit rates, and there is no quality evaluation of the Instruct model.
- Internal inconsistencies noted by the extraction: the introduction says 2-3 tokens per second while Section 4.3 says 2-4; the extraction finds the naive 3-bit value of 1.791 on the RTX 3060 odd; and "RTX 3060 nearly equal to 3080 Mobile" is loose (2.278 against 2.655).

## See Also
- [[LLM Inference Economics]] — prerequisite-for (quantization and memory as serving levers)
- [[LLM in a Flash]] — alternative-to (paging dense feed-forward neurons instead of experts)
- [[MoE-LLaVA and MoE-Tuning]] — related (another sparse mixture-of-experts design)
- [[Scaling Laws for Precision]] — related (how far weights can be quantized)
- [[Straight-Through Estimator]] — related (gated conditional computation)
- [[DeepSpeed Inference and ZeRO-Inference]] — alternative-to (streams weights from CPU or NVMe)
- [[DeepSeekMoE Fine-Grained Expert Segmentation]] — related
