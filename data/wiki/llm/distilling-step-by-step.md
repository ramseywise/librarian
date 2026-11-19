---
title: Distilling Step-by-Step
tags: [llm, fine-tuning, concept]
summary: "Distilling step-by-step extracts rationales from a large LLM with few-shot chain-of-thought and trains a small T5 multi-task to predict both label and rationale, so it needs less labelled data and a far smaller model than the LLM (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-hsieh-2023-distilling-step-step-outperforming-larger.md
---

# Distilling Step-by-Step

Hsieh et al. (arXiv 2305.02301, preprint) ask whether rationales extracted from an LLM can serve as extra supervision for a small task model. Their hypothesis: rationales carry task knowledge that the inputs alone make hard to infer, so having the model predict them as a side task should improve its label predictions.

## Mechanism

1. Few-shot chain-of-thought prompts a 540B PaLM to output a label and a rationale for each training input.
2. A pretrained T5 learns both outputs in one multi-task run, told apart by the prefixes [label] and [rationale]; the loss is L = L_label + lambda L_rationale.
3. At test time the model outputs just the label.

Rationales are not an input; they are a second output the student must learn to produce. A single-task variant that trains rationale-plus-label together is worse: on ANLI it fell below standard fine-tuning (T5-Base 220M, 100% data).

## Reported results (self-reported)

- ANLI, human-labelled, T5-Large 770M: beats few-shot PaLM-540B with 80% of the labelled data, while standard fine-tuning cannot match it with 100%.
- e-SNLI, T5-Base 220M: 12.5% of the labelled data with this method beats standard fine-tuning on 100%, and a 220M model outperforms PaLM few-shot chain of thought with 0.1% of the dataset.
- Unlabelled setting (LLM labels only): an 11B T5 beats PaLM few-shot chain of thought on three of four datasets with under 3% of PaLM's size.
- Teacher choice: rationales from a 20B GPT-NeoX gave a smaller lift than from PaLM 540B on ANLI (T5-Base, 100% data); standard fine-tuning was 43.58 there.
- Headline claims: on average more than 50% fewer training examples, and above 85% fewer at best, and models up to 2000 times smaller than the LLM.

## Limits

- It needs about 10-shot human-written chain-of-thought demonstrations per task and a small extra training-time cost for generating rationales.
- LLM reasoning is weak on complex reasoning and planning tasks, and the effect of rationale quality is left to future work. The student inherits the teacher's biases.
- Four datasets and three task types; accuracy is mostly shown in figures, not tables; optimiser, lambda, schedule and decoding settings are not stated.

## See Also
- [[Knowledge Distillation with Soft Targets]] — prerequisite-for (the task-distillation baseline it extends)
- [[Chain-of-Thought Prompting]] — prerequisite-for (the prompt that produces the rationales)
- [[Impossible Distillation]] — alternative-to (distils without a large teacher)
- [[Reinforcement-Learned Teachers]] — related (teachers trained to explain)
