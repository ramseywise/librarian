---
title: MME Benchmark
tags: [multimodal, concept]
summary: "MME scores multimodal LLMs on 14 subtasks (10 perception, 4 cognition) with manually written yes/no question pairs per image, reporting accuracy and the stricter per-image accuracy+ across 30 models (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-fu-2025-mme.md
---

# MME Benchmark

Fu et al. (NeurIPS 2025 Datasets and Benchmarks track, arXiv v5) set out to measure perception and cognition of multimodal LLMs without data leakage or prompt-engineering effects. Each image gets one question whose truth is yes and one whose truth is no, written by hand. Accuracy is per question; accuracy+ requires both questions of an image to be right. Random guessing gives 50% and 25%. Perception means recognising specifics such as existence, count, position and colour; cognition means combining that with the model's knowledge to deduce harder answers.

## Results (self-reported; 30 MLLMs, zero-shot)

- WeMM tops the perception leaderboard (maximum 2000) and GPT-4V the cognition leaderboard (maximum 800).
- A model that says yes every time the prompt names an object that is absent would get around 50% accuracy and near-zero accuracy+.
- Existence is the subtask where several models tie for first at 195, made of 98.33 accuracy and 96.67 accuracy+ on 30 COCO images and 60 questions. GPT-4V is ahead on OCR by over 22 points and by a wide margin on code reasoning. On text translation, numerical calculation and commonsense reasoning, no model passes 150.
- GPT-4V declines questions that identify people, so it scores zero on the celebrity subtask, and it also turns down some artwork questions.
- The authors report position as the weakest coarse-grained perception subtask, and show examples where a one-word change flips a perception answer or a right derivation ends in a wrong yes/no.

## Limits

- Some subtasks contain just 20 to 30 images, and each question shifts a score by 2.5 to 5 points, so ties and ranking gaps are noisy.
- The OCR, numerical, translation and code subtasks contain only easy items, and the authors admit coverage is limited.
- A yes/no format favours a bias toward no, and mixes hallucination with not following instructions. Any reply that does not begin with yes or no counts as wrong, and GPT-4V's refusals therefore count as wrong as well.
- The paper omits decoding settings, model versions and how many runs were made. Images partly come from public datasets such as COCO, so image-level contamination is possible. The models are 2023-era.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[MMBench]] — alternative-to (concurrent benchmark)
- [[POPE Object Hallucination Probing]] — related (object-hallucination focus)
- [[Microsoft COCO]] — prerequisite-for
