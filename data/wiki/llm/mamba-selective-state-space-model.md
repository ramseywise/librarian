---
title: Mamba Selective State Space Model
tags: [llm, architecture, concept]
summary: "Mamba makes the state space model parameters Delta, B and C functions of the input and computes the resulting recurrence with a fused hardware-aware scan, in an attention-free block; Gu and Dao report parity with Transformer++ from about 125M to 1.3B parameters."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-gu-2023-mamba.md
---

# Mamba Selective State Space Model

Gu and Dao ask whether one sequence model can grow linearly with length yet reach Transformer quality on dense data like language. Their hypothesis: letting the SSM parameters depend on the input (selection) lets the model choose what to keep and what to filter, which narrows the gap that time-invariant SSMs (LTI, with Delta, A, B and C constant across time-steps) show on discrete data.

## Mechanism

- **Selection:** Delta, B and C are functions of the input. S4 models with selection computed by a scan are called S6.
- **Discretisation:** A = exp(Delta A) and B = (Delta A)^-1 (exp(Delta A) - I) Delta B.
- **Hardware-aware scan:** the time-varying recurrence is computed as one fused parallel scan with the expanded state held in SRAM, plus recomputation.
- **Block:** one uniform gated block combines the H3 block with an MLP, so there is no attention and no separate MLP. Theorem 1 (Eq 5) gives a gated recurrence where the gate g_t is a sigmoid of a linear map of x_t and the new state mixes the previous state with the input, weighted by (1 - g_t) and g_t.

## Results (all self-reported)

- Language, trained on the Pile with the GPT-NeoX tokenizer, 300B tokens, context 2048: Mamba-2.8B averages higher than Pythia-2.8B and RWKV-3B in zero-shot accuracy over six tasks, and is on par with or above GPT-J-6B (63.0) and Pythia-6.9B (61.7). Pythia-2.8B has Pile validation perplexity 6.73.
- Scaling laws (Pile, Chinchilla token counts, context 2048 and 8192): Mamba matches Transformer++ from about 125M to 1.3B parameters, which the paper presents as the first attention-free model to do so.
- Throughput (A100 80GB, prompt 2048, 128 generated tokens, batch up to 128): higher than similar-size Hugging Face Transformers. The fused scan is faster than FlashAttention-2 beyond length 2K (A100 80GB PCIe, N=16, D=1024, BF16) and 20-40x faster than a PyTorch scan. Training memory is 38.2GB against 34.5GB for a FlashAttention-2 Transformer (125M models, batch 32, length 2048).
- Synthetics: on Selective Copying (length 4096, 2 layers) a Mamba block with S6 is near-perfect while S4 in the same block reaches 56.4. On induction heads, a model trained at length 256 generalises to length 1,048,576; no other method exceeds 2x its training length.
- Ablations (about 350M models, Pile, Chinchilla tokens): replacing the LTI SSM with S6 takes perplexity from 10.56 down to 8.69. Making only Delta selective gives 9.81, versus 10.93 with no selective parameter and 8.71 with all three. Raising the state size N (1 up to 16) while B and C are selective lowers perplexity 9.73 to 8.71, costing 1% more parameters; with B and C held constant, that sweep barely changes the result (9.88, then 9.81). A real-valued S4D-Real initialisation gets 8.71 against 9.16 for the complex S4D-Lin one.
- DNA (HG38, context 1024, 10B tokens): at about 40M parameters Mamba equals Transformer++ and HyenaDNA while using roughly 3x to 4x fewer. For 5-class great-ape classification at length 2^20, a 7M Mamba gets 81.31% against 54.87% for a 1.4M HyenaDNA (chance is 20%).
- Audio: on SC09 unconditional generation, a 6.1M Mamba gets FID 0.94 against 1.99 for SaShiMi, and a 24.3M model 0.67 against 1.42 for DiffWave+SaShiMi. On YouTubeMix (8 layers, 6M parameters), complex LTI S4 beats selective S6.

## Limits

- Evaluation stops below 7B parameters; the authors say larger sizes remain to be assessed.
- Audio waveforms and other continuous signals are a weak spot for selection; complex LTI S4 does better there.
- Quantization, RLHF, instruction tuning, in-context learning and fine-tuning are all outside what the paper studies.
- No seeds, error bars or training hardware and compute are reported.
- At the tested scales, a Mamba-MHA hybrid gives only a small gain over pure Mamba.

## See Also

- [[Structured State Space Sequence Model (S4)]] — prerequisite-for
- [[Mamba-2 and Structured State Space Duality]] — extends
- [[RWKV Linear-Time Recurrent Language Model]] — alternative-to
- [[Transformer Architecture]] — alternative-to
