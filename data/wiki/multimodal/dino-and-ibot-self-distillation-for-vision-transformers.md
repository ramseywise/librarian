---
title: DINO and iBOT Self-Distillation for Vision Transformers
tags: [multimodal, vision-backbones, comparison]
summary: "DINO trains a student ViT to match an EMA teacher's output with centering and sharpening instead of negatives; iBOT adds a masked-patch version of the same loss so the teacher acts as an online tokenizer."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-caron-2021-emerging-properties-self-supervised-vision.md
  - data/raw/papers/2026-11-07-zhou-2021-ibot.md
---

# DINO and iBOT Self-Distillation for Vision Transformers

Both methods train a Vision Transformer without labels by distilling a teacher, a momentum-averaged copy of the student (the EMA teacher: an exponential moving average of its weights) with the same architecture, into the student. DINO asks whether self-supervised pretraining gives ViTs traits that supervised ViTs and convnets lack, such as visible scene layout and strong k-NN features; the authors suspect that supervised pretraining is why ViTs had shown little advantage. iBOT asks if BERT-style masked image modelling trains ViTs effectively if the visual tokenizer is itself learned online with the model, and holds that a semantically meaningful tokenizer is the crux.

## DINO

A student (a ViT or ResNet) is trained to match a momentum teacher's K-dimensional softmax outputs with cross-entropy. Multi-crop supplies local-to-global correspondence: the student sees every crop, the teacher only the global views. Collapse is prevented by centering and sharpening the teacher outputs, with the centre updated as C = m*C + (1-m)*mean of teacher outputs.

Results (self-reported, ImageNet val unless noted):
- ViT-B/8 scores 80.1% linear and 77.4% k-NN top-1. At 800 epochs ViT-S/16 scores 77.0 linear (a supervised ViT-S gets 79.8) and 74.5 k-NN, and ResNet-50 gets 75.3 linear and 67.5 k-NN. On ViT-S, DINO leads BYOL, MoCo v2 and SwAV (all run by the authors) by 3.5% in linear and 7.9% in k-NN accuracy.
- Ablations on ViT-S/16 at 300 epochs: with no momentum encoder the framework collapses; omitting centering or sharpening drives the KL to zero; using the previous epoch's teacher gives 66.6 k-NN, whereas copying the student or using the previous iteration fails to converge; MSE in place of cross-entropy lowers k-NN; a student-side predictor barely matters. Multi-crop helps DINO the most (+3.4% linear) and harms BYOL.
- Multi-crop exchanges memory for time: two 224 crops plus ten 96 crops give 74.6 in 24 hours, against 72.5 in 46 hours for two 224 crops alone (ViT-S/16). Smaller patches help without extra parameters but lower throughput.
- Thresholding the [CLS] token's best attention head and scoring against PASCAL VOC12 by Jaccard gives comparable figures for several self-supervised ViT-S/16 models (SwAV 46.8, MoCo-v2 46.3, BYOL 47.8; DINO lacking multi-crop 45.1), so the property is shared across self-supervised training and not unique to DINO.
- Fine-tuning on ImageNet with the DeiT procedure from DINO ViT-B/16 weights beats starting from supervised pretraining (81.9) or random initialisation (81.8). A DINO ViT-S/16 trained for 300 epochs on two 8-GPU servers over 3 days (72.6 hours) reaches 76.1% linear.

## iBOT

The student gets blockwise-masked views and the teacher the unmasked ones. The loss sums, without rescaling, a cross-entropy term on [CLS] between the teacher's and student's softmax outputs (across views, as in DINO) and one on the masked patch tokens (within the same view). The teacher is an EMA of the student and uses soft token distributions as targets, with a single projection head serving both [CLS] and patch tokens. The online tokenizer is simply the teacher backbone with its projection head. Reported pre-training epochs are scaled to count the extra images that multi-crop adds.

Results (self-reported):
- Pre-trained on ImageNet-1K for 1600 effective epochs, ViT-B/16 gets k-NN 77.1, linear 79.5 and fine-tuned 84.0. With ImageNet-22K pre-training, ViT-L/16 scores 82.3% linear and 87.8% fine-tuned at image size 512. The linear improvement over DINO increases with model size: 0.9 for ViT-S, 1.3 for ViT-B.
- In a 300-epoch ViT-S/16 ablation, masked modelling without any [CLS] distillation reaches only 9.5 on k-NN and 29.8 on linear; BEiT using the DALL-E tokenizer reaches 6.9 k-NN, 23.5 linear and 81.4 fine-tuned; taking DINO as a fixed tokenizer yields 44.3 k-NN versus 69.1 for iBOT. Soft token distributions beat hard labels.
- Dense tasks: with ViT-B/16, COCO box AP 51.2 and mask AP 44.2 (DINO 50.1 and 43.4) with Cascade Mask R-CNN, and ADE20K mIoU 50.0 with UperNet, 3.2 over DINO. Part-wise probing on ViT-S/16 at 800 epochs: top-56 patch tokens give iBOT 5.9 points over DINO.
- With multi-crop, iBOT needs 25% more memory and takes 7.4% longer to train than DINO (ViT-S/16, batch 1024 on two 8-GPU V100 machines).

## Limits

- DINO: the bulk of the ablations use ViT-S/16, 300 epochs and k-NN rather than the headline ViT-B/8, and no seeds or error bars are given. BYOL could not be trained past 300 epochs, so the main comparison puts it at 300 against 800 for the rest. A figure gives the mask threshold as 60% and the appendix as 80%. Combining multi-crop with BYOL is left open, and pretraining uses curated ImageNet only.
- iBOT: single runs; masked modelling pays off only when paired with the [CLS] distillation loss. With ImageNet-1K data, ViT-L/16 fine-tunes 0.4 under BEiT (84.8 against 85.2), which the authors read as iBOT needing more data at larger scale. On image retrieval (ROxford medium: DINO 37.2, iBOT 36.6) and video object segmentation it does not beat DINO. Multi-crop without random masking was unstable. In the clustering results the text gives NMI as 32.8% but the table lists NMI 78.6 and ARI 32.8.

## See Also
- [[Vision Transformer ViT Patch Tokens and Scaling]] — prerequisite-for
- [[BYOL Bootstrap Your Own Latent]] — prerequisite-for (DINO takes its inspiration from BYOL)
- [[Contrastive Visual Representations: SimCLR, MoCo, CPC v2 and PIRL]] — prerequisite-for
- [[BEiT Masked Image Modeling with Visual Tokens]] — alternative-to (offline DALL-E tokenizer that iBOT replaces)
- [[DINOv2 Curated-Data Self-Supervised Features]] — extends
- [[Masked Autoencoders Pixel Reconstruction]] — alternative-to
- [[DeiT Data-Efficient Image Transformers]] — related (DINO fine-tuning uses its procedure)
- [[Vision Transformer Registers and High-Norm Tokens]] — related
