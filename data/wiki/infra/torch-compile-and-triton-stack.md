---
title: Torch Compile and Triton Stack
tags: [infra, concept]
summary: "How the book describes PyTorch profiling and the torch.compile stack (Dynamo, AOT Autograd, Inductor, Triton, XLA): one illustrative MoE speedup, graph-break and dynamic-shape advice, and internal inconsistencies about compile modes."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch13-profiling-tuning-scaling-pytorch.md
  - data/raw/papers/2026-11-08-ai-systems-performance-engineering-ch14-pytorch-compiler-openai-triton-xla-backe.md
---

# Torch Compile and Triton Stack

## Profiling first (ch13)

The chapter profiles one illustrative MoE training run (64 experts, bf16 autocast, batch size 4) with three tools. Linux perf at 2000 Hz found 45.0% of CPU samples in the Python forward function and 20.5% in aten::matmul, the DataLoader 10.2%, NCCL all-reduce 8.7%. The PyTorch profiler gave aten::matmul as the top CUDA op (43.00 ms over 128 calls). Nsight Systems projected 138.0 ms of GPU time for the train step. Fusing kernels to raise arithmetic intensity took the expert matmul from 50% to 85% of peak FLOPS, with memory bandwidth use falling from 70% to 40% of peak.

Compiling that MoE example brought one iteration down from roughly 248 ms in eager mode to roughly 173 ms, about 30% faster (GPU, model name and iteration counts not given). The chapter expects a dense model dominated by a single large GEMM to gain under 10% (claim). Other advice: raise the DDP bucket from 25 MB to 50 MB so all-reduce starts earlier (no measurement), and gate CI on a 5% regression sustained over 3 runs. SimpleFSDP is quoted as cutting memory up to about 28% and raising throughput up to about 69% against FSDP2 (reported, model and hardware not stated).

## The compiler stack (ch14)

The compiler stack names Dynamo, AOT Autograd, Inductor and Triton or other backends. PrimTorch defines about 250 primitive operations against more than 2,000 ATen operations, which means a new backend need cover only the primitives (claim). A toy function containing a print and a branch on tensor data produced 3 graphs and 2 graph breaks. In one Proton profile (8192x8192 matmuls, K=512) a Triton persistent kernel beat cuBLAS (165.349 ms for the Triton matmul kernel against 174.671 ms for torch; GPU and dtype not stated).

Shape advice (claims, no measurement): if sequence lengths vary only 10-20%, pad to a fixed length with static shapes; reduce-overhead mode uses CUDA Graphs and needs stable shapes, so dynamic shapes remove its gains.

## Limits

- One illustrative example and one profile excerpt carry all measured numbers; no variance or repeats. The perf stat counters look round and illustrative (the extraction's note).
- Internal inconsistencies noted by the extractions: ch13 credits max-autotune for the 173 ms result although its printed code uses reduce-overhead; its DDP bucket advice conflicts (bigger buckets launch earlier, one giant bucket loses overlap); the appendix gives torch.compile gains as both 10-40% and 20-50%.
- API names (set_stance, triton_op, warp_specialize) date from 2025 and change quickly; the extraction truncates code listings.

## See Also
- [[GPU Kernel Tuning Workflow]] — related
- [[LLM Inference Economics]] — prerequisite-for
- [[FlashAttention and FlashAttention-2]] — related
