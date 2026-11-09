---
title: Model Compression Landscape
tags: [infra, reference]
summary: "A survey-level map of language-model compression, pruning, quantization, distillation and low-rank methods, plus two measurement studies, post-training quantization across 1B to 405B Llama models and dropping layers from pre-trained encoders."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-park-2024-comprehensive-survey-compression-algorithms-language.md
  - data/raw/papers/2026-11-08-ding-2023-efficiency-spectrum-large-language-models.md
  - data/raw/papers/2026-11-08-lee-2024-exploring-trade-offs.md
  - data/raw/papers/2026-11-08-sajjad-2022-effect-dropping-layers-pre-trained.md
---

# Model Compression Landscape

Four sources, two surveys and two measurement studies. Numbers in surveys are quoted from cited papers under differing setups and are not comparable across rows.

## The two surveys

- **Park et al.** (compression algorithms for language models, coverage to early 2024) split methods into high-cost (retraining) and low-cost (calibration data, post-training). Quoted figures: structured pruning (ZipLM) up to 15x BERT-base speedup; Kprune prunes BERT in 10 minutes, where high-cost methods take as long as 40 hours; on OPT-175B, SparseGPT with 2:4 sparsity gives 50% compression and a 1.66x speedup while WikiText2 perplexity goes from 8.35 to 8.74, and GPTQ gives 81.3% compression and a 3.20x speedup with perplexity rising from 8.34 to 8.68; on LLaMA-7B at 70% sparsity Wanda has perplexity 85.77 where SparseGPT has 26.30; LLM-Pruner (structured) compressing LLaMA-7B by 20% lifts perplexity from 12.62 to 17.37 and speeds inference up by only 1.18x. They claim that loading memory rather than compute dominates LLM inference time, which is why recent LLM quantization targets weights only. Their stated practices include using low-cost methods for LLMs, 2:4 sparsity on A100 for speed, and pruning large granularities (sublayers) to gain GPU speed.
- **Ding et al.** (efficiency across scaling laws, data, architecture, training, tuning and inference, mostly before September 2023) quote Chinchilla 70B beating Gopher 280B at similar compute, up to 4 epochs of repeated data changing loss negligibly, GLaM activating 99B of over 1.2T parameters, and one-shot unstructured pruning to at least 50% sparsity at minimal loss but needing special software or hardware for speed. They say quantization is more mature than structured pruning for LLMs. The quantization section of that survey offers no bit widths or accuracy figures.

## Post-training quantization study (Lee et al.)

12 instruction-tuned models from 1B to 405B (Llama, Vicuna, Gemma), GPTQ, AWQ, SmoothQuant and FP8, 12 benchmarks plus MT-Bench with a GPT-4 judge (self-reported):

- For Llama-3.2-1B, 4-bit GPTQ costs 25.32 points on GSM8k and 16.01 on IFEval; its v1 average falls 10.14 (GPTQ) and 5.72 (AWQ).
- On Llama-3.1-70B, FP8 stays within 0.21 of FP16 on the v1 average and within 0.03 on v2; SmoothQuant W8A8 on 405B drops the v2 average by up to 10.86 against FP8.
- On the v1 average, a 4-bit 405B model (202.5 GB) outscores FP16 70B (140 GB): 78.76 for the latter, against 81.76 with GPTQ and 82.20 with AWQ.
- At 70B, 4-bit GPTQ is ahead of 8-bit by 1.89 on v2, while at 8B 8-bit wins over 4-bit. MT-Bench Reasoning rises after quantization for 9 of 12 models, which the authors attribute partly to GPT-4 judging; second-turn scores fall more.

## Layer dropping (Sajjad et al.)

Six strategies for dropping encoder layers from pre-trained BERT, RoBERTa, ALBERT, XLNet and DistilBERT, then fine-tuning on GLUE for three epochs (self-reported): removing the upper 6 of 12 layers reduces BERT and RoBERTa parameters by about 40% (BERT 110M to 66M), halves inference time and costs 0.89-2.91 points on average; top-layer dropping beats the other strategies and bottom dropping is worst. QQP on XLNet stays within 1% with 9 of 12 layers dropped. Pruned 6-layer models are competitive with distilled ones (RoBERTa-6 QQP 90.91 against DistilRoBERTa 89.40, baselines copied from other papers).

## Limits

- The surveys run no experiments of their own; their rows mix models, calibration sets and hardware, and Park et al. mix memory reduction with FLOPs reduction as "compression rate". Park et al. omit KV-cache compression, speculative decoding and FP8/FP4; Ding et al. omit serving and hardware.
- Lee et al.: single runs, no error bars; many deltas below 1 point; tools and calibration sets differ across rows, so method and tool effects are confounded; no latency, throughput or memory measurements, and the FP8 speed and KV-cache-halving remarks are asserted, not measured; the 405B FP16 and most GPTQ configurations were not run (over 30 days). Inconsistencies: the body text and Appendix C.1 name different MT-Bench categories as the biggest decliners, and the abstract cites 13 datasets where Appendix A lists 12 plus MT-Bench.
- Sajjad et al.: base-size models only, GLUE classification only, default hyperparameters, single runs apparently, small RTE and MRPC dev sets; the depth is static for all inputs; ALBERT keeps parameters shared so memory is not saved.

## See Also

- [[LLM.int8 Outlier-Aware Quantization]] — related
- [[SparseGPT and Wanda Post-Training Pruning]] — related
- [[Deep Compression Pipeline]] — related
- [[BitNet b1.58 Ternary Weights]] — related
- [[LLM Inference Economics]] — related
