---
title: GPU Cluster Host, Network and Storage Tuning
tags: [infra, reference]
summary: "Synthesis of one book's chapters on NVL72 rack hardware, host OS and container tuning, NCCL and collective communication, and GPU storage I/O; the figures are vendor specifications, unsourced ranges or illustrations."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch02-ai-system-hardware-overview.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch03-os-docker-kubernetes-tuning-gpu-based.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch04-tuning-distributed-networking-communicat.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch05-gpu-based-storage-i-o-optimizations.md
---

# GPU Cluster Host, Network and Storage Tuning

The four chapters are training-centred; inference appears only in side remarks. None reports an experiment of its own at a stated hardware and software level, so read every figure as a vendor number, a rule of thumb or an illustration.

## Rack hardware (ch2)

Vendor figures for the GB200/GB300 NVL72 generation (2025): a rack of 72 GPUs and 36 Grace CPUs across 18 compute trays; per GPU, 18 NVLink 5 links give 1.8 TB/s bidirectional, and about 130 TB/s across the rack; B200 at 192 GB HBM3e (180 GB usable) and about 8 TB/s against H100's 80 GB and about 3.35 TB/s; 126 MB L2; NVLink-C2C up to about 900 GB/s between CPU and GPU; rack power up to about 130 kW and about 3,000 lbs, liquid cooled. For small messages, in-rack GPU latency is quoted at 1-2 microseconds against 5-10 microseconds or more across InfiniBand. Only the CPU-GPU path is cache coherent. An NVIDIA-reported 1.8T-parameter MoE comparison puts H100 at about 3.4 tokens/s per GPU against about 150 on NVL72, roughly 30x; the extraction notes it mixes precision, domain size and hardware.

## Host and container (ch3)

- NUMA: one experiment on a dual-socket system found about 80 ns local against about 139 ns remote memory access (CPU and method not named). Pinning to avoid cross-socket traffic may give 5-10% training throughput (claim).
- Pinned host memory copies 2-3x faster than pageable (claim); transparent hugepages about 3-5% (claim, with a note of latency pauses for inference); persistence mode avoids a one-to-two-second cold start (claim).
- A properly configured container differs under 2% from bare metal (claim). Keep ECC on; disabling gains only a few percent.
- MIG: up to seven instances per GPU; MPS lets two jobs each using 40% of a GPU reach 80-90% (illustrative). Topology-blind placement of a 4-GPU job can halve inter-GPU bandwidth (claim).

## Collectives (ch4)

- Examples, all toy-scale: a 400 MB two-rank all-reduce fell from 200 ms on Gloo (CPU) to 4 ms on NCCL over 800 Gb/s InfiniBand; DDP took 30 ms against 45 ms for DataParallel on a small MLP with two GPUs; rebuilding the process group each iteration cost 48 ms next to a 0.5 ms all-reduce.
- Overlapping gradient communication with compute gave about 30% iteration time in an illustrative table; a topology-aware overlap example went from 100 ms to 70 ms.
- Vendor claims: SHARP 2x to 5x all-reduce speedups at large scale, small at 2-4 nodes; KV offload to CPU improving TTFT up to 14x against recompute on PCIe x86 plus H100, with Grace Hopper at 2x faster than that; Dynamo with NIXL up to 30x throughput on a roughly 680B-parameter model on one rack (baseline not stated); NCCL symmetric memory up to about 7.6x lower latency for small and medium messages.
- Meta's Llama 3 405B pretraining attributed its largest block of unexpected interruptions to faulty GPUs: 148 of them, 30.1%, across 54 days (reported).

## Storage (ch5)

A gdsio run showed GPUDirect Storage reads with higher throughput and lower latency than the CPU path (no hardware or values stated, round numbers). VAST Data reported a gain on A100 and 30% or more on H100; DeepSeek's 3FS beat Ceph on a 68-node cluster (Ceph was about 1.1 TB/s on comparable hardware, reported). The chapter illustrates a 6x gain from cutting GPU data waiting from 30% to 5%.

## Limits

- Internal inconsistencies noted by the extractions: ch2 Grace bandwidth about 500 TB/s in one place and about 500 GB/s in another, GPU heat 1,200 W against 1,000 W, and NVLink latency 1-2 microseconds against single-digit microseconds; ch3 gives 45 GB total for two 2g.45gb slices in its MIG example, which disagrees with its Table 3-1, and MIG reset wording differs ("needs a reset" against "without rebooting").
- Hardware and software versions for the ch4 toy examples are not stated; defaults (DDP 25 MB bucket, NCCL variables, NIXL 0.5.x) are as of writing.
- Support lists and roadmap items (Rubin, Rubin Ultra, Feynman) are partly speculative and dated to 2025.

## See Also
- [[Disaggregated Prefill-Decode Serving]] — related
- [[GPU Kernel Tuning Workflow]] — related
- [[LLM System Bottleneck Table]] — related
- [[DeepSpeed Inference and ZeRO-Inference]] — related
