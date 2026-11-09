---
title: InstructBLIP Instruction-Aware Query Transformer
tags: [multimodal, concept]
summary: "InstructBLIP instruction-tunes only the Q-Former of a BLIP-2 model on 13 held-in datasets and feeds it the instruction too, improving zero-shot results on 13 held-out datasets."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-dai-2023-instructblip.md
---

# InstructBLIP Instruction-Aware Query Transformer

InstructBLIP studies vision-language instruction tuning over 26 datasets spanning 11 task categories: 13 held-in datasets are used for tuning and the other 13 are held out for zero-shot evaluation, and four task categories are held out in full. It begins from a pretrained BLIP-2 (a ViT-g/14 image encoder, the Q-Former and a frozen LLM) and tunes only the Q-Former on instruction templates. The twist is that visual features are extracted with the instruction in view: the Q-Former receives the instruction along with the LLM, so what it extracts depends on the task. Datasets are sampled in proportion to the square root of their size, with some manual adjustment. Models are released on FlanT5 and Vicuna backbones.

## Reported results (self-reported)

- Zero-shot on the 13 held-out datasets, the FlanT5-XL model improves on BLIP-2 FlanT5-XL by 15.0% on average, in relative terms (self-reported). On the six datasets shared with Flamingo-80B, the 4B model beats it by 24.8% average relative improvement (self-reported).
- MSRVTT-QA zero-shot (4 frames): up to 47.1% relative improvement over the prior best, although no temporal video data was seen; FlanT5-XXL scores 25.6 against 17.4 for both Flamingo-80B and BLIP-2.
- NoCaps zero-shot CIDEr is 123.1 for Vicuna-7B, whereas the BLIP-2 Vicuna-7B model gets 107.5 (self-reported).
- Ablations (self-reported): removing instruction-aware features lowers ScienceQA-IMG by 7.0 points (FlanT5-XL) and iVQA from 52.2 to 36.8 (Vicuna-7B); without them the held-in average goes from 94.1 down to 89.8, and without data balancing it goes down to 92.6.
- Instruction tuning beats multitask training on the held-out average (52.9, against between 45.5 and 46.8), and the two roughly tie on held-in data; multitask training stays at the BLIP-2 zero-shot level (self-reported).
- On ScienceQA-IMG, finetuned FlanT5-XXL scores 90.7 (self-reported), while BLIP-2 gets 89.5 and LLaVA 89.0, with trainable parameters cut from 1.2B to 188M by freezing the visual encoder at 224x224.
- FlanT5 variants do better at multiple choice and Vicuna variants at open-ended generation, an explanation the authors attribute to the frozen LLM but did not test.

## Limits

- Hallucination and bias come along from the frozen LLMs; the authors advise a safety and fairness check before downstream use.
- No seeds or significance tests. Ablations cover FlanT5-XL and Vicuna-7B on five held-out datasets only.
- The GPT-4, LLaVA and MiniGPT-4 comparisons are a few hand-picked examples, dating from early 2023.
- Pretraining data of the LLM and image encoder is not audited for contamination.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[BLIP Bootstrapped Captioning and Filtering]] — related (earlier method from the same line of work; InstructBLIP builds on BLIP-2)
- [[LLaVA Visual Instruction Tuning]] — alternative-to (instruction tuning with generated data)
- [[MultiInstruct Multimodal Instruction Benchmark]] — related
- [[MiniGPT-4 Linear Projection Alignment]] — related
- [[Vision-Language Model Architectures]] — related
