---
title: FP8-LM Mixed-Precision FP8 Training
tags: [foundations, concept]
summary: "FP8-LM extends FP8 beyond matrix multiplies to gradients, optimizer states and distributed communication in three add-on levels; the paper reports GPT-175B training 75% faster than BF16 Megatron-LM with 39% less memory and matching loss curves."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-peng-2023-fp8-lm.md
---

# FP8-LM Mixed-Precision FP8 Training

Peng et al. ask whether most training variables can use 8-bit floating point, not just GEMM compute, without hyperparameter changes. Their framework (MS-AMP) adds three levels: gradients in FP8 with all-reduce, using automatic scaling and one shared minimum scaling factor; an Adam optimizer that stores the first moment in FP8, the second in FP16, and keeps FP16 master weights under tensor scaling; and FP8 tensor and sequence parallelism with a greedy whole-tensor ZeRO distribution. In the paper's worked example the optimizer setup costs 6 bytes per parameter where FP32 Adam mixed precision costs 16, a 2.6x saving.

## Results (all self-reported)

- GPT-175B on H100 80GB (TP8, PP4, DP4, 40B tokens), Megatron-LM based: 75% faster than BF16, 39% less per-GPU memory at the same batch size; 37% lower training time and 42% less memory than Transformer Engine. The speed row uses micro batch 4 for FP8, against 1 for BF16.
- Weight-related communication falls 63-65% against BF16, and activation communication in sequence and tensor parallelism 34%.
- FP8 and BF16 loss curves almost overlap for 7B, 13B (100B tokens) and 175B (40B tokens) at identical hyperparameters. Zero-shot nine-task averages: GPT-7B 58.0 FP8 against 58.4 BF16; GPT-13B 60.4 against 61.0.
- FP8 supervised fine-tuning of LLaMA-7B (ShareGPT): 14% less memory, 27% higher throughput, AlpacaEval 67.20 against 66.15, MT-Bench 5.70 against 5.75. FP8 RLHF (AlpacaFarm PPO): 32% less weight memory and 62% less optimizer-state memory, AlpacaEval 72.42 against 72.05.
- Ablations on GPT-125M, 100B tokens: an FP8 second moment makes training diverge, an FP8 master weight degrades accuracy, while an FP8 first moment with FP16 scaled master weights matches the baseline.
- With 32 H100s FP8 trains 175B-parameter models at 4,096 context, where Transformer Engine fits 2,048. Model FLOPs utilisation at 175B is 34.2% for FP8 against 39.0% BF16 and 24.9% Transformer Engine.

## Limits

- The 175B model is trained for only 40B tokens; no downstream accuracy at 175B, and SFT and RLHF only at 7B scale. Single runs, no variance; differences such as 58.0 against 58.4 are single-run.
- At equal micro batch 1 the 175B speed gain is +21%, not 75%.
- Needs Hopper hardware; weights and data mix are not released. As a training method it does not address FP8 inference or post-training quantization.

## See Also

- [[LLM.int8 Outlier-Aware Quantization]] — related
- [[Scaling Laws for Precision]] — related
- [[Model Compression Landscape]] — related
- [[ZeRO-Offload]] — related
