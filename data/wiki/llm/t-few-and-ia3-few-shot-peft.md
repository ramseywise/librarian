---
title: T-Few and (IA)3 Few-Shot PEFT
tags: [llm, fine-tuning, concept]
summary: "Liu et al. propose (IA)3, learned vectors that rescale keys, values and feed-forward activations, and T-Few, a fixed recipe on T0 that beat few-shot GPT-3 175B in-context learning at about 1,000 times fewer inference FLOPs (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-liu-2022-few-shot-parameter-efficient-fine.md
---

# T-Few and (IA)3 Few-Shot PEFT

Liu, Tam, Muqeeth et al. (preprint, under review) ask if fine-tuning a small parameter set on a handful of labelled examples can outdo few-shot in-context learning on both accuracy and compute. A further hypothesis is that an unlikelihood term helps rank classification by pushing down the probability of wrong answer choices.

## Components

- **(IA)3** adds learned vectors that rescale the keys, values and the inner activations of the feed-forward blocks. On T0-3B it adds 540K parameters, against 9.1M for LoRA.
- **T-Few** is one fixed recipe built from T0, (IA)3, a pre-training step for the (IA)3 vectors on T0's multitask mixture, an unlikelihood loss (LUL) and a length-normalised loss (LLN). No per-task tuning is needed.
- The authors designed it on T0-3B, using 5 few-shot subsamples drawn from nine held-out T0 datasets and comparing 12 PEFT settings, then ran it unchanged on T0 11B.

## Reported results (self-reported)

- T-Few on T0 11B beat few-shot in-context learning with GPT-3 175B on the held-out tasks (median over 5 few-shot subsets). GPT-3 figures are copied from Brown et al. rather than rerun.
- Inference cost is about 1,000 times fewer FLOPs than GPT-3 175B in-context learning (Kaplan's per-token estimates, with 41 shots of 98 tokens plus 103 tokens). Training T-Few costs about 20 times the FLOPs of a single GPT-3 175B in-context example, at 2.7e16 FLOPs (T0 11B, 1000 steps at batch size 8, sequence length 103).
- On RAFT (11 tasks, 50 training examples each, hidden test) T-Few set a new best and beat the human baseline with the recipe unchanged.
- (IA)3 was the only PEFT method that beat full-model fine-tuning on T0-3B with LUL and LLN.
- Adding LLN lifts full fine-tuning accuracy from 60.7 to 62.71, and adding LUL gives 63.3 (T0-3B, nine datasets). Pre-training the (IA)3 vectors moves accuracy from 64.6 to 65.8 (100k steps at batch size 16 on the T0 mixture).
- On T0 11B the ablations give 70.8 without pre-training, 68.3 without LUL and LLN, and 69.7 for neither. T0 zero-shot scores 66.9% and T5+LM in-context learning 49.6%.
- Storage in single-precision floats: the fine-tuned (IA)3 vectors occupy 4.2 MB, and the in-context examples 16 kB.

## Limits

- Every task is classification or multiple choice and is scored with rank classification; generative tasks are deferred by the authors.
- GPT-3 results were taken from Brown et al. without rerunning, and the few-shot subsets used there are not disclosed.
- The paper counts FLOPs as a proxy that does not depend on hardware; it does not measure latency.
- The authors' prompt tuning and Compacter results disagree with earlier reports, and varying hyperparameters did not close the gap.
- Design decisions were made on T0-3B with the very nine datasets later used to evaluate T0 11B.
- The paper is reported as a preprint under review.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for
- [[LoRA Low-Rank Adaptation]] — prerequisite-for (the PEFT baseline compared against)
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — prerequisite-for (T0 is the backbone)
- [[GPT-3 and Few-Shot In-Context Learning]] — alternative-to (the in-context baseline it beats)
- [[Prefix-Tuning and Prompt Tuning]] — alternative-to
