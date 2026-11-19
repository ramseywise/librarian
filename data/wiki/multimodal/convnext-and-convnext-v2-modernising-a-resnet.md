---
title: "ConvNeXt and ConvNeXt V2 Modernising a ResNet"
tags: [multimodal, vision-backbones, concept]
summary: "ConvNeXt applies a stepwise roadmap of Transformer-era design and training choices to a ResNet without attention, and ConvNeXt V2 adds Global Response Normalization and a sparse-convolution masked autoencoder; both papers report their own ImageNet, COCO and ADE20K numbers (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-liu-2022-convnet-2020s.md
  - data/raw/papers/2026-11-07-woo-2023-convnext-v2.md
---

# ConvNeXt and ConvNeXt V2 Modernising a ResNet

## ConvNeXt

Liu, Mao, Wu and colleagues (CVPR 2022) ask whether a plain ConvNet, once it adopts design and training ideas from vision Transformers, can keep pace with hierarchical Transformers such as Swin. They hypothesise that much of the Transformer's edge comes from the training recipe and from macro and micro design choices, not from self-attention.

The roadmap begins with ResNet-50 (and ResNet-200) trained under a DeiT and Swin style recipe. Each step is then applied in turn, with ImageNet-1K top-1 tracked: the ratio of compute across stages, a patchify stem (a non-overlapping 4x4 convolution with stride 4), depthwise convolution with wider channels, an inverted bottleneck (the MLP's hidden width is four times its input width), kernels grown to 7x7, GELU, fewer activation and normalisation layers, LN replacing BN, and downsampling in its own layers. The outcome is a T/S/B/L/XL family, scaled further with ImageNet-22K pretraining.

Results (self-reported):

- A stronger recipe by itself takes ResNet-50 from 76.1 up to 78.8 (mean of 3 seeds). The recipe lasts 300 epochs and combines AdamW with Label Smoothing, Stochastic Depth, Random Erasing, RandAugment, Cutmix and Mixup. So some of the ConvNet-versus-ViT gap is down to training technique.
- Inside the ResNet-50 regime, one GELU per block is the biggest single gain (+0.7 on a starting 80.6). A 7x7 depthwise kernel beats 3x3 (which scores 79.9) and gains stop at 7x7. LN instead of BN adds a little, reaching 81.5 from 81.4. Inverting dimensions helps more with ResNet-200 than with ResNet-50, where it adds +0.14%.
- At 224^2 and 4.5G FLOPs, trained on ImageNet-1K only, ConvNeXt-T is 0.8 points ahead of Swin-T. ConvNeXt-B at 384^2 is 0.6 points ahead of Swin-B and its V100 throughput is 12.5% higher. On an A100 with TF32, channels-last and PyTorch 1.10 at 224^2, ConvNeXt-S has up to 49% more throughput than Swin-S.
- ConvNeXt-XL has 350M parameters; pretrained 90 epochs on IN-22K and fine-tuned 30 epochs at 384^2, it gets 87.8% ImageNet-1K top-1.
- ADE20K, UperNet, 160K iterations at batch 16 and multi-scale testing: ConvNeXt-B (IN-22K pretraining, 640^2) leads Swin-B by 1.4 mIoU. COCO, Cascade Mask-RCNN with a 3x schedule and multi-scale training: ConvNeXt-XL (IN-22K pretraining) gets 55.2 box AP.
- Isotropic ConvNeXt against a DeiT-trained ViT on ImageNet-1K at 224^2: S 79.7 and 79.8, B 82.0 and 81.8, L 82.6 and 82.6 (ConvNeXt first).
- With per-GPU batch size 2, Cascade Mask-RCNN training uses less peak memory with ConvNeXt-B than with Swin-B.

## ConvNeXt V2

Woo, Debnath, Hu and colleagues (preprint, 2023) ask whether masked-autoencoder pre-training can be made to work for pure ConvNets. They hypothesise that merely pairing ConvNeXt with MAE gives poor results, and that adding feature competition to the architecture, together with a fully convolutional MAE, cures feature collapse.

- **FCMAE** hides 60% of the 32x32 patches. The ConvNeXt encoder sees only the visible pixels, through submanifold sparse convolution. One ConvNeXt block serves as the decoder, rebuilding patch-normalised pixels with MSE on the masked patches.
- **GRN** (Global Response Normalization) aggregates each channel by a global L2 norm, divides each channel's value by the mean of those norms across channels, and then calibrates with learnable gamma and beta plus a residual connection. It sits after the expansion MLP, and LayerScale is removed.

Results (self-reported):

- ConvNeXt-Base, IN-1K, 800 epochs of FCMAE then 100 of fine-tuning, 224 single crop: FCMAE alone just equals 300-epoch supervised training, and FCMAE with GRN exceeds it. With the V1 architecture, FCMAE reaches 83.7 where 100-epoch supervised training reaches 82.7 and 300-epoch supervised 83.8.
- Taking out sparse convolution drops accuracy from 83.7 to 79.3. For ConvNeXt-Large, FCMAE with GRN gets 85.6 against 84.4 for V1. Under supervised training GRN makes little difference.
- Ablations on ConvNeXt-Base: global L2 aggregation scores 84.6, global average pooling 83.7. Among normalisers, GRN gets 84.6, LN 83.8, LRN 83.2 and BN 80.5. GRN outperforms SE and CBAM while adding no parameters. A one-block ConvNeXt decoder performs like a UNet decoder and pre-trains 1.7x faster. A mask ratio of 0.6 works best.
- Sparse encoding gave about 1.3x the throughput of masked dense convolution at half the memory (measured with MinkowskiEngine 0.5.4 on PyTorch 1.8.0 and an RTX A6000, at batch 64 per GPU, 224x224 images and mask ratio 0.6).
- For the Huge model, 1600 epochs of FCMAE on IN-1K alone give 86.3, under ViT-H MAE's 86.9. Adding an IN-22K fine-tuning stage and moving to 512^2 inputs (659M parameters) lifts it to 88.9% top-1, trained on public data alone. For Base, 1600 epochs give 84.9 and 800 give 84.6.
- COCO: the Huge FCMAE model scores 55.7 box AP with Mask R-CNN (3x schedule, IN-1K pretraining, 2525G FLOPs). ADE20K: 57.0 mIoU with UperNet (707M), after 22K fine-tuning at 640^2.
- The 3.7M-parameter Atto model with FCMAE gets 76.7, and the V1 supervised version 75.7 (IN-1K, single 224 crop). For ConvNeXt V2-Base, FCMAE pre-training also comes out ahead of MoCo V3.

## Limits

ConvNeXt:

- The authors grant that Transformers may suit multi-modal learning (via cross-attention) and tasks with discretised, sparse or structured outputs better.
- The roadmap was worked out at small scale, mainly in a single ResNet-50 setting averaged over seeds; the ResNet-200 setting is one run. Training compute and hardware are not given.
- The authors think the split of compute across stages is probably not ideal.
- Throughput was timed on V100 and A100 GPUs from 2021, so the main efficiency claims depend on that hardware.
- For COCO and ADE20K the Swin baselines come from public repositories and were not retrained, apart from a Swin-B and Swin-L sweep on COCO.

ConvNeXt V2:

- Only end-to-end fine-tuning is evaluated; there is no linear probe or frozen-feature test.
- There are no seeds, error bars or significance tests, so gaps of 0.1 to 0.5 points come from single runs.
- On IN-1K alone the Huge model falls behind ViT-H MAE; the authors propose that bigger ViTs gain more from self-supervised learning.
- Feature collapse is described as a potential issue and supported by visualisation and cosine distance, with no causal test.
- Sparse-convolution libraries are not heavily optimised, so how much efficiency is gained depends on the framework.
- ADE20K models are initialised from weights already fine-tuned with IN-1K labels, not raw self-supervised weights; the small models' pre-training epochs are not stated.
- Headline runs used TPUs with dense masked convolution, while the sparse GPU variant is a reproduction in PyTorch.

## See Also
- [[Masked Autoencoders Pixel Reconstruction]] — prerequisite-for
- [[Swin Transformer Shifted Windows]] — alternative-to
- [[Residual Connections and the Degradation Problem]] — prerequisite-for
- [[ResNeXt Cardinality in Residual Blocks]] — prerequisite-for (grouped and depthwise convolution)
- [[Early and Late Dropout]] — related (reports late stochastic depth gave ConvNeXt-B no gain)
- [[DINOv3 Gram Anchoring Self-Supervised Backbone]] — related (distils into ConvNeXt students)
- [[Vision Transformer ViT Patch Tokens and Scaling]] — related
