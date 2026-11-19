---
title: "SimCLRv2 Pretrain, Fine-Tune, Distill"
tags: [data-science, pattern]
summary: "SimCLRv2 pretrains a big ResNet without labels, fine-tunes it on 1% or 10% of ImageNet labels, then distils it into a same-size or smaller student using unlabeled images only."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-chen-2020-big-self-supervised-models-strong.md
---

# SimCLRv2 Pretrain, Fine-Tune, Distill

The question is whether unsupervised pretraining, then supervised fine-tuning with a big network, then distillation on unlabeled data can learn well from 1% or 10% of ImageNet labels. The authors' hypothesis is that the fewer the labels, the more a bigger network helps, and that its task-specific knowledge can be moved into a smaller network with little loss.

## The recipe

1. **Pretrain** with SimCLRv2, a revision of SimCLR. Changes from SimCLR: larger ResNets (the biggest is ResNet-152 3x+SK), a projection head of three layers that is kept and fine-tuned starting at its first layer, and a memory in the style of MoCo.
2. **Fine-tune** the pretrained network on the 1% or 10% label subset.
3. **Distil** the fine-tuned network as teacher into a student of the same or smaller architecture, on unlabeled images with no real labels. The loss is the teacher's softened class distribution against the student's, with temperature.

The extraction defines *task-agnostic* use of unlabeled data as self-supervised pretraining without class labels, and *task-specific* use as imputing labels from a fine-tuned teacher. Self-distillation means the student has the teacher's architecture, excluding the projection head.

## Results (all self-reported, ImageNet)

- Distilled ResNet-50, teacher a self-distilled ResNet-152 (3x+SK): 73.9% top-1 with 1% of labels (13 or fewer per class) and 77.5% with 10%. The 10% figure is above a standard supervised ResNet-50 trained on all labels.
- Self-distilled ResNet-152 (3x+SK): 76.6% (1%) and 80.9% (10%).
- Distilled ResNet-50 (2x+SK) from the same teacher: 75.9% (1%) and 80.2% (10%). Reported comparison points: SimCLR ResNet-50 (4x) 63.0% and 74.4%; BYOL ResNet-200 (2x), concurrent work, 71.2% and 77.7%.
- Linear evaluation on frozen features, ResNet-152 (3x+SK), all labels: 79.8% top-1, a 4.3% relative gain on SimCLR.
- Fine-tuning on 1% of labels before distillation: 74.9% for ResNet-152 (3x+SK) versus 57.9% for the plain ResNet-50 (1x, without SK); the extraction gives the ResNet-50 to ResNet-152 (3x+SK) gain as 29% relative.
- Projection head: starting fine-tuning from the first layer of the deeper head improves on SimCLR's two-layer head by up to 14% relative at 1% labels, with less benefit on bigger ResNets. The memory adds about 1% in linear evaluation and 1%-label fine-tuning (batch size 4096).
- Distillation ablation, ResNet-50 student and ResNet-50 (2x+SK) teacher at 70.6% (1%) and 77.0% (10%): distillation loss on labeled plus unlabeled images gives 68.9% and 74.3%, against 12.3% and 52.0% with the labels only. Adding the label loss gives 69.0% and 75.1%. Distilling on the labeled images only gives 23.6% and 66.2%, which the extraction reads as unlabeled examples being essential for distillation.
- Teacher accuracy correlates strongly with student accuracy over five teachers. Distillation at temperature 0.1 or 1.0 gives similar results, and 2.0 is worse.
- CIFAR-10: the top score is 96.4%, reached by both the 101-layer and 152-layer +SK ResNets (1x width; fine-tuning used anywhere up to the full label set).

## Limits

- ImageNet is well curated and may not reflect real semi-supervised use.
- The reason larger models do better with few labels is only a conjecture, and the gains may partly reflect a ceiling effect.
- ResNet-152 (3x+SK) is marginally better than 2x+SK at almost double the parameters.
- No seeds, variance or confidence intervals; compute and wall-clock not stated.
- Distillation used only random crop and flip, with no strong augmentation or consistency loss.
- Vision only; the pretrain-then-fine-tune analogy with NLP is asserted, not tested.

## See Also
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for
- [[BYOL Bootstrap Your Own Latent]] — alternative-to (concurrent, compared in the paper)
- [[Noisy Student Self-Training]] — related (self-training; SimCLRv2 omits its noise and thresholding)
- [[Sequence-Level Knowledge Distillation]] — related
- [[Contrastive Visual Representations: SimCLR, MoCo, CPC v2 and PIRL]] — prerequisite-for
