---
title: Selective Activation Recomputation and Sequence Parallelism
tags: [infra, concept]
summary: "Korthikanti et al. cut activation memory about 5x in tensor-parallel Transformer training by splitting layer-norm and dropout activations along the sequence and recomputing only the attention core, which the paper reports lifts 530B-model utilisation from 42.1% to 54.2% against full recomputation."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-korthikanti-2022-reducing-activation-recomputation-large-transformer.md
---

# Selective Activation Recomputation and Sequence Parallelism

Full activation recomputation checkpoints at layer boundaries and recomputes the rest in the backward pass; in the authors' runs it costs 30 to 40% of execution time. Korthikanti et al. ask whether most of that cost can be avoided, and combine two techniques without extra communication.

## Mechanism

- **Sequence parallelism.** In tensor-parallel training the regions outside the tensor-parallel blocks (layer-norm, dropout) are replicated. Here those activations are partitioned along the sequence dimension, and the tensor-parallel all-reduce is replaced by a conjugate all-gather and reduce-scatter pair.
- **Selective recomputation.** Only the attention core is checkpointed and recomputed (the QK^T product, softmax, softmax dropout and the multiplication with V). The paper's criterion is parts that take considerable memory but are cheap to recompute.

Per-layer activation memory with tensor parallelism plus sequence parallelism is sbh/t x (34 + 5as/h), with t the tensor-parallel degree, 16-bit activations and 1-byte dropout masks. Worked examples: selective recomputation saves 70% of activation memory for a GPT-3 configuration (96 heads, sequence 2048, hidden 12288) at 2.7% FLOPs overhead and 65% for an MT-NLG configuration (128 heads, hidden 20480) at 1.6%.

## Reported results (self-reported, A100 GPUs, tensor parallel 8, s=2048)

- Activation memory falls about 5x against the tensor-parallel baseline, to under 20%, across 22B to 1T models.
- Against full recomputation, throughput rises by between 29.0% and 32.1% for 22B to 1T models (no data parallelism).
- The 530B model on 2240 A100s (with 8-way data parallelism added) reaches 54.2% MFU against 42.1% with full recomputation.
- The 1T model on 512 GPUs (tensor 8, pipeline 64) gets MFU 56.3% and HFU 57.0%, and an iteration takes 71.49 s against 94.42 s.
- Per-layer recomputation overhead falls over 90%: 2% for 530B and 1T against 36% for full recomputation. For one 22B layer it is 4% against 39%.
- Recomputing at the microbatch level adds just 0.7 (175B) and 0.4 (530B) points of MFU.

## Limits

- Most evaluations omit data parallelism, which keeps batches well under real training sizes; the authors say adding 8-way data parallelism costs little (MFU 56.0% to 54.2%).
- Setting this against ZeRO and offloading is declared out of scope. Fragmentation of memory and the memory load on the first pipeline stage are left open.
- Single measurements, no variance, no convergence or accuracy study; the memory formulas presume 16-bit storage, leave out small buffers, and the hardware is A100 only.

## See Also

- [[Tensor, Pipeline and Data Parallelism for Large Transformers]] — prerequisite-for
- [[ZeRO Memory Partitioning]] — related (complementary; not compared in the paper)
- [[FlashAttention and FlashAttention-2]] — related
