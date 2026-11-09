---
title: LLM.int8 Outlier-Aware Quantization
tags: [infra, concept]
summary: "LLM.int8() quantizes transformer matrix multiplications to 8 bits with per-vector scaling and routes the rare large-magnitude outlier feature dimensions through 16-bit, which the paper reports preserves quality up to 175B parameters."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-dettmers-2022-llm-int8.md
---

# LLM.int8 Outlier-Aware Quantization

Dettmers et al. ask why standard 8-bit quantization fails on large transformers and whether Int8 inference can lose nothing. They report that systematic large-magnitude feature dimensions (outliers) emerge abruptly in all layers between about 6B and 6.7B parameters and that these break standard quantization. LLM.int8() has two parts: vector-wise absmax quantization, with one scale per row of the input and per column of the weights, dequantized by their outer product; and mixed-precision decomposition, where any input dimension containing a value of at least 6.0 in magnitude is multiplied in FP16 and the rest in Int8 with Int32 accumulation. It is applied to pretrained models without training, to feed-forward and attention projection layers.

## Results (all self-reported)

- At 13B (fairseq, C4 validation) LLM.int8() matches 32-bit perplexity while plain absmax Int8 degrades sharply; zero-point vector-wise quantization without decomposition also degrades.
- BLOOM-176B memory falls 1.96x versus 16-bit.
- At 6.7B about 150k outliers appear per 2048-token sequence, concentrated in 6 feature dimensions. Zeroing at most 7 outlier dimensions increases perplexity by 600-1000%, whereas removing 7 random dimensions increases it by about 0.1%; the same removal also halves the mean top-1 attention softmax probability (about 40% before, about 20% after).
- Speed: the raw Int8 matmul reaches 2x only at large sizes; once quantization overhead is counted, LLM.int8() loses to FP16 for small models and gains 1.81x at the GPT-3 175B feed-forward dimension (12288). End-to-end BLOOM-176B Int8 on 8 A100 80GB at batch size 1 is slightly slower than bfloat16.
- Fine-tuning RoBERTa-large on GLUE with an Int8 feed-forward gives a mean of 88.81 against 88.61 at 32-bit. Int8 training of a 1.1B model with feed-forward and attention projections degrades (perplexity 10.52 against 9.99).

## Limits

- Only the Int8 type, not FP8; only models up to 175B; attention itself is not quantized.
- The aim is memory, not speed; overhead slows models below 6.7B.
- The perplexity comparison across baselines covers 125M-13B only; larger scales appear as OPT zero-shot accuracy. Training and fine-tuning are an initial analysis with hyperparameters not given.

## See Also

- [[BitNet b1.58 Ternary Weights]] — alternative-to
- [[FP8-LM Mixed-Precision FP8 Training]] — related
- [[SparseGPT and Wanda Post-Training Pruning]] — related
- [[Model Compression Landscape]] — related
- [[LLM Inference Economics]] — related
