---
title: SparseGPT and Wanda Post-Training Pruning
tags: [infra, comparison]
summary: "SparseGPT prunes GPT-scale models one-shot with a layer-wise Hessian-based solver, while Wanda scores weights by magnitude times input activation norm with no weight update; both reach about 50% sparsity with little loss and break down at high sparsity."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-frantar-2023-sparsegpt.md
  - data/raw/papers/2026-11-07-sun-2023-simple-effective-pruning-approach-large.md
---

# SparseGPT and Wanda Post-Training Pruning

Both papers prune pretrained language models without retraining, using a small calibration set.

**SparseGPT** (Frantar and Alistarh) solves layer-wise sparse regression approximately: columns are processed in order with shared inverse Hessians, remaining weights receive OBS-style updates, and masks are chosen per block of 128 columns. It also handles 2:4 and 4:8 patterns and joint sparsity with quantization. **Wanda** (Sun et al.) scores each weight by multiplying |W_ij| with the l2 norm of input feature j taken across calibration tokens, then zeroes the lowest scores within each output row, with no weight update. The authors motivate it by the emergent large-magnitude input features of LLMs.

## SparseGPT results (self-reported)

- OPT-175B, one shot, 128 C4 segments of 2048 tokens: 50% unstructured pruning reaches WikiText2 perplexity no worse than dense; 2:4 costs 0.39 and 4:8 costs 0.11 perplexity. Layerwise magnitude pruning at 50% collapses the model.
- OPT-175B and BLOOM-176B are pruned on a single A100 80GB in less than 4.5 hours. On BLOOM-176B magnitude pruning tolerates 30% sparsity, SparseGPT 50%.
- On OPT-175B, a 50% sparse 4-bit model outperforms 3-bit GPTQ of equal size; 50% plus 3-bit beats GPTQ at 2.5 bits.
- Layer-level 2:4 matmul speedups of 1.54-1.79x on OPT-175B (CUTLASS against cuBLAS, 2048 tokens); not end to end.

## Wanda results (self-reported)

- LLaMA-7B at 50% unstructured, 128 C4 calibration sequences: perplexity far below magnitude pruning (dense 5.68, SparseGPT 7.22); on LLaMA-2-70B it matches SparseGPT (dense 3.12, magnitude 4.98). The zero-shot accuracy gap to the dense model narrows with scale, and at 50% sparsity LLaMA-65B and LLaMA-2-70B equal dense.
- The pruning metric is computed hundreds of times faster than SparseGPT's (LLaMA-65B, A6000, excluding the shared forward pass).
- A per-output comparison group gives the best perplexity (7.26 against 7.95 per layer). Wanda stays robust with one calibration sample (7.46 against SparseGPT 10.22).
- 2:4 sparse LLaMA-7B end to end: 251 ms against 312 ms dense.
- LoRA fine-tuning (r = 8, one GPU, 12 hours) lifts 2:4 LLaMA-7B above the unstructured 50% model.

## Limits

- Wanda is worse than SparseGPT at 2:4 on LLaMA-7B, on OPT, and at 80% sparsity, where it collapses; both are far from dense at 70-80%.
- Why larger models prune more easily is speculation in the SparseGPT paper. Only OPT and BLOOM (SparseGPT) and mainly LLaMA families (Wanda) were studied; the evaluation covers perplexity plus a handful of zero-shot tasks, without any generation or reasoning test.
- Speedups are preliminary; zero-shot numbers are noisy by the authors' own account. Wanda's fine-tuning setup (learning rate, optimizer, batch size) goes unstated.

## See Also

- [[LLM.int8 Outlier-Aware Quantization]] — related
- [[Model Compression Landscape]] — related
- [[Deep Compression Pipeline]] — related
- [[ThinK Key Cache Channel Pruning]] — related
