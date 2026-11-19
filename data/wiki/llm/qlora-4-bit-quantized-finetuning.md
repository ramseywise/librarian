---
title: QLoRA 4-Bit Quantized Finetuning
tags: [llm, fine-tuning, concept]
summary: "QLoRA trains LoRA adapters through a frozen 4-bit NF4 base model, with double quantization of the constants and paged optimizers, bringing 65B finetuning under 48 GB (self-reported) while matching 16-bit LoRA on the tested setups."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-dettmers-2023-qlora.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch07-finetuning.md
  - data/raw/papers/2026-11-08-llm-engineers-handbook-ch05-supervised-fine-tuning.md
---

# QLoRA 4-Bit Quantized Finetuning

Dettmers et al. (2023) test whether the quality lost to 4-bit quantisation can be recovered by adapter finetuning. The pretrained model is quantised and held fixed, and gradients flow through its dequantised weights into LoRA adapters, placed on every linear layer and trained in BF16.

## Three ingredients

- **NF4 (4-bit NormalFloat).** A quantile quantisation data type for zero-centred normal data with an exact zero, described as information-theoretically optimal for normally distributed weights. Its 16 levels run from -1.0 to 1.0 (Appendix E of the paper lists them).
- **Double Quantization.** The quantisation constants are themselves quantised: blocksize 64 for weights, with the 32-bit constants quantised to FP8 at blocksize 256. The saving is roughly 0.373 bits for each parameter, which the paper works out as about 3 GB for a 65B model.
- **Paged optimizers.** Optimizer states sit in NVIDIA unified memory; when GPU memory is exhausted they are moved out to CPU RAM.

The forward pass is Y = X doubleDequant(c1, c2, W_NF4) + X L1 L2, with the LoRA product added in BF16. Huyen's finetuning chapter describes the same recipe: 4-bit NF4 weights, BF16 compute, paged optimizers.

## Reported results (self-reported)

- Memory: finetuning LLaMA 65B in 16 bits needs more than 780 GB; QLoRA needs under 48 GB.
- LLaMA 7B to 65B on Alpaca and FLAN v2: NF4 with double quantization matches BF16 LoRA on mean MMLU (53.1 against 53.0), while Float4 is about a point behind (52.2).
- Perplexity (Pile Common Crawl, OPT, BLOOM, LLaMA and Pythia, 125M to 13B) is lowest for NF4 with double quantization. RoBERTa-large on GLUE: QLoRA matches the 16-bit baseline (88.8).
- LoRA must sit on all linear layers to match 16-bit performance; rank does not matter (LLaMA 7B on Alpaca, r from 8 to 64, three seeds each).
- Guanaco, trained on OASST1: the 65B reaches 99.3% of ChatGPT's score on the Vicuna benchmark after 24 hours on one GPU, and the 33B reaches 97.8% at 21 GB (GPT-4 judge, 80 prompts, both orders, 95% CI 4.4%). With GPT-4 as judge, Guanaco 65B scores Elo 1022, versus GPT-4 at 1348 and ChatGPT at 966; human raters put Guanaco at 1023 and ChatGPT at 916.
- Data: on chatbot quality the small OASST1 set (9K samples) outperformed a 450K-sample FLAN v2 subsample, yet FLAN v2 was best on MMLU and worst on Vicuna, so the two measures track each other only partly. Training on the target alone beat source plus target for MMLU.
- In LLaMA 7B, 7.5% of hidden units fail the Shapiro-Wilk test of normality (5% significance), exceeding the expected false-positive rate by 2.5 points.

## Handbook figures (LLM Engineer's Handbook, ch. 5)

Iusztin and Labonne give QLoRA fine-tuning memory for a 7B model as 9.3 GB against 15.6 GB for LoRA (about 40% less), and initialisation memory as 9.1 GB against 14 GB (35%). They say training with QLoRA is about 30% slower than with LoRA, with small quality differences. The chapter names no source or setup for these figures and cites none. Their guidance is LoRA when memory allows and QLoRA when memory-bound. Their own SFT run used LoRA, not QLoRA.

## Limits

- At 33B and 65B the authors did not show that QLoRA equals 16-bit finetuning. They used just the MMLU, Vicuna and OA benchmarks, with no other bit widths or adapter methods.
- The authors call chatbot benchmarks untrustworthy: wide, overlapping confidence intervals, GPT-4 order effects and self-preference. GPT-4 and human majority agree only weakly at the example level (system-level Kendall tau 0.43; human-human kappa 0.42).
- Paged optimizers were measured once (65B on 48 GB, batch size 16, same speed). Responsible-AI evaluation was limited to CrowS. Warmup, weight decay, epochs and token counts go unreported; Guanaco is compared against baselines trained on proprietary data.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for (the LoRA family it belongs to)
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — alternative-to (another LoRA refinement; the DoRA page cites a third-party quantised variant)
- [[LLM.int8 Outlier-Aware Quantization]] — related (another quantisation scheme for large models)
- [[Scaling Laws for Precision]] — related
- [[LoRA Low-Rank Adaptation]] — prerequisite-for (the adapter method QLoRA builds on)
