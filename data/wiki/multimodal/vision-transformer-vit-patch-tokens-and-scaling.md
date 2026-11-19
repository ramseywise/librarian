---
title: Vision Transformer ViT Patch Tokens and Scaling
tags: [multimodal, vision-backbones, concept]
summary: "ViT feeds flattened image patches to a standard Transformer encoder with a class token; supervised pre-training on JFT-300M or ImageNet-21k makes it match or beat ResNets, and a follow-up study fits power laws to its error against compute up to ViT-G/14."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-dosovitskiy-2020-image-worth-16x16-words.md
  - data/raw/papers/2026-11-07-zhai-2022-scaling-vision-transformers.md
---

# Vision Transformer ViT Patch Tokens and Scaling

Dosovitskiy et al. ask whether a plain Transformer fed image patches, with almost no image-specific bias, can rival CNNs on classification once pre-trained at scale. Their bet is that scale beats inductive bias: lacking the locality and translation equivariance of a CNN, the model should trail on small data yet catch up with or pass ResNets after pre-training on 14M to 300M images. Zhai et al. then ask how ViT transfer quality scales with parameters, data and compute, expecting language-model-style scaling laws to carry over.

## Architecture

The image is split into fixed-size patches (16x16, 14x14 or 32x32), each flattened and linearly projected to D dimensions (the patch embedding). A learnable [class] token is prepended, learnable 1D position embeddings are added, and the sequence goes through a BERT-style encoder with pre-norm and a GELU MLP. The state of the [class] token at the output is the image representation. A hybrid variant builds the input sequence from CNN feature maps instead of raw patches. Models are pre-trained supervised with Adam and fine-tuned with SGD at higher resolution.

## Results of the original study (self-reported)

- ViT-H/14 pre-trained on JFT-300M gets 88.55% ImageNet top-1 (fine-tuned at resolution 518 with Polyak averaging, averaged over three fine-tuning runs), 77.63% across the 19 VTAB tasks (1,000 examples per task, 2,500 steps, learning rate 0.01), 94.55% on CIFAR-100 and 90.72% on ImageNet-ReaL.
- ViT-L/16 pre-trained on JFT-300M beats BiT-L (a ResNet152x4 on the same data) on ImageNet while using far less pre-training compute, 0.68k TPUv3-core-days, where BiT-L needs 9.9k and Noisy Student 12.3k. The ImageNet-21k version of ViT-L/16 scores 85.30% at 0.23k core-days.
- A JFT-300M scaling sweep (5 transfer datasets averaged, 7 ResNets, 6 ViTs and 5 hybrids, 7 to 14 epochs) found ViT reaching the same average transfer score with roughly a half to a quarter of the ResNet compute. Hybrids edge ahead of ViT only at small compute, and ViT shows no saturation over the sizes tried.
- Pre-training data size matters. When pre-trained on ImageNet alone, ViT-L ends up worse than ViT-B. ViT-B/16 reaches 77.91, 83.97 and 84.15 top-1 (fine-tuned at 384) after pre-training on ImageNet, ImageNet-21k and JFT, while ViT-L/16 reaches 76.53, 85.15 and 87.12. On random JFT subsets with no added regularisation, ViT-B/32 trails ResNet50 at 9M images and leads at 90M and beyond.
- Dropping position embeddings lowers ImageNet 5-shot accuracy by roughly 2.8 points for ViT-B/16, while the 1D, 2D and relative encodings land within about 0.3 points of each other. The learned embeddings capture 2D distance and row/column structure, and a few heads already attend over the whole image in early layers.
- Scaling depth gives the largest gains and width the smallest in the authors' sweep; a smaller patch size improves results without adding parameters. A class token and global average pooling perform similarly once the learning rate is tuned separately.
- A preliminary masked-patch self-supervision run (ViT-B/16, JFT, 1M steps) reaches 79.9% ImageNet, 2% above training from scratch and 4% behind supervised pre-training.

## Scaling study (self-reported)

Zhai et al. train ViTs from 5M to roughly 2B parameters on ImageNet-21k and on JFT subsets of up to 3B images, and fit error against TPUv3 core-days C with a saturating power law of the form c + a(C+d)^-b. The constant c is the error left at unbounded compute, and d shifts the x-axis since even a zero-compute model has non-zero accuracy. Fits read off the paper's figures give, for JFT-3B, a fine-tune curve with c=0.09, a=0.26, d=0.01, b=0.35 and a 10-shot curve with c=0.12, a=0.63, d=0.52, b=0.32; the ImageNet-21k 10-shot fit has exponent 0.61.

- ViT-G/14 (about 2B parameters), pre-trained on JFT-3B at 224 and fine-tuned on ImageNet at 518, reports 90.45% ImageNet top-1, a new best, and 84.86% 10-shot on frozen features. On ObjectNet it sits about 2% under CLIP, which skips ImageNet fine-tuning.
- Larger models use data more efficiently: matching L/16's 10-shot result takes Ti/16 about 100 times more images, and about 20 times more when fine-tuning (JFT-3B, ImageNet 10-shot). L/16 trained on only 30M images stalls near 27% error against 19% with more data. The authors conclude that given enough data, a bigger model trained for fewer steps is preferable.
- Recipe changes: a larger, decoupled weight decay on the head (it helps few-shot transfer but reduces upstream accuracy in a ViT-B/32 JFT-300M test); a global-average-pool or MAP head instead of the [class] token (with 257 tokens for ViT-H/14 at 224, rounding the token count up to a multiple of 128 on TPU can cost up to half again in memory); an Adafactor variant that cuts optimiser state to half the parameter count; bfloat16 for the first Adam moment, with no effect on outcomes; and a reciprocal-square-root schedule ending in a cooldown.
- Moving from JFT-300M to JFT-3B lifts ImageNet transfer by about 1% for both B/32 and L/16.

## Limits

- Only classification is evaluated in the original study, with detection and segmentation left as open problems. Its best numbers rest on JFT-300M, an unreleased internal dataset; with ImageNet as the only pre-training data, ViT-L trails ViT-B and same-size ResNets.
- The authors hedge on compute efficiency: pre-training cost may depend on schedule, optimiser and weight decay as well as architecture. The label-smoothing value, numeric precision, hardware counts and pre-training seeds go unreported, and the self-supervised result is a preliminary run.
- The extraction notes that later work showed ViT can train on ImageNet alone with stronger augmentation (see [[DeiT Data-Efficient Image Transformers]]).
- The scaling study uses proprietary JFT-3B, checked on public ImageNet-21k. Its authors say the conclusions may not generalise beyond the scale studied or beyond the ViT family; only supervised classification pre-training is covered; smaller models saturate at the low end of compute, so the power law needs the shift term.
- VTAB used one hyperparameter for all tasks, and a per-task sweep is left to future work. The number of seeds behind the plus-or-minus values in the scaling paper's main table is not stated, and some appendix rows are missing.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[DeiT Data-Efficient Image Transformers]] — extends (training recipe and distillation token on the same architecture)
- [[Vision Transformer Registers and High-Norm Tokens]] — extends
- [[DINO and iBOT Self-Distillation for Vision Transformers]] — extends
- [[Swin Transformer Shifted Windows]] — related
- [[Big Transfer (BiT) Generalist Pretraining]] — alternative-to (the ResNet baseline ViT is compared with)
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — prerequisite-for
- [[Residual Connections and the Degradation Problem]] — related
