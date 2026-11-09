---
title: Contrastive and Masked Vision-Language Pretraining
tags: [multimodal, comparison]
summary: "Family comparison of how vision and vision-language encoders are pretrained: contrastive dual towers, fusion encoders, masked image or video modeling, self-distillation, and LLM-bridged instruction tuning, with a page per method."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-akkus-2023-multimodal-deep-learning.md
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch02-introducing-modalities.md
  - data/raw/papers/2026-11-08-awais-2023-foundational-models-defining-new-era.md
  - data/raw/papers/2026-11-07-huang-2023-language-not-all-you-need.md
  - data/raw/papers/2026-11-07-bao-2021-beit.md
  - data/raw/papers/2026-11-07-cherti-2023-reproducible-scaling-laws-contrastive-language.md
  - data/raw/papers/2026-11-07-dai-2023-instructblip.md
  - data/raw/papers/2026-11-07-fang-2023-eva.md
  - data/raw/papers/2026-11-07-fu-2021-violet.md
  - data/raw/papers/2026-11-07-girdhar-2023-imagebind-one-embedding-space-bind.md
  - data/raw/papers/2026-11-07-grill-2020-bootstrap-your-own-latent.md
  - data/raw/papers/2026-11-07-he-2022-masked-autoencoders-scalable-vision-learners.md
  - data/raw/papers/2026-11-07-jia-2021-scaling-up-visual-vision-language.md
  - data/raw/papers/2026-11-07-kirillov-2023-segment-anything.md
  - data/raw/papers/2026-11-07-li-2021-align-before-fuse.md
  - data/raw/papers/2026-11-07-li-2022-blip.md
  - data/raw/papers/2026-11-07-liu-2021-swin-transformer.md
  - data/raw/papers/2026-11-07-lu-2019-vilbert.md
  - data/raw/papers/2026-11-07-oquab-2023-dinov2.md
  - data/raw/papers/2026-11-07-radford-2021-learning-transferable-visual-models-natural.md
  - data/raw/papers/2026-11-07-ramesh-2021-zero-shot-text-image-generation.md
  - data/raw/papers/2026-11-07-wang-2021-simvlm.md
  - data/raw/papers/2026-11-07-xu-2023-multiinstruct.md
  - data/raw/papers/2026-11-07-yu-2022-scaling-autoregressive-models-content-rich.md
  - data/raw/papers/2026-11-07-yuan-2021-florence.md
  - data/raw/papers/2026-11-08-berrios-2023-towards-language-models-that-can.md
  - data/raw/papers/2026-11-08-dong-2023-dreamllm.md
  - data/raw/papers/2026-11-08-kim-2021-vilt.md
  - data/raw/papers/2026-11-08-zellers-2021-merlot.md
  - data/raw/papers/2026-11-08-zhai-2023-sigmoid-loss-language-image-pre.md
---

# Contrastive and Masked Vision-Language Pretraining

This page compares the pretraining recipes that produce image, video and image-text representations, grouped by what the model is asked to predict. Each method has its own page; the numbers there are self-reported by the papers and use different data, so this page does not rank them.

## Families and what each predicts

| Family | Training signal | Methods |
|---|---|---|
| Contrastive dual tower | Match an image to its own text within a batch | [[CLIP Contrastive Language-Image Pretraining]], [[ALIGN Noisy Alt-Text Dual Encoder]], [[Florence UniCL Vision Foundation Model]] |
| Contrastive loss variants and extensions | Replace the softmax, or tie extra modalities to image embeddings | [[SigLIP Sigmoid Loss for Language-Image Pretraining]], [[ImageBind Emergent Cross-Modal Alignment]] |
| Fusion encoders | Align first or fuse directly, with matching and masked-language losses | [[ALBEF Align Before Fuse]], [[ViLBERT Co-Attention Two-Stream Pretraining]], [[ViLT Patch Projection Vision-Language Transformer]] |
| Generative image-text | Predict text given an image prefix, or clean the data with a captioner | [[SimVLM PrefixLM Pretraining]], [[BLIP Bootstrapped Captioning and Filtering]] |
| Masked image modeling | Predict masked patches as tokens, pixels or CLIP features | [[BEiT Masked Image Modeling with Visual Tokens]], [[Masked Autoencoders Pixel Reconstruction]], [[EVA Masked CLIP-Feature Regression]] |
| Self-distillation | Predict a moving-average target without negatives | [[BYOL Bootstrap Your Own Latent]], [[DINOv2 Curated-Data Self-Supervised Features]] |
| Video-language | Masked tokens and script knowledge from video | [[VIOLET Masked Visual-Token Modeling]], [[MERLOT Multimodal Script Knowledge]] |
| Backbones and segmentation | A general vision encoder and a promptable mask model | [[Swin Transformer Shifted Windows]], [[Segment Anything SAM and SA-1B]] |
| Instruction tuning and LLM bridges | Tune a vision-language model on instructions, or wire frozen parts together | [[InstructBLIP Instruction-Aware Query Transformer]], [[MultiInstruct Multimodal Instruction Benchmark]], [[LENS Frozen LLM with Vision Modules]], [[DreamLLM Interleaved Comprehension and Creation]] |
| Token-based generation | Generate images as discrete token sequences | [[DALL-E and Parti Autoregressive Text-to-Image]] |

## Design axes the papers expose

- **Target of the prediction.** BEiT predicts discrete dVAE tokens and reports that pixel regression is worse in its ablation; MAE reports tokens are no better than normalized pixels as a target; EVA regresses CLIP features. Each result uses a different setup (BEiT 300-epoch ViT-B ablation, MAE ViT-B/L/H on ImageNet-1K, EVA ViT-B pilot).
- **Negatives.** CLIP and ALIGN rely on in-batch negatives, SigLIP makes each pair an independent binary decision, and BYOL reports learning with none. The BYOL paper's own ablation adds negatives to its formalism and scores lower (70.9 against 72.5).
- **Data curation versus scale.** ALIGN trains on noisy alt-text, BLIP filters and re-captions it, Florence curates 900M pairs, and DINOv2 curates 142M images without text. The OpenCLIP scaling study on the CLIP page covers how performance moves with data and compute.
- **Detector use.** ViLBERT uses region features from a detector; ALBEF and ViLT drop it, and ViLT reports the largest speed gain at some accuracy cost on VQA.
- **Frozen versus trained parts.** InstructBLIP tunes only the Q-Former; LENS trains nothing; DreamLLM keeps both CLIP encoder and Stable Diffusion decoder frozen.

## Kosmos-1 and the surveys

Kosmos-1 is a language model trained from the ground up, with plain text, captioned images and interleaved image-text documents as its data: a 24-layer MAGNETO decoder (stated as about 1.3B in the method and 1.6B in the setup) taking CLIP ViT-L/14 embeddings through a Resampler, trained for 300k steps and then given language-only instruction tuning. Its self-reported zero-shot Flickr30k captioning beats Flamingo-3B and 9B (which are prompted with text-only examples), and its Raven IQ accuracy is barely above chance (22% against 17%). Later models in this line are covered on [[Kosmos-2 Grounded Multimodal LLM]], [[Flamingo Gated Cross-Attention VLM]] and [[BLIP-2 Q-Former Bridging]].

Three surveys supplied background. Akkus et al. (a student seminar booklet) report that the contrastive objective reached the generative objective's zero-shot ImageNet accuracy with one seventh of the data, and recommend wrapping labels in sentence templates and freezing pretrained unimodal parts. Chapter 2 of the same book covers the modality foundations. Awais et al. (mid-2023) propose a taxonomy of contrastive, generative, hybrid and conversational text-prompted models and visually prompted models, and note that CLIP applied naively performs poorly on localisation tasks.

## Limits

- Every number is reported by the cited papers under different data, model size and evaluation protocols; none is a controlled comparison.
- The surveys report numbers from other papers; the Akkus chapter-3 result tables are images. The extraction records inconsistencies: SimCLR ResNet-50(4x) at 85.8 in prose against 76.5 in its table, CO2 for the big Transformer at 249 t against 284 t, ViT-H layers given as 32, and a CLIP data size of more than 250M pairs in the chapter against 400M in the paper.
- Kosmos-1 results are a single 1.6B model with no seeds or variance, and its Flamingo baselines were prompted differently, so comparisons are not like for like.
- Awais et al. exclude generative image models (GANs, VAEs, diffusion), and their Table 3 mixes evaluation mechanisms.

## See Also
- [[Vision-Language Model Training Families]] — prerequisite-for (the broader survey of training families)
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for (the contrastive background)
- [[CLIP Contrastive Language-Image Pretraining]] — instance-of
- [[ALIGN Noisy Alt-Text Dual Encoder]] — instance-of
- [[SigLIP Sigmoid Loss for Language-Image Pretraining]] — instance-of
- [[Florence UniCL Vision Foundation Model]] — instance-of
- [[ImageBind Emergent Cross-Modal Alignment]] — instance-of
- [[ALBEF Align Before Fuse]] — instance-of
- [[ViLBERT Co-Attention Two-Stream Pretraining]] — instance-of
- [[ViLT Patch Projection Vision-Language Transformer]] — instance-of
- [[SimVLM PrefixLM Pretraining]] — instance-of
- [[BLIP Bootstrapped Captioning and Filtering]] — instance-of
- [[BEiT Masked Image Modeling with Visual Tokens]] — instance-of
- [[Masked Autoencoders Pixel Reconstruction]] — instance-of
- [[EVA Masked CLIP-Feature Regression]] — instance-of
- [[BYOL Bootstrap Your Own Latent]] — instance-of
- [[DINOv2 Curated-Data Self-Supervised Features]] — instance-of
- [[VIOLET Masked Visual-Token Modeling]] — instance-of
- [[MERLOT Multimodal Script Knowledge]] — instance-of
- [[Swin Transformer Shifted Windows]] — instance-of
- [[Segment Anything SAM and SA-1B]] — instance-of
- [[InstructBLIP Instruction-Aware Query Transformer]] — instance-of
- [[MultiInstruct Multimodal Instruction Benchmark]] — instance-of
- [[LENS Frozen LLM with Vision Modules]] — instance-of
- [[DreamLLM Interleaved Comprehension and Creation]] — instance-of
- [[DALL-E and Parti Autoregressive Text-to-Image]] — instance-of
