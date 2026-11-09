---
title: PaLI and PaLI-X Jointly Scaled VLMs
tags: [multimodal, concept]
summary: "PaLI feeds ViT patch features to an mT5 encoder-decoder and scales vision and language together on the multilingual WebLI dataset; PaLI-X pairs a 22B ViT with a 32B encoder-decoder and a 13-objective mixture (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-chen-2022-pali.md
  - data/raw/papers/2026-11-08-chen-2023-pali-x.md
---

# PaLI and PaLI-X Jointly Scaled VLMs

Both papers ask what is gained by scaling the vision encoder and the language encoder-decoder together, with a mixture of objectives, in a multilingual model where every task is cast as image plus text in, text out.

## PaLI (ICLR 2023)

- An mT5 encoder-decoder takes the unpooled patch features of a ViT as its visual tokens. Training makes one pass over a multilingual mixture of 1.6B examples at 224x224; the language part is updated while the ViT stays frozen. PaLI-17B adds a 10k-step phase at 588x588 with all parameters updated.
- Replacing ViT-G with the 4B ViT-e (about 13% more model) adds 3.2 points on the average of seven benchmarks, from PaLI-15B to PaLI-17B (self-reported). Enlarging mT5 from L to XXL (about 12B more parameters) gives +3.1 on that same average (self-reported). The paper reports +0.9 per 1B ViT parameters against +0.2 per 1B mT5 parameters (self-reported).
- For PaLI-17B the high-resolution phase adds 2.0 points to the average over seven benchmarks (self-reported).
- Generating open-vocabulary answers, PaLI-17B gets 84.3 on the VQAv2 test-dev split and 149.1 CIDEr on the COCO Karpathy test split (self-reported).
- Initialising from unimodal checkpoints matters: PaLI-3B from scratch scores 72.8 COCO CIDEr against 141.4 (200M-example ablation) (self-reported). Removing the VQG objective drops zero-shot VQG from 96.7 to 17.9 (self-reported).
- Pretraining PaLI-17B used 1,024 TPUv4 chips for a week, and the high-resolution phase added 512 chips for three days (self-reported).

## PaLI-X (2023)

- The vision side is a ViT-22B given extra training on JFT classification and a bag-of-words OCR classification task; the language side is a 32B encoder-decoder initialised from UL2. Projected patch embeddings are concatenated with the text embeddings.
- Training has two stages over 13 objectives (frozen ViT at 224px, then OCR and detection data at rising resolution up to 756px), followed by per-task or multitask fine-tuning.
- Across PaLI at 700M, 3B and 17B and PaLI-X at 55B (224px), complex counting appears between the 3B and 17B sizes, whereas simple counting improves more steadily (self-reported).
- At four shots PaLI-X captions COCO better than Flamingo, yet it trails Flamingo on few-shot VQAv2; the authors attribute that to fine-tuning the language backbone, which Flamingo keeps frozen (self-reported).
- Not pooling image tokens matters for few-shot use, per a 700M-parameter ablation (self-reported).
- Video: 16 frames beat 8 and set state of the art on 5 of 7 tasks (self-reported).
- Multitask fine-tuning costs little on captioning across six benchmarks. The extraction records this as a contradiction of the claim in Unified-IO that a multitask-versus-single-task gap exists.

## Limits

- PaLI: open-vocabulary VQA scoring counts paraphrases as wrong; fine-tuning on English-only data erodes some multilingual ability; without OCR input TextVQA is 58.80 against 73.06 with it. The high-resolution gain comes bundled with a changed mixture and unfrozen parameters, and is measured on PaLI-17B alone. The text names no checkpoints for the 3.2 versus 3.1 comparison, and no seeds are given. Weights, code and WebLI are not released.
- PaLI-X: no optimizer, compute or batch details; no seeds; WebLI and several mixture sources are unreleased; multitask fine-tuning loses 7.3 on Screen2Words; some video datasets miss 10% or more of their videos; counting emergence is read from four model sizes; ablations use 5B or 700M proxies.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Flamingo Gated Cross-Attention VLM]] — alternative-to
- [[UL2 Mixture of Denoisers]] — prerequisite-for
- [[PaLM-E Embodied Multimodal Language Model]] — related
