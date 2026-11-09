---
title: FlashAttention and FlashAttention-2
tags: [infra, concept]
summary: "FlashAttention computes exact attention block by block in on-chip memory with a running softmax, avoiding the full score matrix in HBM; FlashAttention-2 reworks work partitioning to approach matmul-level GPU utilisation."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-dao-2022-flashattention.md
  - data/raw/papers/2026-11-07-dao-2023-flashattention-2.md
---

# FlashAttention and FlashAttention-2

## FlashAttention (Dao et al. 2022)

The paper's premise is that on a GPU the time attention takes is set by data movement between HBM and on-chip SRAM rather than by arithmetic. A single fused CUDA kernel works through softmax(QK^T)V one block at a time inside SRAM, carrying a running maximum m and normaliser l per row so that partial softmaxes can be merged (m(x) = max of the two maxima, l rescaled by the exponentials of the differences). The full N x N score matrix is never stored in HBM. Backward recomputes S and P from the saved output and the (m, l) statistics rather than loading them. A block-sparse variant leaves out the blocks of a butterfly mask that are zero. By the paper's IO analysis, HBM accesses are Theta(N^2 d^2 M^-1) against Theta(Nd+N^2) for standard attention, and it also states a lower bound.

Results below are self-reported, each with its setup.

- On an A100, forward plus backward, with 16 heads of dimension 64, batch 64 and sequence 1024 (GPT-2 medium), attention time falls from 41.7 ms to 7.3 ms even though FLOPs rise and HBM traffic drops sharply.
- OpenWebText, 8xA100-40GB, 400K steps: GPT-2 small trains 3.5x quicker than the HuggingFace implementation at equal perplexity (18.2), and GPT-2 medium 3.0x quicker than HuggingFace and 1.8x quicker than Megatron (perplexity 14.3 against 14.2).
- BERT-large on 8xA100-80GB, 10 runs: reaches 72.0% masked-language-model accuracy faster than the MLPerf 1.1 record.
- Long Range Arena with a vanilla Transformer on 1K-4K sequences: 2.4x speedup over standard attention, average accuracy 59.8 against 59.3; the block-sparse variant gives 2.8x at 59.6.
- Longer context: a pretrained RoBERTa with repeated positional embeddings gains on MIMIC-III micro F1 as length grows from 512 to 16K and on ECtHR from 512 to 8K; Path-X (sequence 16K, pretrained on Path-64) is the first better-than-chance result for a Transformer per the paper, and block-sparse FlashAttention is above chance on Path-256 (sequence 64K).
- Memory: up to 20x more efficient than exact-attention baselines on one A100-40GB with dropout and padding mask on random inputs.

## FlashAttention-2 (Dao 2023)

The hypothesis is that the first version's inefficiency comes from work partitioning between thread blocks and warps. The kernel (built on CUTLASS 3.x) holds the output accumulator without rescaling it each step, keeps only the logsumexp L(j) = m(j) + log(l(j)), swaps the loop order so row blocks run in parallel across thread blocks (adding parallelism over sequence length), and splits Q rather than K and V across warps to avoid split-K shared-memory reductions. The paper reports that on A100 each non-matmul FLOP costs 16x a matmul FLOP, which motivates cutting non-matmul work.

- On an A100 80GB SXM4, forward pass without a causal mask at head dimension 128: up to 230 TFLOPs/s, 73% of the theoretical maximum (self-reported). Backward reaches up to 63% (self-reported).
- Attention benchmark on A100 across sequence lengths from 512 to 16k, head dimensions 64 and 128, with and without causal masking: about twice as fast as FlashAttention, spanning 1.7-3.0x (self-reported). FlashAttention v1 reaches 30-50% of peak forward and 25-35% backward on the same hardware.
- Training GPT-style 1.3B and 2.7B models at 2k or 8k context on 8 A100s: the best end-to-end speedup is 2.8x without FlashAttention as the reference and 1.3x against FlashAttention; the 2.7B model at 8k context sustains up to 225 TFLOPs/s on each A100, 72% model FLOPs utilisation (self-reported).
- H100 80GB SXM5, forward plus backward, head dim 128, no Hopper-specific instructions: up to 335 TFLOPs/s (self-reported).

## Limits

- FlashAttention needs a fresh hand-coded CUDA kernel for each attention variant and does not carry over between GPU architectures; speedup is smaller on T4 and at head dim 128; the IO optimality is up to constants on one GPU and the multi-GPU analysis is open.
- Beyond 1K sequence length, exact attention runs slower than some approximate methods (Linformer); at short lengths its backward pass trails Apex FMHA slightly; numerical equivalence is argued from matching GPT-2 validation curves, with no isolated error analysis; Block Sparse, Longformer and BigBird baselines were run without masking because of external bugs.
- FlashAttention-2 block sizes are tuned by hand per head dimension; results are single-run bars with no variance; training-speed numbers cover only 1.3B/2.7B GPT-style models and no model quality; the whole-model FLOPs formula leaves the attention term unhalved under causal masking, which inflates reported utilisation; no FP8, AMD or decode benchmark; the H100 run uses no TMA or fourth-generation Tensor Core instructions.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Multi-Query and Grouped-Query Attention]] — related (FlashAttention-2 supports them by index manipulation)
- [[Cut Cross-Entropy]] — extends (applies the same blockwise online-softmax idea to the loss layer)
- [[Star Attention]] — related (uses FlashAttention per host for local attention)
- [[GPU Kernel Tuning Workflow]] — related
- [[Torch Compile and Triton Stack]] — related
