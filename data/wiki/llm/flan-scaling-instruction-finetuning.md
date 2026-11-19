---
title: Flan-PaLM Instruction Finetuning Scaling
tags: [llm, fine-tuning, concept]
summary: "Chung et al. (2022) instruction-finetune T5 and PaLM on up to 1,836 tasks including nine chain-of-thought datasets, and report how held-out gains scale with task count and model size, at about 0.2% of pretraining compute for Flan-PaLM 540B (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-chung-2022-scaling-instruction-finetuned-language-models.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch08-dataset-engineering.md
---

# Flan-PaLM Instruction Finetuning Scaling

Chung et al. measure how the benefit of instruction finetuning changes with the count of finetuning tasks, the model size and the presence of chain-of-thought (CoT) data, and whether it transfers across model families. T5, PaLM, cont-PaLM and U-PaLM are finetuned (constant learning rate, Adafactor) on a blend of the Muffin, T0-SF, NIV2 and CoT collections totalling 1,836 tasks. Held-out evaluation uses MMLU, BBH, TyDiQA and MGSM. A human preference study (190 examples) and responsible-AI benchmarks come on top. A task here is a unique dataset and task-category pair; the normalized average is a macro-average of six scores rescaled against a floor such as random guessing. Every figure is self-reported.

## Results

- On the 1,836-task mixture (proportion A, four held-out suites) Flan-PaLM 540B adds 9.4 points of normalized average over PaLM 540B; the 8B model gains 15.5 and 62B gains 10.4.
- Task count: most of the gain arrives by 282 tasks, with 1,836 adding little (Flan-PaLM 8B, 62B and 540B). Huyen's chapter on dataset engineering reports the same shape, a steep climb from 9 to 282 tasks and then a plateau.
- Finetuning with no CoT data hurts held-out CoT results, and including nine CoT datasets restores them (8B, 62B, 540B; read from a figure).
- With CoT and self-consistency, Flan-PaLM 540B gets 75.2% on 5-shot MMLU, versus 69.3 for PaLM 540B direct. See [[Self-Consistency]].
- On 8-shot MGSM the same setup gives 72.0% against 57.9 for PaLM. It also gets 83.9% on GSM8K, which is not a held-out result because GSM8K training data sits in the mixture.
- On 1-shot TyDiQA, Flan-PaLM is 14.9% absolute above PaLM, and Flan-PaLM 62B beats PaLM 540B (58.7 vs 52.9 EM).
- Flan-T5-XL (3B) scores 52.4% on 5-shot MMLU (validation), above GPT-3 175B at 43.9%.
- Raters chose Flan-PaLM 540B over PaLM 540B for 79% of 190 open-ended prompts (temperature 0.7, 5 samples per prompt with the highest log-probability one shown, a single rater per pair).
- Cost: 1.4B finetuning tokens, which is 0.2% of PaLM's 780B pretraining tokens; for 540B that was about 512 TPU v4 chips over 37 hours, 0.2% of pretraining compute.
- Flan-U-PaLM 540B posts the top normalized average among the models trained (59.1, Table 5).
- On RealToxicityPrompts the chance of a toxic continuation for non-toxic prompts dropped, for the 8B models, from 0.44 with PaLM to 0.14 with Flan-PaLM. Zero-shot CivilComments AUC is 86.8 for Flan-PaLM 62B and 66.6 for PaLM 62B.
- The 8B model gained more in absolute terms than 540B, yet 540B had the larger relative error reduction (18.4% against 16.6%).

## Limits

- Runs were single, with no seeds or intervals. Only Flan-T5 weights are public; Flan-PaLM and PaLM are not released.
- Because baselines also improve with scale, the scaling plot cannot show whether small or large models gain more.
- Single-task finetuning of instruction-tuned models is not evaluated. Neither code-davinci-002 on BBH-algo nor finetuned ByT5 on TyDiQA is beaten by Flan-PaLM.
- Mixture proportions changed between sections, so Tables 3 and 5 do not compare directly. The 540B model's normalized average reads 58.5 in Table 3 (proportion A) but 58.4 in Table 5 (proportion B).
- The authors offer, without testing, explanations for why gains past 282 tasks are small.
- Responsible-AI evaluations are English-only and use a biased subset of identity terms.
- The text says 43.7 vs 37.5 for Flan-T5 11B against PaLM 62B on BBH-direct.

## See Also
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — prerequisite-for
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[LIMA: Small Curated Instruction Data]] — alternative-to (a small curated set where this page uses over a thousand tasks)
- [[Synthetic Instruction Data: Curation and Verification]] — related
