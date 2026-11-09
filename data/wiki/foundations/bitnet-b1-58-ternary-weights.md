---
title: BitNet b1.58 Ternary Weights
tags: [foundations, concept]
summary: "BitNet b1.58 trains a language model natively with weights restricted to -1, 0 and 1; the 2B model trained on 4T tokens averages 54.19 against 55.23 for Qwen2.5-1.5B on 16 benchmarks with 0.4 GB non-embedding memory (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ma-2025-bitnet-b1-58-2b4t-technical.md
---

# BitNet b1.58 Ternary Weights

Ma et al. (Microsoft, arXiv 2504.12285, technical report, 2025) release a 2B-parameter model trained from scratch on 4T tokens with ternary weights, as opposed to quantizing a full-precision model afterwards.

## Mechanism

- Linear layers are replaced with BitLinear. Weights are quantized to -1, 0 or 1 by absmean scaling, and activations to int8 per token.
- Other changes: subln normalisation, squared ReLU in the feed-forward layer, and no bias terms.
- The model runs on CPU through the authors' bitnet.cpp.

## Reported results

- **16 benchmarks, against instruction-tuned peers (Table 1):** average 54.19 against 55.23 for Qwen2.5-1.5B (self-reported). Non-embedding memory is 0.4 GB, and decoding on a laptop CPU takes 29 ms per token on bitnet.cpp against llama.cpp baselines (both self-reported). The 0.028 J energy figure is the authors' analytical estimate that counts arithmetic only (self-reported).
- **Against post-training quantization (Table 2, three benchmarks):** BitNet average 55.01 against 55.72 for bf16, 52.15 for GPTQ-int4 and 51.17 for AWQ-int4 (self-reported).
- Table 3 reports an average of 60.68 over 11 benchmarks, which is a different benchmark set and not comparable with Table 1.

## Limits

- No GPU numbers; behaviour at larger scale is unknown; English only; no reinforcement-learning stage.
- The "on par" claim trails on MMLU and several other benchmarks.

## See Also
- [[Scaling Laws for Precision]] — related (loss as a function of weight precision during training)
- [[LLM in a Flash]] — alternative-to (fitting a model into limited memory by paging)
- [[LLM Inference Economics]] — prerequisite-for (the quantization lever)
- [[Weight Initialisation and Activation Scale]] — related
- [[Straight-Through Estimator]] — related
- [[Bi-Mamba Binarized State Space Model]] — extends (1-bit weights in a state space model)
- [[LLM.int8 Outlier-Aware Quantization]] — alternative-to
- [[Model Compression Landscape]] — related
