---
title: GPU Kernel Tuning Workflow
tags: [infra, reference]
summary: "Checklist-style synthesis of one book's CUDA chapters: occupancy, memory access, warp efficiency, arithmetic intensity, pipelining, streams and graphs, plus AI-generated kernels; almost all numbers are the book's own illustrations or unsourced rules of thumb."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch06-gpu-architecture-cuda-programming-maximi.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch07-profiling-tuning-gpu-memory-access-patte.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch08-occupancy-tuning-warp-efficiency-instruc.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch09-increasing-cuda-kernel-efficiency-arithm.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch10-intra-kernel-pipelining-warp-specializat.md
  - data/raw/papers/2026-11-08-ai-systems-performance-engineering-ch11-inter-kernel-pipelining-synchronization-.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch12-dynamic-scheduling-cuda-graphs-device-in.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch20-ai-assisted-performance-optimizations-sc.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-appendix-ai-systems-performance-checklist-175.md
---

# GPU Kernel Tuning Workflow

The book's chapters 6 to 12 walk one loop: profile, decide whether a kernel is memory-bound or compute-bound, then apply the matching fix. Most chapters state that the numbers in its metrics tables are illustrative and that real benchmarks live in the book's code repository, so every number below is a rule of thumb or an illustration, not a measurement.

## The loop, by stage

1. Occupancy (ch6, ch8): start blocks at 256 threads; a Blackwell B200 SM holds at most 64 warps (2,048 threads). Chapter 8 recommends achieved occupancy of about 50-75% with diminishing returns past 60-70%, and says two to four independent operations per thread is the usual ILP sweet spot (claims). On the RTX PRO 6000 and the DGX Spark GB10 (capability 12.x), the limit is 48 warps.
2. Memory access (ch7): coalesce loads, use vector loads, tile through shared memory, pad tiles to avoid bank conflicts, mark read-only data. Illustrative before-and-after: a stride-2 copy falling from 4.8 to 1.3 ms; a float4 copy falling from 4.2 to 1.2 ms; 32x32 tiling from 15 to 170 GFLOPS; TMA double buffering from 18 ms to 7 ms.
3. Warp efficiency (ch8): replacing a divergent if/else with predication halves an illustrative threshold kernel from 30 ms to 15 ms; the chapter says that in the ideal case, eliminating a branch that splits threads evenly can almost double throughput, and warp-level fixes typically give 5-30%.
4. Arithmetic intensity (ch9): fuse kernels to cut memory traffic (an illustrative 4-kernel L2-normalize at 0.083 FLOPs/byte, fused near 0.25 and still memory-bound); use FP8, 2:4 sparsity and CUTLASS, which the chapter says matches hand-tuned kernels within about 2% (illustrative table). Inline PTX on an optimised kernel gave about 7% in a hypothetical example.
5. Intra-kernel pipelining (ch10): double buffering roughly halves illustrative GEMM time; warp specialisation adds 10.2%, clusters a further 6.5%, DSMEM pairs 40% (all illustrative). Megakernels are quoted as cutting latency 1.2x to 6.7x against per-layer launches (model, GPU and batch not stated).
6. Inter-kernel overlap (ch11): streams, stream-ordered allocation and programmatic dependent launch. The chapter has no benchmarks and judges that warp specialisation plus clusters is rarely worth the engineering effort when HBM is already saturated and streams hide the transfers (the authors' opinion).
7. Scheduling and graphs (ch12): atomic work queues, CUDA Graphs and device-initiated launches. Illustrative: capturing a 3-kernel pipeline cut iteration latency 25%; a warp-batched atomic queue halved runtime in an imbalanced microbenchmark (GPU model and repeats not stated).

## AI-assisted kernels (ch20)

The chapter quotes vendor results: a DeepSeek-R1 loop of generate, verify and refine yielded an attention kernel after 15 minutes on an H100; an RL-tuned 32B coder model rose from almost no working Triton kernels to about 40%, some up to 3x faster than baseline. Both are blog-sourced, and the extraction notes Predibase's environment rewarded correctness, not runtime, and that NVIDIA still needed some human oversight.

## Appendix rules of thumb (claims)

Mixed precision 1.5-3.5x, autotuned launch parameters 20-30%, INT8 inference 2-4x, FP8 about double FP16 on compute-bound kernels, 2:4 sparsity about 2x for pruned layers, and a data-pipeline fix lifting utilisation from about 70% to above 95%.

## Limits

- Table values are illustrative with no GPU model, clocks or run counts; the ch6 vector-add example gives utilisation from 1.5% to 95% with the same caveat.
- Internal inconsistencies noted by the extractions: ch7 31.8 sectors per request for a scalar copy against an optimum of 4; ch8 launch_bounds example (4 in prose, 8 in the listing) and the "Not Selected" stall described two ways, and the course note disputes the dual-issue claim; ch9 miscounts the fused kernels (4 against three); ch10 prose and code disagree on consumer_release, Table 10-3 labels SM utilisation as warp efficiency, and the megakernel caption says throughput where the text says latency; ch11 multi-GPU graph capture issues a collective on a second stream with no event fork; appendix gives torch.compile both 10-40% and 20-50%.
- Chapter 20 expands GRPO as "Group Relative Preference Optimization" (the extraction says the standard name is Policy).
- Blackwell-specific; dated to 2025.

## See Also
- [[FlashAttention and FlashAttention-2]] — related
- [[Torch Compile and Triton Stack]] — related
- [[LLM System Bottleneck Table]] — related
- [[LLM Inference Economics]] — prerequisite-for
