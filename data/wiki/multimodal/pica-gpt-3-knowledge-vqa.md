---
title: PICa GPT-3 Knowledge VQA
tags: [multimodal, concept]
summary: "PICa turns an image into a caption and tags, then prompts a frozen GPT-3 with a few examples; with 16 shots it reports 48.0% on OK-VQA against 39.4% for the supervised state of the art (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-yang-2022-empirical-study-gpt-3-few.md
---

# PICa GPT-3 Knowledge VQA

Yang et al. (arXiv v2, September 2022; AAAI 2022) test whether a frozen GPT-3 can serve as an implicit knowledge base for knowledge-based VQA, with neither a retrieval step nor fine-tuning. The extraction spells the name out as a prompt for GPT-3 built on image captions.

## Mechanism

- Beforehand, every image is turned into a caption (VinVL-base) and optionally tags from a cloud tagging API. A prompt then carries a fixed instruction, n in-context examples each made of caption, question and answer, and finally the test item, after which GPT-3 writes the answer.
- PICa-Full adds two things: choosing in-context examples by CLIP similarity to the test question (or question plus image), and a multi-query ensemble that builds k prompts from n times k examples and keeps the answer with the highest summed log-probability.

## Results (self-reported)

- Unless noted, the setup is a frozen 175B GPT-3, soft VQA accuracy, and the OK-VQA test split of 14,055 image-question pairs. PICa-Full, with 16 shots plus captions and tags, scores 48.0%; the supervised MAVEx baseline scores 39.4% and KRISP 38.9. Frozen, which trains a visual encoder, reaches 12.6 on OK-VQA and 38.2 on VQA v2.
- Zero-shot is low and one example gives a large jump; the ensemble helps most with one example (36.4 at k=1, 40.8 at k=5). Dissimilar examples hurt, and answer-similarity oracle selection serves as an upper reference.
- A captioner trained on Conceptual Captions rather than COCO still beats the supervised baseline with selection and ensemble, which the authors use to address overlap between the COCO captioner's training images and OK-VQA test images.
- On VQA v2 validation, few-shot PICa beats Frozen but the supervised Oscar model (73.8) is far ahead. The extraction strips most other figures, so they are not reproduced here.

## Limits

- Captions and tags describe an image only partly, missing details such as colour and counts; the authors expect end-to-end vision tuning to help.
- The raw model is inaccessible, so behaviour analysis rests on prompted rationales. Decoding temperature, maximum tokens and engine are not stated; single runs with no variance.
- The best captioner was fine-tuned on COCO 2014 train. All images are COCO photos, with no charts or documents. Open-ended answers make scoring depend on answer-format agreement.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[OK-VQA]] — prerequisite-for
- [[VQA v2 Balanced Dataset]] — prerequisite-for
- [[Frozen Visual Prefix Few-Shot]] — alternative-to
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for
