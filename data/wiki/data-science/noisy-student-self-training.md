---
title: "Noisy Student Self-Training"
tags: [data-science, deep-learning, pattern]
summary: "Noisy Student trains a teacher on labeled images, pseudo-labels unlabeled images, then trains an equal-or-larger student on both with noise added, and iterates; the paper reports 88.4% ImageNet top-1 and large robustness gains."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-xie-2020-self-training-noisy-student-improves.md
---

# Noisy Student Self-Training

The authors ask whether self-training with a noised student on large unlabeled image data can beat supervised and weakly-supervised ImageNet results. They hypothesise that a student can pass its teacher if it is noised and is no smaller than the teacher.

## Method

First an EfficientNet teacher is fitted to labeled ImageNet. It then labels a filtered and balanced set of unlabeled JFT images, without noise applied to it. An EfficientNet student of the same size or bigger learns from the labeled and pseudo-labeled images together, with noise on the input (RandAugment) and in the model (dropout, stochastic depth). The student then becomes the teacher and the loop repeats. The paper's term for this is Noisy Student Training.

## Results (self-reported)

- Setup: EfficientNet-L2 student, 3 iterations, 300M unlabeled JFT images of which 130M remain after filtering and balancing. Result: 88.4% top-1 on ImageNet 2012 val, against 86.4% for FixRes ResNeXt-101 WSL, which used 3.5B Instagram images.
- The gain over EfficientNet-B7 at 85.0% splits into +0.5% from the larger model and +2.9% from Noisy Student.
- Each EfficientNet size B0 to B7 gains about 0.8% with a same-size teacher and no iteration.
- Without noise on the unlabeled data, B5 drops to 84.3% from 85.1%, near its 84.0% supervised baseline (130M unlabeled images, no iteration).
- Across L2 iterations the scores were 87.6%, 88.1% and 88.4%, the last with a 28:1 unlabeled-to-labeled ratio.
- Joint training beat pretrain-then-fine-tune on B0 (77.9% against 77.5%, B0 to B3, 350 epochs).
- With public YFCC100M in place of JFT, B7 reached 86.2% against 86.4% on JFT (no iteration).
- Robustness for EfficientNet-L2: ImageNet-A top-1 reaches 83.7%, up from 49.6% for supervised L2 and 61.0% for the prior best; ImageNet-C mCE 28.3 against 45.7 for the prior best at 299x299; ImageNet-P mFR 12.2 against 27.8 at 299x299. Under a 10-step PGD attack at epsilon 16 (800x800 input) accuracy rose from 1.1% to 4.4%.
- B4 trained with that 88.4% L2 as teacher reached 85.3% (standard augmentation, 700 epochs).

## Limits

- The unlabeled JFT data is Google-internal; public YFCC100M gave slightly lower results.
- Each result is a single run, without seeds or error bars, and the optimizer and precision go unstated.
- L2 training used a 2048-core TPU v3 Pod for 6 days.
- The authors note RandAugment overlaps slightly with the ImageNet-C and ImageNet-P corruptions (brightness, contrast, sharpness).
- The adversarial results are not comparable with earlier work because of the 800x800 input.
- The choice between hard and soft pseudo-labels depends on the case.

## See Also
- [[SimCLRv2 Pretrain, Fine-Tune, Distill]] — related
- [[Big Transfer (BiT) Generalist Pretraining]] — alternative-to (concurrent; BiT-L 87.5%, a generalist)
- [[ImageNet-A and ImageNet-O Natural Adversarial Examples]] — related (a robustness set it is scored on)
- [[Sequence-Level Knowledge Distillation]] — related
- [[Compound Scaling of Depth, Width and Resolution (EfficientNet)]] — prerequisite-for
- [[UDA: Unsupervised Data Augmentation]] — related
