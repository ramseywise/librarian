---
title: ZeRO-Offload
tags: [infra, concept]
summary: "ZeRO-Offload keeps fp16 parameters and the forward and backward pass on the GPU while gradients, optimizer states and the Adam update live on the CPU, which the paper reports lets one 32GB V100 train a 13B-parameter model."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-ren-2021-zero-offload.md
---

# ZeRO-Offload

Ren et al. model mixed-precision Adam training as a weighted dataflow graph and partition it between CPU and GPU. Model states cost 16 bytes per parameter (2 fp16 parameter, 2 fp16 gradient, and 4+4+4 fp32 parameter, momentum and variance). The paper argues the minimum CPU-GPU traffic for any model-state offload is 4M bytes per iteration for M parameters, and that the strategy with the largest GPU memory saving at that traffic keeps fp16 parameters and forward/backward on the GPU, with fp16 gradients, fp32 states and the optimizer step on the CPU. For several GPUs it combines this with ZeRO-2 partitioning or model parallelism. Two further pieces are an optional one-step delayed parameter update (DPU), which overlaps the CPU optimizer with GPU compute, and a CPU-Adam built on SIMD.

## Results (all self-reported)

- One 32GB V100 in a DGX-2 (GPT-2-like transformers, mixed-precision Adam): 13B parameters trainable, against 1.4B for PyTorch DDP.
- With model parallelism (degree 8) on 16 V100s: up to 70B parameters at over 30 TFLOPS per GPU.
- Against the layer-to-layer (L2L) baseline on one V100 (batch 512): 14% higher average throughput; L2L moves 28M bytes between GPU and CPU, seven times the 4M of ZeRO-Offload. L2L fits a larger model (17B) on a single GPU but fails to scale as GPUs are added.
- CPU-Adam is over 5x faster than PyTorch Adam at all sizes up to 10B, and the intro states over 6x.
- DPU, enabled after 40 iterations without hyperparameter changes, keeps BERT-large SQuAD F1 equal to the baseline.
- A 10B GPT-2 holds over 30 TFLOPS per GPU, and aggregate throughput scales almost linearly up to 128 GPUs (8 DGX-2 nodes). On one 16-GPU node with 1B-15B models, the throughput gains are at most 1.33x over PyTorch, 1.11x over ZeRO-2 and 1.64x over Megatron.

## Limits

- The derivation covers only mixed-precision Adam, and activations stay on the GPU, so checkpointing is relied on.
- ZeRO-2 is quicker at 64 and 128 GPUs, so offloading chiefly pays off where GPUs are scarce, and CPU compute may become the bottleneck with small batches.
- DPU alters training semantics, and its check covers just GPT-2 over 100K iterations plus BERT-large on SQuAD.
- The extraction notes an inconsistency: the single-GPU baseline is 1.2B in the introduction and 1.4B in Section 6.2.1.
- One hardware platform (V100 32GB, PCIe at 32 GBps), which is the cost driver; no seeds or variance; GPT-2 data and learning-rate details are not printed.

## See Also

- [[DeepSpeed Inference and ZeRO-Inference]] — extends
- [[MoE Expert Offloading]] — related
- [[LLM Inference Economics]] — related
