---
title: DeepSpeed Inference and ZeRO-Inference
tags: [infra, concept]
summary: "DeepSpeed Inference combines fused small-batch GPU kernels, tensor and pipeline parallelism for dense models, expert/data/tensor parallelism for mixture-of-experts models, and ZeRO-Inference, which streams weights from CPU memory or NVMe to run huge models on few GPUs."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-aminabadi-2022-deepspeed-inference.md
---

# DeepSpeed Inference and ZeRO-Inference

Aminabadi et al. target latency-critical, throughput-oriented and GPU-poor inference with three parts.

- **Single-GPU kernels.** Deep-Fusion tiles the computation along dimensions without cross-tile dependency, which lets operators (reductions, transposes, GeMMs) fuse whenever a tile in the later operator needs just one tile from the earlier one; SBI-GeMM is the small-batch matrix kernel.
- **Multi-GPU.** Dense models use tensor parallelism plus an inference-tuned pipeline schedule. MoE models use expert, data and tensor parallelism with PCC (parallelism-coordinated communication): all-to-all runs only among devices with the same tensor-slicing rank, followed by an allgather, and the paper states this brings the all-to-all cost down from O(p) to O(p/L), where L is the tensor-slicing degree and p the device count.
- **ZeRO-Inference.** Weights stay in DRAM or NVMe and each layer is streamed into GPU memory, which permits large batches; it adapts the offloading of ZeRO-Infinity.

## Results (all self-reported)

- MoE latency versus a PyTorch MoE baseline (not FasterTransformer): up to 7.3x lower on 256 A100 40GB GPUs for 100B to 2T models, per-token, prompt 128, batch 8. A 1T MoE (1064.9B) is served under 25 ms on 256 A100 40GB with 128 TB/s aggregate memory bandwidth. MoE kernel optimisations cut kernel-related latency by over 6x.
- Dense models 1.5B-175B at small batch, prompt 128 and 8 generated tokens, identical tensor-parallel strategy: speedup over FasterTransformer FP16, largest for the smallest models; headline up to 1.9x over the state of the art including INT8. FasterTransformer supports INT8 only for encoders, so its baseline stayed FP16.
- GPT-3 175B on 2x8 A100, prompt 512, 50 tokens generated, best batch size per configuration: higher throughput than the best FasterTransformer configuration, from a better pipeline schedule and larger batches. At 530B on 5 nodes (40 A100) it beats TP-only FasterTransformer; FasterTransformer with TP+PP crashed.
- Hybrid scheduling speeds prompt processing 1.18x (pipeline plus model parallel) and 3.06x (model parallel only) over FasterTransformer, GPT-3 175B, 2x8 A100, batch 24.
- ZeRO-Inference runs a 530B model on one A6000 48GB with 256GB DRAM and 2TB NVMe, 25x larger than the 20B that fits GPU-only; in offline inference at very large batch it hits 84 TFLOPS (54% of a 158.4 TFLOPS peak); for models that fit in CPU memory its throughput is more than 25x that of CPU-only inference.
- On A100 at batch 1 and sequence length 128 it is 1.7x faster than E.T. on DistilBERT and 1.4x on BERT.

## Limits

- No repeats, seeds or variance; speedups are "up to" maxima.
- The MoE baseline is an unoptimised PyTorch implementation; FasterTransformer could not run TP+PP at 530B.
- Hybrid scheduling was evaluated only at batch 24 because of a suspected PyTorch AllReduce issue.
- No accuracy evaluation, so the INT8 effect on quality is unreported; ZeRO-Inference targets throughput and is unsuited to latency-sensitive use.
- The hardware is 2022 (A100, A6000, V100), and the extraction notes that continuous batching and paged KV systems, absent from the paper, have since overtaken this stack. Absolute latencies appear only in figures.

## See Also

- [[LLM Inference Economics]] — related
- [[MoE Expert Offloading]] — alternative-to (another way to serve MoE models beyond GPU memory)
- [[ZeRO-Offload]] — related (the training-side offload that ZeRO-Inference adapts)
- [[Disaggregated Prefill-Decode Serving]] — related
