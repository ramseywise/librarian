---
title: Mixed-Precision Training and Loss Scaling
tags: [infra, concept]
summary: "Micikevicius et al. train in FP16 with an FP32 master copy of the weights, loss scaling and FP32 accumulation, matching FP32 accuracy on six task families with unchanged hyperparameters; fairseq and Switch Transformer reuse the recipe with dynamic loss scaling or an FP32 router."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-micikevicius-2017-mixed-precision-training.md
  - data/raw/papers/2026-11-08-ott-2019-fairseq.md
---

# Mixed-Precision Training and Loss Scaling

Micikevicius et al. ask whether networks can be trained in FP16, for both storage and arithmetic, while keeping accuracy and leaving hyperparameters untouched. Three techniques are used.

1. **FP32 master weights.** Weights, activations and gradients are stored in FP16 and updates go to an FP32 copy. The copy adds 50% to weight memory only; since activations dominate, overall memory roughly halves. Updating FP16 weights without the master copy lost 80% relative accuracy on Mandarin speech (DeepSpeech 2, about 800 hours, 20 epochs). About 5% of that model's weight-gradient values have exponents below -24, and an FP16 weight update becomes zero when the weight is at least 2048x the update.
2. **Loss scaling.** The loss is scaled before back-propagation so small gradients stay representable, and unscaled before the update. FP16 cannot hold magnitudes below 2^-24 and tops out at 65,504. SSD diverges in FP16 without it and a factor of 8 matches the FP32 mAP (76.9 baseline); bigLSTM needs 128. Factors used ranged from 8 to 32K, and many networks needed none.
3. **FP32 accumulation** of FP16 products.

ResNet50, AlexNet and Inception v3 on ILSVRC12, English and Mandarin DeepSpeech 2, translation LSTMs and bigLSTM all matched FP32 in the paper's runs (self-reported). Half-precision math is 2x to 8x single-precision throughput on recent GPUs, and DeepBench operations see 2 to 6x speedups on Volta.

## Reuse in fairseq and Switch

fairseq (Ott et al., 2019) trains with FP16 compute and FP32 updates, using dynamic loss scaling, with synchronous multi-GPU training that overlaps gradient sync and supports gradient accumulation. In the paper FP16 inference of the big Transformer on WMT'14 En-De decodes 54% faster than FP32 with no accuracy loss, and training En-De takes about 1.3 h on 128 V100s against about 12 h on 8. Its big Transformer scores 43.2 BLEU on En-Fr and 29.3 on En-De. Switch Transformers apply the idea selectively: casting only the router to float32 recovers float32 quality at near-bfloat16 speed (see [[Mixture-of-Experts Routing and Scaling]]).

## Limits

- Micikevicius et al. give no byte-per-parameter figure and no account of optimizer-state memory (Adam moments are absent). Speedups come from DeepBench operations only; whole-network speedups are future work.
- Mostly single runs, and translation shows large run-to-run variance among FP32 runs. GAN quality is qualitative. Speech models were trained in emulated mode on internal data. BF16 is not discussed, and dynamic loss scaling is proposed but not implemented in that paper.
- fairseq is a system-demo paper with no ablation of overlapped sync or gradient accumulation, and its sole speed comparison is FP16 against FP32 inference. Learning rates, batch sizes, optimizer and step counts are not given; single runs; a 2019 toolkit predating large decoder-only pretraining.

## See Also

- [[FP8-LM Mixed-Precision FP8 Training]] — extends
- [[Tensor, Pipeline and Data Parallelism for Large Transformers]] — related
- [[ZeRO Memory Partitioning]] — related (partitions the 12 bytes of fp32 optimizer state per parameter)
- [[Scaling Laws for Precision]] — related
