---
title: Bi-Mamba Binarized State Space Model
tags: [foundations, concept]
summary: "Bi-Mamba binarizes the input and output projections of Mamba-2 to 1-bit weights with learnable scale and shift, trained from scratch with distillation from a LLaMA2-7B teacher, and keeps most of full-precision accuracy where post-training binarization collapses."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-tang-2024-bi-mamba.md
---

# Bi-Mamba Binarized State Space Model

Tang et al. swap the linears for the input and output projections in Mamba-2 (780M, 1.3B, 2.7B) for FBI-Linear, whose weights are signs in {1, -1} with a column-wise scale alpha and a shift beta that are both learned. Training relies on a straight-through estimator and a cross-entropy distillation loss, with LLaMA2-7B as teacher over 105B Amber tokens. Conv1d, A, D, norm, delta_bias, the embedding and the head are kept at 16 bits. The linear modules hold 95.2% of Mamba-2-2.7B's parameters.

## Results (all self-reported)

- Zero-shot average over 7 tasks at 2.7B: Bi-Mamba 50.6, FP16 Mamba-2 59.6, GPTQ 2-bit 35.8. At 780M: 45.3 against 52.5 FP16, 42.6 GPTQ 3-bit and 38.1 BiLLM; at 1.3B: 48.4 against 55.8 FP16 and 46.3 FBI-LLM. Accuracy runs use weights simulated in high precision.
- Perplexity at 2.7B: Wikitext2 10.0 against 9.1 FP16 and 8707.0 for BiLLM; C4 11.3 against 13.3 FP16.
- Post-training baselines applied by the authors collapse on Mamba-2 (BiLLM 2.7B Wikitext2 8707.0, GPTQ 2-bit 2.1e+5).
- llama.cpp on a Mac M4 Pro CPU, 8 threads, 2.7B: 1.04 GB against 5.03 GB memory, 77.81 against 24.59 tokens/s (3.16x), and 44.9 J against 148.4 J per 128 generated tokens. Theoretical storage of the fully binarized model is 0.55 GB, 89.0% compression, computed rather than measured.
- Ablations at 780M: removing distillation gives 42.7 average against 45.3; a KL loss gives 43.3; a Phi-3.5 teacher 43.4. Binarizing only the input projection gives 53.1 at 2.7B against 50.6 for both.
- Training took 5780 and 7822 A100 GPU hours for the 1.3B and 2.7B models against 2360 for Mamba-2-370M.

## Limits

- Real 1-bit packing is evaluated only on CPU through llama.cpp; accuracy numbers use simulated weights; hardware support is needed for full gains.
- The 1-bit models trail FP16 Mamba-2 by about 7-9 points; HumanEval and GSM8K are near zero for all base models, so those rows are uninformative.
- Only Mamba-2 was tested; the BitNet comparison is not size-matched. The extraction notes that no seeds or context length are stated, and that the text says training runs "until convergence" while the appendix says otherwise.

## See Also

- [[BitNet b1.58 Ternary Weights]] — alternative-to
- [[Straight-Through Estimator]] — prerequisite-for
- [[Model Compression Landscape]] — related
- [[RWKV Linear-Time Recurrent Language Model]] — related (another attention-free architecture)
