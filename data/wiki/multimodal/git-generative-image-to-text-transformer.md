---
title: GIT Generative Image-to-Text Transformer
tags: [multimodal, concept]
summary: "GIT uses one contrastively pretrained image encoder and a 6-block text decoder trained with a single language-modelling loss on 0.8B pairs, casting captioning, VQA, classification and scene-text tasks as caption generation (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-wang-2022-git.md
---

# GIT Generative Image-to-Text Transformer

Wang et al. (2022) ask whether a lone image encoder paired with a lone text decoder, scaled up in data and size and trained under one language-modelling loss, can unify captioning for images and video, QA, classification and scene-text recognition, with no detectors, tags or OCR. Their hypothesis is that a simple architecture with scale is enough.

## Mechanism

- A Florence/CoSwin image encoder (contrastively pretrained) gives flattened features, mapped to D=768 by a linear layer and layer norm, and concatenated with text embeddings. A randomly initialised 6-block transformer decoder with a seq2seq attention mask generates text. Pretraining uses 0.8B image-text pairs; GIT is 0.7B parameters with a 681M encoder.
- VQA, classification and scene text are all turned into caption generation. For video, 6 frames are used, with learnable temporal embeddings.
- GIT2 is 5.1B parameters (4.8B DaViT encoder) trained on 12.9B pairs.

## Results (self-reported)

- TextCaps test CIDEr beats the earlier OCR-using best (TAP) by 28.5 and is above a human row taken from an earlier paper; GIT2 reaches 145.0 (self-reported).
- nocaps test overall 123.0 against 120.6 for the 2.1B CoCa; COCO Karpathy test CIDEr is 144.8, below OFA at 145.3 (self-reported).
- Flickr30K few-shot (32-shot) 80.5 against 75.4 for Flamingo, but zero-shot 49.6 against 67.2 (self-reported).
- VQAv2 test-std is 78.81 with open-vocabulary generation, below the discriminative Florence (80.36) and also below Flamingo (82.1); TextVQA 59.75 against 54.1 for Flamingo. MSRVTT-QA is 43.2 against 47.4 for Flamingo (self-reported).
- Fine-tuning on ImageNet-1k through generation reaches 88.79% top-1, 1.2 points below Florence; zero-shot exact match is 1.93% (self-reported).
- Decoder ablations: COCO CIDEr is 136.4, 136.0 and 134.6 for 6, 12 and 24 layers (0.4B-pair subset); at 0.8B pairs a self-attention-only decoder comes out ahead on all 7 benchmarks, whereas cross-attention wins several at 10M pairs. Starting the decoder from BERT gives no benefit over random initialisation. Image-encoder initialisation matters: CLIP 131.4 against supervised 122.1 and random 89.0 on COCO (GITB, 10M pairs) (self-reported).
- Gender and skin-tone bias differences range from 0.7% to 5.3% over metrics (self-reported).

## Limits

- Controlling generated captions and in-context learning without parameter updates is unclear (authors).
- Larger decoders did not help; this may not carry over to frozen pretrained decoders.
- With the same encoder, generative VQA and ImageNet fall about 1.2 to 1.5 points behind discriminative Florence.
- Text and table disagree in two places per the extraction: on nocaps the text gives 123.0 against 120.6 for CoCa, and on TextVQA the text says +5.4 while 59.75 against 54.1 is a gap of 5.65.
- No seeds or variance; 0.6B of the 0.8B pairs are non-public; compute is not stated; toxic language in pretraining data is not ruled out.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[SimVLM PrefixLM Pretraining]] — related
- [[Flamingo Gated Cross-Attention VLM]] — alternative-to
- [[PaLI and PaLI-X Jointly Scaled VLMs]] — alternative-to
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for
