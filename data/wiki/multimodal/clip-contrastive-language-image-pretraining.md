---
title: CLIP Contrastive Language-Image Pretraining
tags: [multimodal, concept]
summary: "CLIP trains an image encoder and a text encoder together with a symmetric contrastive loss on web image-text pairs, so class names can be turned into a zero-shot classifier; a later open study (OpenCLIP) fits power-law scaling curves and finds scaling differs by training dataset."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-radford-2021-learning-transferable-visual-models-natural.md
  - data/raw/papers/2026-11-07-cherti-2023-reproducible-scaling-laws-contrastive-language.md
  - data/raw/papers/2026-11-07-akkus-2023-multimodal-deep-learning.md
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch02-introducing-modalities.md
---

# CLIP Contrastive Language-Image Pretraining

CLIP trains an image encoder plus a text encoder, both from scratch, using a symmetric InfoNCE contrastive loss over 400M web (image, text) pairs that the authors name WIT. At test time the class names are embedded using prompt templates and serve as a zero-shot linear classifier. The authors describe it as ConVIRT in simplified form, trained at scale.

## Results from the original paper

All numbers below are self-reported, for zero-shot CLIP with a ViT-L/14 at 336 px unless noted.

- On ImageNet it matches the original ResNet-50 while using none of the 1.28M training labels (self-reported).
- It outperforms a linear probe fitted on ResNet-50 features, winning on 16 of the 27 datasets (self-reported).
- The template "A photo of a {label}." adds 1.3% on ImageNet, and averaging 80 prompts in embedding space then adds 3.5% more (self-reported). Across 36 datasets, prompt engineering with ensembling adds close to 5 points on average (self-reported).
- Measured by zero-shot ImageNet with a ResNet-50 encoder, the contrastive objective is 4x as efficient as a bag-of-words prediction baseline, which in turn is 3x as efficient as a transformer caption model (self-reported).
- Zero-shot CLIP shrinks the gap between ImageNet accuracy and accuracy under seven natural distribution shifts by up to 75% (self-reported). A logistic regression fitted on ImageNet raised accuracy there by 9.2% (to 85.4%) but slightly lowered the average accuracy under shift (self-reported).
- Pretraining cost was 18 days on 592 V100 GPUs for RN50x64 and 12 days on 256 V100 GPUs for ViT-L/14 (self-reported).

## Open scaling study (OpenCLIP on LAION)

Cherti et al. train CLIP models from ViT-B/32 to g/14 with OpenCLIP on LAION subsets of 80M, 400M and 2B pairs and fit power laws E = beta*C^alpha on the Pareto frontier of total compute (self-reported). Zero-shot ImageNet error falls with a steeper exponent for the OpenAI WIT-400M models than for the LAION models, whereas zero-shot MS-COCO and Flickr30K retrieval scale more steeply on LAION (self-reported). The authors hypothesise that the training data explains the difference. ViT-H/14 on LAION-2B, at 34B samples seen, reaches 78.0% zero-shot ImageNet (self-reported). Fine-tuned OpenCLIP models reach as high as 88.5% ImageNet top-1 (self-reported). The study's total pre-training cost was 370.41 MWh (self-reported).

## Data sizes quoted by the survey

The survey by Akkus et al. reports 400M pairs for CLIP and, for the objective, that the contrastive form reached the generative form's zero-shot ImageNet accuracy with a seventh of the training data (reported from other work).

## Limits

- On average, zero-shot CLIP is only competitive with a ResNet-50 feature linear probe; the authors estimate roughly 1000x more compute would be needed to approach the overall state of the art (claim).
- It is weak on fine-grained classes, counting, satellite, tumour and traffic-sign tasks, and reaches 88% on MNIST; it can only choose among the class names supplied.
- The authors queried entire validation sets while developing the method, so the zero-shot claims are not clean. WIT is unreleased, and no seeds or variance are reported.
- In the OpenCLIP study the dataset explanation for the reversal is untested, only three OpenAI models were available for comparison, sampling across scales is sparse, and the duplicate check is a simple perceptual-hash test. Batch size differs from the original recipe (86-88K against 32K).
- Source inconsistency: the extraction of the textbook chapter notes it gives more than 250M pairs for CLIP's data, while the paper states 400M.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for (the contrastive objective in general)
- [[ALIGN Noisy Alt-Text Dual Encoder]] — alternative-to (same objective, noisier and larger data)
- [[SigLIP Sigmoid Loss for Language-Image Pretraining]] — extends (replaces the softmax loss)
- [[Florence UniCL Vision Foundation Model]] — extends
- [[EVA Masked CLIP-Feature Regression]] — extends (uses CLIP features as targets)
- [[ImageBind Emergent Cross-Modal Alignment]] — extends
- [[unCLIP Hierarchical Text-Conditional Generation]] — related (conditions a decoder on CLIP image embeddings)
- [[MERLOT Reserve Audio-Video-Text Pretraining]] — extends
- [[StyleCLIP Text-Driven StyleGAN Editing]] — extends
- [[RA-CM3 Retrieval-Augmented Multimodal Modeling]] — related
- [[PICa GPT-3 Knowledge VQA]] — related
- [[LAION-5B Open CLIP-Filtered Image-Text Dataset]] — related
- [[Multimodal Architectures Survey (Image-Text)]] — related
- [[InternVL Scaled Vision Encoder with QLLaMA]] — related
