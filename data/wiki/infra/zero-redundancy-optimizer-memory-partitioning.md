---
title: ZeRO Memory Partitioning
tags: [infra, concept]
summary: "ZeRO removes the replication of optimizer states, gradients and parameters across data-parallel ranks in three stages, with a memory formula of 16 bytes per parameter for mixed-precision Adam; the paper reports 170B-parameter training on 400 V100s, with only the first two stages implemented."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-rajbhandari-2020-zero.md
---

# ZeRO Memory Partitioning

Rajbhandari et al. ask how data-parallel training can shed redundant memory so that models with billions to trillions of parameters become trainable. Their answer is to partition, rather than replicate, the training state across data-parallel ranks, aiming for the memory efficiency of model parallelism with the compute and communication efficiency of data parallelism.

## Memory accounting

Under mixed-precision Adam each parameter costs 16 bytes: 2 for the fp16 weight, 2 for the fp16 gradient and 12 for the fp32 optimizer state (K=12). A 1.5B-parameter GPT-2 thus needs at least 24 GB of model state, while its fp16 weights alone take 3 GB. The paper splits memory into model states (optimizer states, gradients, parameters) and residual states (activations, temporary buffers, fragmented memory).

## ZeRO-DP stages and ZeRO-R

- Pos partitions optimizer states, cutting model-state memory 4x.
- Pos+g also partitions gradients, 8x.
- Pos+g+p also partitions parameters, reducing memory by the data-parallel degree Nd.

Analytic example, 7.5B parameters at Nd=64, per device: 120 GB with plain DP, then 31.4 GB, 16.6 GB and 1.88 GB for Pos, Pos+g and Pos+g+p. Communication volume equals plain DP (2 Psi) for Pos and Pos+g, and is 3 Psi, 1.5x, for Pos+g+p.

ZeRO-R handles residual states: partitioned activation checkpointing (analytic: checkpoints for a 100B model at batch 32, sequence 1024 and 16-way model parallelism shrink from roughly 33 GB to roughly 2 GB per GPU), constant-size buffers and memory defragmentation. ZeRO-100B is the implementation of Pos+g plus ZeRO-R.

## Reported results (all self-reported, V100 32GB, GPT-2-like models)

- 170B parameters on 400 GPUs with 16-way model parallelism, over 8x larger than Megatron-LM alone; a sustained 15 Petaflops for models of 8B to 100B, and above 38 TFlops per GPU on the 100B model.
- Up to 10x speedup over Megatron-LM, with the baseline given 256 to 384 GPUs against 400 for ZeRO.
- A 60B model scales super-linearly from 64 to 400 GPUs, because the batch per GPU grows as the data-parallel degree rises.
- With no model parallelism on 128 GPUs, 13B parameters train at over 40 TFlops per GPU; plain DDP stops above 1.4B parameters.
- The 17B Turing-NLG, trained with ZeRO-100B, got WikiText-103 perplexity 10.21 while running at 41.4 TFlops per GPU.
- A 40B Megatron-LM spread over two DGX-2 nodes manages roughly 5 TFlops per V100.

## Limits

- Only Pos+g and ZeRO-R were built; Pos+g+p and the trillion-parameter statements come from analysis, not measurement. A 1T model would still take over a year on then-current hardware (back-of-envelope claim).
- The baseline ran on fewer GPUs than ZeRO did, a difference the authors say works in the baseline's favour.
- For the throughput runs the paper states neither learning rate, optimizer settings, dataset, sequence length nor seeds, and each is one measurement. Large-batch convergence is not examined. The extraction notes the text says Webtext-103 for the WikiText-103 result.
- Figures are for V100 32GB with NVSwitch, which has dated.

## See Also

- [[ZeRO-Offload]] — extends
- [[DeepSpeed Inference and ZeRO-Inference]] — extends
- [[Tensor, Pipeline and Data Parallelism for Large Transformers]] — alternative-to (PTD-P beat ZeRO-3 by 70% in that paper's comparison)
- [[Selective Activation Recomputation and Sequence Parallelism]] — related (the paper calls it complementary and does not compare)
- [[Mixed-Precision Training and Loss Scaling]] — prerequisite-for
