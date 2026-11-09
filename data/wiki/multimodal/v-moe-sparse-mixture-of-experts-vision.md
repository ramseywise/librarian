---
title: V-MoE Sparse Mixture of Experts for Vision
tags: [multimodal, concept]
summary: "V-MoE replaces a subset of ViT MLP blocks with sparse expert layers (32 experts, top-k routing per patch) and adds Batch Prioritized Routing, which drops the least useful patches first when expert capacity is small (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-riquelme-2021-scaling-vision-sparse-mixture-experts.md
---

# V-MoE Sparse Mixture of Experts for Vision

Riquelme et al. (2021) ask whether sparse conditional computation lets Vision Transformers grow to dense state-of-the-art quality while needing less compute. Vision backbones like this feed the image side of the models in [[Vision-Language Model Architectures]].

## Mechanism

- A subset of ViT MLP blocks becomes a sparse MoE layer: 32 experts, routing per patch with a top-k taken after the softmax, a fixed expert buffer capacity and importance plus load auxiliary losses. The top-k-after-softmax order beat the softmax-after-top-k order of earlier work on ViT-S/32 (self-reported).
- **Batch Prioritized Routing (BPR)** sorts tokens across the whole batch by their largest routing weight before assigning buffer slots, so when capacity C is low the least useful patches are the ones dropped. The paper notes router outputs encode expert-token fit, not importance, so BPR uses them as a proxy.
- Pretraining on JFT-300M (or JFT-3B for the largest model), then few-shot linear transfer or full fine-tuning.

## Results (self-reported)

- V-MoE-15B (14.7B parameters, 48 blocks, JFT-3B) reaches 90.35% ImageNet top-1 after fine-tuning at 560x560, above Meta Pseudo Labels at 90.2%, at 16.8k TPUv3-core-days against 22.5k quoted for that baseline (self-reported).
- On ImageNet 5-shot, V-MoE-L/16 outperforms dense ViT-H/14 using about half of the FLOPs at inference and 57% of the runtime. At matched FLOPs V-MoE-H/14 with BPR gains about a point but takes 118% of the runtime (self-reported).
- Trained with BPR at low capacity, V-MoE-S/32 matches dense upstream performance with about 20% fewer training FLOPs (4 seeds); V-MoE-H/14 remains competitive at inference while processing only 15-30% of tokens, where vanilla routing collapses (self-reported).
- In fine-tuning, setting capacity C=0.1 lowers ImageNet accuracy from 77.4% to 68.6%, and BPR brings it back to 71.8%; generous capacity matters more during fine-tuning than during pretraining (74.1% against 71.7%) (self-reported).
- With 9M JFT images the L/32 model cannot use its extra capacity; from 30M it does. VTAB gain is 0.9 points at L/16 and within confidence intervals at H/14 (self-reported).

## Limits

- The authors suspect that the fine-tuning protocol was never tuned for sparse models.
- At equal FLOPs, dense models run faster, because of the cost of moving data between devices.
- Without RandAugment, V-MoE gives no gain when pretrained on ImageNet-21k, because of overfitting.
- The paper omits batch size, warmup and hardware counts, and JFT is not public; hyperparameters were tuned for transfer, not JFT precision.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[DINOv3 Gram Anchoring Self-Supervised Backbone]] — related (a vision backbone at a different scaling axis)
- [[Swin Transformer Shifted Windows]] — related
