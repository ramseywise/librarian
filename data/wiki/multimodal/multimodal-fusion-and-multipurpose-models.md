---
title: Multimodal Fusion and Multipurpose Models
tags: [multimodal, concept]
summary: "A textbook digest on how deep to fuse modalities (early, joint, late), the structured-plus-unstructured data findings, and multipurpose multitask models (MultiModel, UniT, OFA, Gato, LIMoE, muNet), with the chapter's caveats about missing numbers."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch04-further-topics.md
---

# Multimodal Fusion and Multipurpose Models

Chapter 4 of Multimodal Deep Learning (Moldovan, Schulte, Koch et al.) extends past text and images. The extraction notes the chapter has almost no experimental numbers, that model comparisons are qualitative, that its authors admit that suitable metrics for multipurpose models are missing, and that many citations are unresolved. It is dated to 2022.

## Fusion depth

- **Early fusion** merges at the input layer, **joint fusion** merges learned latents inside the model with backpropagation, and **late fusion** combines predictions of per-modality models. The chapter's practice advice is to favour end-to-end learning rather than extracting features separately, to benchmark against single-modality baselines (especially structured-only), and to use multimodal dropout (dropping whole modalities in training) for missing modalities at inference.
- The taxonomy of four challenges is representation, alignment, fusion and translation. Joint representation learning projects a concatenated input into one space; coordinated learning keeps one space per modality and aligns them with a common distance.
- General architectures covered: Perceiver and Perceiver IO (a latent array as query compresses a long input by over 300x) and training paradigms data2vec, VATT and MultiMAE. Latent-prediction self-supervision avoids hard-negative mining and data-space decoders.

## Structured plus unstructured data

- In the survival-analysis and economics studies, the strongest single modality was usually the structured data, and where multimodal models were compared with every single-modality model they usually won. MultiSurv's best model used clinical plus mRNA data, adding more modalities slightly reduced performance, and for some cancer types roughly 20 training observations were available. Many studies skipped single-modality baselines, and small samples and publication bias could overstate the results.
- For Wide and Deep models, avoid feature overlap between the linear and neural parts or orthogonalise to keep identifiability.

## Multipurpose models

- MultiModel (eight datasets, four experts in MoE layers) was below the state of the art on ImageNet and translation and not clearly ahead of a specialist, yet far ahead on a task with little data. UniT (201M parameters) beat its specialist on multimodal tasks and lost on unimodal ones. OFA (33M to 930M parameters) beat the state of the art on captioning, VQA, visual entailment and grounding, fell short on unimodal tasks, and had no specialist baseline to compare against. Gato (79M to 1.18B parameters) was worse than specialist reinforcement-learning agents and needed fine-tuning on unseen tasks with mixed results.
- LIMoE-H/14 (12 MoE layers, 32 experts) beat CLIP by a significant margin with minimal extra parameters, with no numbers given; local and global entropy losses balance routing across modalities. muNet (an evolutionary method where the chance of drawing a parent for mutation halves each time that parent has been selected) beat a fine-tuned ViT with fewer parameters, with no numbers given.
- Training-cost comparators: GPT-2 about 168 hours on 32 TPUv3 chips, and one BERT (110M) training about 1,438 lbs of CO2 against 1,984 for a New York to San Francisco passenger flight (Strubell et al., as cited).

## Limits

- The OFA row of the comparison table has blank or ambiguous cells, and one subsection describes the authors' own unpublished work without results.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[V-MoE Sparse Mixture of Experts for Vision]] — related
- [[Multimodal Architectures Survey (Image-Text)]] — related
- [[PaLM-E Embodied Multimodal Language Model]] — related
