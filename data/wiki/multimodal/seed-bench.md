---
title: SEED-Bench
tags: [multimodal, concept]
summary: "SEED-Bench is a 19K-question multiple-choice benchmark over 12 image and video dimensions, with human-verified answers and scoring by option likelihood; in its July 2023 tests the best of 18 models reached 53.37% (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-li-2023-seed-bench.md
---

# SEED-Bench

Li et al. (arXiv 2307.16125 v2) ask how generative comprehension in multimodal LLMs can be evaluated objectively and at scale across images and video, without relying on small test sets or GPT or human judges.

## Construction

- 19,242 four-option questions over 12 spatial and temporal dimensions. The paper states this is about 6 times the size of MMBench and 9 times MME.
- ChatGPT or GPT-4 writes questions from captions, detections and OCR output for CC3M images; video questions come from ground-truth annotations because the authors say automatic temporal extraction is unreliable.
- Questions that three text-only LLMs (Vicuna-7B, Flan-T5-XXL, LLaMA-7B) can answer without the image are removed (5.52% of the generated set); the survivors then go to human verifiers.
- Models are scored by the likelihood they give each option, not by parsing generated text.

## Results (self-reported; 18 models, four-option, likelihood scoring)

- The best model reaches 53.37% overall. Text-only LLaMA-7B scores 26.75% against 25% chance.
- InstructBLIP (Flan-T5-XL) is best on temporal dimensions at 38.31 and top on 8 of 12 dimensions; the authors credit its large instruction-tuning set (16M samples) and its frozen LLM, neither of which they ablated.
- Among video LLMs the leader is VideoChat with 37.63% overall (rank 6 of all models); Video-ChatGPT gets 31.17% and Valley 30.32%.
- LLaVA scores 33.52% overall and 23.75% on temporal dimensions, below the text-only LLMs.
- Most models stay under 40% on text recognition and the best reaches only about 40% on spatial relations; on procedure understanding the best model is about 5% above LLaMA.

## Limits

- Questions and distractors depend on ChatGPT or GPT-4 reading captions and detections from other models, so their mistakes and phrasing habits can leak in; the humans only check the result.
- Ranking options by likelihood is sensitive to how long and how worded each option is, and differs from how chat models are actually used.
- Dimension sizes are uneven (85 to 4,649 questions). Runs are single, with no variance; video input handling per model is not stated.
- Images come from CC3M web captions, and the paper does not discuss overlap with the training data of the evaluated models. Only July 2023 models are tested.
- The 87.0% alignment figure it gives for MMBench's matching is reported from that benchmark, not re-measured.

## See Also
- [[MMBench]] — alternative-to (its matching is criticised here)
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[VLM Benchmark Shortcuts]] — prerequisite-for
- [[LLaVA Visual Instruction Tuning]] — related
