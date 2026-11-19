---
title: Tensor, Pipeline and Data Parallelism for Large Transformers
tags: [infra, concept]
summary: "Large language models are trained by splitting work three ways: data parallelism across replicas, tensor (intra-layer) parallelism inside a layer, and pipeline parallelism across layers; GPipe, Megatron-LM, PTD-P and MT-NLG each add a piece, and Mesh-TensorFlow names the split by tensor dimension (all figures self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-abadi-2016-tensorflow.md
  - data/raw/papers/2026-11-08-shazeer-2018-mesh-tensorflow.md
  - data/raw/papers/2026-11-07-huang-2018-gpipe.md
  - data/raw/papers/2026-11-07-shoeybi-2019-megatron-lm.md
  - data/raw/papers/2026-11-08-narayanan-2021-efficient-large-scale-language-model.md
  - data/raw/papers/2026-11-07-smith-2022-using-deepspeed-megatron-train-megatron.md
---

# Tensor, Pipeline and Data Parallelism for Large Transformers

Each paper here answers how a model too large for one accelerator is split. All numbers are the authors' own (self-reported).

## Data parallelism in TensorFlow

Abadi et al. describe TensorFlow as one dataflow graph with mutable state, placed over CPUs, GPUs and TPUs, with parameter servers, sharded embeddings, checkpointing and replication built from graph primitives. For synchronous training they add backup workers: the update aggregates the first m of n worker updates. On Inception-v3 with 50 workers, 3 backup workers gave the best normalised speedup and 4 the shortest median step; throughput gains from backup workers reach 15%, and the median synchronous step runs about 10% longer than an asynchronous step with the same workers. At 200 workers synchronous training reaches 2,300 images/s, with returns tapering.

## Named tensor dimensions (Mesh-TensorFlow)

Shazeer et al. (2018) let tensors carry named dimensions and map them onto named mesh dimensions through a computation layout; the program compiles to SPMD with collectives. In the Transformer they split vocabulary, d_ff and heads along one mesh axis and the batch along the other. Their cost analysis of two fully connected layers has pure data parallelism all-reducing about 2 x d_io x d_h values per processor, pure model parallelism 2 x b x d_io, and the mixed layout 2 x b x d_io/r + 2 x d_io x d_h/c on an r x c mesh. They claim that at constant efficiency a 2-D mesh lets the processor count grow quadratically while batch and layer sizes only grow linearly. A 4.9B-parameter decoder on a 512-core TPUv2 mesh (16x32) reached 24.0 word perplexity on One Billion Word dev after 10 epochs (13 hours), and a 2.9B model got 43.9 BLEU on WMT14 En-Fr. Perplexity fell from 35.0 at 0.14B parameters, but the final doubling (2.48B to 4.90B) bought only 24.1 to 24.0.

## Pipeline parallelism (GPipe)

Huang et al. partition L layers into K cells on K accelerators and split each mini-batch into M micro-batches that are pipelined through the cells. Gradients accumulate and apply synchronously, and activations are re-computed at partition boundaries, so peak activation memory is O(N + L/K x N/M) instead of O(N x L). The idle bubble is O((K-1)/(M+K-1)) and is negligible when M >= 4K. A Transformer reached 83.9B parameters on 128 TPUv3 partitions (2048 model dim, 8192 FF, 32 heads, seq 1024, with re-materialisation). Transformer-48 at K=8, M=32 had 6.3x the throughput of K=2, M=1, while at M=1 K=8 gave only 1.3x. A single 6B, 128-layer multilingual Transformer beat individually trained 350M bilingual models on 100 language pairs.

## Tensor parallelism (Megatron-LM)

Shoeybi et al. split intra-layer: the first MLP matrix along its columns and the second along its rows, attention across heads, and the embedding across the vocabulary; each layer then needs two all-reduces going forward and two going backward. This needs a few changes to PyTorch code. An 8.3B GPT-2 on 512 V100s (8-way model x 64-way data parallel) sustained 15.1 PetaFLOPs; against a 1.2B single-GPU baseline at 39 TFLOPs, the body text puts weak scaling at 74% of linear. More attention heads lowered efficiency (82% at 16, 77% at 32 on 8-way). The 8.3B model got zero-shot WikiText103 test perplexity 10.81 against a previous 15.79, and LAMBADA accuracy 66.51%.

## Composing the three (PTD-P) and MT-NLG

Narayanan et al. combine pipeline parallelism across servers (1F1B schedule, optionally interleaved), tensor parallelism inside a server and data parallelism. A 1T-parameter GPT (128 layers, hidden size 25600, tensor degree 8, pipeline degree 64, batch 3072) hit 502 petaFLOP/s on 3072 A100s: 52% of peak, 163 teraFLOP/s per GPU. The interleaved schedule gave up to about 10% over earlier schedules at small batch (175B, 96 GPUs); scatter/gather raised throughput up to 11%, and fused operators took GPT-3 175B from 113 up to 135 teraFLOP/s per GPU. Doubling GPUs at fixed batch, PTD-P beat ZeRO-3 (no tensor or pipeline parallelism) by 70% for 175B and 530B models. The authors estimate 34 days to train GPT-3 175B on 1024 A100s and 84 days for the 1T model (estimates from throughput, 300B and 450B tokens).

Smith et al. train the 530B Megatron-Turing NLG (105 layers, 270B tokens) with 8-way tensor slicing, 35-way pipeline and data parallelism on Selene, which sustains between 113 and 126 TFLOP/s per A100 (batch 1920, 280 to 420 servers). They define 3D parallelism as that combination, with pipeline efficiency MB / (MB + PP - 1) for MB micro-batches.

## Limits

- TensorFlow: measures throughput and step time only, on a shared production cluster with no run counts; defers time-to-accuracy. Parameter-server and K40 era, with no tensor or pipeline parallelism, mixed precision or all-reduce; the static graph limits dynamic algorithms.
- Mesh-TensorFlow: the paper leaves out the optimizer, learning rate, precision, layer counts and tokenizer. Runs are single, layouts are chosen by hand, and implementations exist only for TPU SPMD and multi-CPU/GPU MIMD. On WMT14 En-De the largest model (26.7 BLEU) trails the 1.48B one (27.5).
- GPipe: assumes a single layer fits on one accelerator; load imbalance makes scaling sub-linear; batch norm needs special handling; deep NMT models needed scaled initialisation and logit clipping. NMT results are only in a figure, on an in-house corpus.
- Megatron-LM: the contributions list says up to 76% scaling efficiency while the body text says 74%. Tensor parallelism was tried only at up to 8-way inside one server, on 2019 V100 hardware; the 3.9B BERT had not finished training at the time of reporting; optimizer-state memory is left to future work.
- PTD-P: throughput only, with no convergence run and no optimizer or data stated; needs NVLink inside nodes and high-bandwidth InfiniBand; ZeRO-3 was compared without model parallelism, which the authors concede could improve it. Training times are estimates.
- MT-NLG: no ablation of data mix, filtering or learning rate; the paper does not give wall-clock, GPU-hours or total GPU count for the full run. Stability remarks (init std, beta2 0.99 to 0.95) are observations without runs shown.

## See Also

- [[Selective Activation Recomputation and Sequence Parallelism]] — extends
- [[ZeRO Memory Partitioning]] — alternative-to
- [[Mixed-Precision Training and Loss Scaling]] — related
- [[Mixture-of-Experts Routing and Scaling]] — related (GShard and Switch use the same sharding ideas)
- [[ZeRO-Offload]] — related
- [[FP8-LM Mixed-Precision FP8 Training]] — related (built on Megatron-LM)
- [[Partitioning Layouts for Transformer Inference]] — related
