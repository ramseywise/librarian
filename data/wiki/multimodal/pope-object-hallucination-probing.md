---
title: POPE Object Hallucination Probing
tags: [multimodal, concept]
summary: "POPE asks a vision-language model yes/no questions about whether chosen objects are in an image, with absent objects sampled randomly, by popularity or by co-occurrence; it varied less across prompts than caption-based CHAIR in the authors' tests (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-li-2023-evaluating-object-hallucination-large-vision.md
---

# POPE Object Hallucination Probing

Li et al. (EMNLP 2023, arXiv 2305.10355) study whether large vision-language models hallucinate objects that are not in the image and how to measure it more stably than with caption-based CHAIR. **POPE** (Polling-based Object Probing Evaluation) casts hallucination as binary classification.

## Mechanism

Each probe is a question of the form "Is there a X in the image?", with a 1:1 ratio of present to absent objects. Absent objects are chosen in one of three ways: at random, by popularity, or adversarially from objects that co-occur with those truly present. Object lists come either from COCO annotations or from SEEM segmentation, which extends POPE to unannotated images. Yes or No is decided by word matching.

## Results (self-reported)

Setups: five open models, MSCOCO validation, CHAIR on 2,000 images; POPE on 500 images.

- Instruction-tuned LVLMs show more hallucination than the small VLPMs; InstructBLIP has the lowest CHAIR_S under the first prompt. CHAIR is prompt-sensitive: mPLUG-Owl's CHAIR_S goes from 25.4 to 76.8 between two prompts.
- For LLaVA over four prompts, CHAIR_I has a standard deviation of 3.22 against 0.78 for POPE F1.
- Under the random setting InstructBLIP gets F1 89.29, whereas LLaVA, MultiModal-GPT and mPLUG-Owl all fall under 70. MultiModal-GPT says Yes to 99.97% of questions, giving accuracy 50.03.
- InstructBLIP F1 drops from 89.29 (random) to 83.45 (popular) to 78.45 (adversarial); MiniGPT-4 drops from 78.86 to 71.37. With SEEM-derived objects, MiniGPT-4 adversarial F1 is 62.70.
- For mPLUG-Owl, roughly half of the hallucinated objects in each image are drawn from the 10 most common COCO objects; for LLaVA, the 30 most common objects cover about 70% of hallucinated ones.
- Consistency: of 1,303 objects InstructBLIP answered No to, none appeared in its captions; for MiniGPT-4, 5 of 1,445 did.
- Less hallucination does not mean better VQA: on A-OKVQA, MiniGPT-4 beats LLaVA in POPE F1 (72.47 vs 66.64) yet trails it in VQA score (38.69 vs 50.51).

## Limits

- Object-level only; attributes, counts and positions are left open. POPE measures hallucination alone, so a higher score does not mean a stronger model.
- Subsets of validation sets (500 images) were used because of compute; word matching may miss answers phrased differently; SEEM labels may differ from human ones.
- Few open models, no closed-source or later ones. The link to instruction data is correlational, with no retraining on altered data. Single run, no confidence intervals.

## See Also
- [[VLM Benchmark Shortcuts]] — related (lists POPE among the CHAIR alternatives)
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[LLaVA Visual Instruction Tuning]] — related (LLaVA is among the models tested)
- [[Microsoft COCO]] — related (the image source)
