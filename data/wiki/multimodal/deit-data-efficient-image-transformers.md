---
title: DeiT Data-Efficient Image Transformers
tags: [multimodal, vision-backbones, concept]
summary: "DeiT trains the unchanged ViT architecture on ImageNet-1k alone by changing the recipe and adds a distillation token trained on a convnet teacher's hard labels, reaching 85.2% top-1 for the distilled base model with 1000 epochs."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-touvron-2020-training-data-efficient-image-transformers.md
  - data/raw/papers/2026-11-07-darcet-2023-vision-transformers-need-registers.md
---

# DeiT Data-Efficient Image Transformers

Touvron et al. test whether a vision transformer with no convolutions can reach competitive accuracy using ImageNet-1k as its only training data, and whether a token dedicated to distillation adds more. They bet that stronger augmentation and regularisation remove ViT's reliance on enormous pre-training sets, and that a convnet teacher feeding a distillation token passes on useful inductive bias.

## Method

DeiT keeps the ViT architecture unchanged (no convolutions; a plain linear classifier replaces the MLP head) and changes only how it is trained: optimiser AdamW, strong augmentation (RandAugment, Mixup, CutMix, random erasing), stochastic depth, repeated augmentation and no dropout. Repeated augmentation places each image three times per batch under different augmentations, so an epoch covers a third of the distinct images.

The distillation token is a learned token added alongside the class and patch tokens that interacts through self-attention. Its output is trained to reproduce the teacher's hard label, with loss 1/2 CE(student, true label) + 1/2 CE(student, teacher label). At test time the class and distillation softmaxes are summed. The usual soft distillation instead uses (1 - lambda) CE + lambda tau^2 KL on temperature-scaled outputs.

## Results (self-reported)

- DeiT-B distilled from a RegNetY-16GF teacher, trained 1000 epochs and fine-tuned at 384, hits 85.2% ImageNet top-1 with no external data, higher than ViT-B pre-trained on JFT-300M at 384. Without distillation, DeiT-B (86M parameters; 300 epochs at resolution 224, then fine-tuned at 384) gets 83.1.
- Under a like-for-like ImageNet-1k-only setup, DeiT improves top-1 by 6.3 points over the earlier ViT result. Reported separately, retraining ViT-B with the timm recipe alone moved it up from 77.91% to 79.35%.
- A 300-epoch DeiT-B run costs 53 hours on a single 8-GPU machine, and 25 further epochs of fine-tuning at 384 add 20 hours.
- With only the class token, hard-label distillation outperforms soft distillation (DeiT-B at 224, 300 epochs, RegNetY-16GF teacher), and soft distillation at 224 does no better than none. The best accuracy comes from fusing the class and distillation predictions late.
- A convnet teacher beats a transformer teacher of similar accuracy: RegNetY-16GF (82.9) gives a DeiT-B student 83.1 at pre-training, while a DeiT-B teacher (81.8) gives 81.9.
- At the input the class and distillation tokens start apart and drift to different vectors, then grow similar by the final layer. Two class tokens trained on one label collapse to a single vector and contribute nothing extra.
- Distilled DeiT-Ti and DeiT-S outperform the ResNet-18 and ResNet-50 counterparts (DeiT-S distilled at 224, 300 epochs, against ResNet-50 at 76.2).
- Distilled DeiT-B transfer, ImageNet pre-training with fine-tuning at 384: CIFAR-10 99.2, CIFAR-100 91.4, Flowers-102 98.9, Cars 93.9, iNaturalist-18 80.1, iNaturalist-19 83.0.
- Removing any of RandAugment, Mixup, CutMix and similar ingredients costs accuracy; using SGD rather than AdamW in pre-training gives 74.5 at 224. Longer schedules help the distilled model more, while plain DeiT levels off (read from a figure, so a claim not a table value).
- Fine-tuning resolution sweep for DeiT-B trained at 224: 160 gives 79.9, 224 gives 81.8, 320 gives 82.7 and 384 gives 83.1, with throughput falling from 609 to 86 images per second.

Darcet et al. retrain a supervised DeiT-III ViT-B on ImageNet-22k with and without register tokens: registers eliminate its high-norm outlier tokens, and its ImageNet, ADE20k and NYUd results stay about unchanged (self-reported). DeiT-III is the recipe name used there; this page covers the original DeiT. See [[Vision Transformer Registers and High-Norm Tokens]].

## Limits

- The hyperparameters may be suboptimal and some ablation rows did not train well. Transformers are sensitive to initialisation and optimiser settings, and several options did not converge.
- Without distillation DeiT sits a little below EfficientNet on the accuracy-versus-throughput curve. The headline 85.2 required 1000 epochs plus a convnet teacher the authors trained themselves.
- The gain of the distillation token over a class token is small (about 0.1 to 0.3 points), and the authors say the convnet-inductive-bias explanation is not formally established.
- Seed count, mixed-precision use and exact GPU model are not stated; evaluation is single-crop.
- Inconsistent setup: the Contributions text says training used one node of 4 GPUs for three days, while the Results give 53 hours for 300 epochs on an 8-GPU node; the page uses the latter.

## See Also
- [[Vision Transformer ViT Patch Tokens and Scaling]] — prerequisite-for
- [[Knowledge Distillation with Soft Targets]] — prerequisite-for
- [[ConvNeXt and ConvNeXt V2 Modernising a ResNet]] — related
- [[Swin Transformer Shifted Windows]] — related
- [[Vision Transformer Registers and High-Norm Tokens]] — related (retrains DeiT-III ViT-B with registers)
