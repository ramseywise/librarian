---
title: MultiInstruct Multimodal Instruction Benchmark
tags: [multimodal, concept]
summary: "MultiInstruct is a 62-task multimodal instruction tuning benchmark with five expert-written instructions per task; tuning OFA on it improves zero-shot results and lowers sensitivity to instruction wording."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-xu-2023-multiinstruct.md
---

# MultiInstruct Multimodal Instruction Benchmark

MultiInstruct is described as the first multimodal instruction tuning benchmark: 62 tasks in 10 categories from 21 datasets, each in a unified sequence-to-sequence format with five expert-written instructions. The authors fine-tune OFA-large (472M parameters) on the training tasks and evaluate it zero-shot, with 9 multimodal tasks and 20 NLP tasks held out. They compare task-name prompts, transfer from text-only Natural Instructions (mixed or sequential), the number of task clusters and the number of instructions. A sensitivity metric measures how consistently a model answers when the wording of an instruction changes but the task does not.

## Reported results (self-reported)

- Five instructions per task raise aggregated performance and cut sensitivity compared with one fixed instruction (the one-instruction sensitivity is 24.62).
- Average sensitivity on unseen multimodal tasks: original OFA is far higher than the instruction-tuned models (OFA tuned on MultiInstruct 13.84, sequential transfer 10.45, mixed transfer 10.27).
- On Visual7W grounded VQA, zero-shot, the MultiInstruct-tuned OFA reaches a best-of-five-instructions score of 64.32 where original OFA and the task-name variant score about zero.
- Fine-tuning only on Natural Instructions harms multimodal zero-shot results (self-reported).
- Multimodal instruction tuning lifts zero-shot ROUGE-L on the 20 NLP test tasks over original OFA (OFA at 2.25). The model tuned with Natural Instructions is best on these tasks; in the same 20-NLP-task setting the mixed-transfer variant scores 43.32 and the sequential-transfer variant 30.79 (self-reported), with the mixed variant nearly equal to the best and the sequential one lower.

## Limits

- English only and vision-language only; one model size (OFA-large).
- Sensitivity measures only variation across instructions within a task. Only 62 tasks and five instructions each; the authors suggest crowd-sourcing or automatic generation.
- Gains from text-only transfer over the plain MultiInstruct baseline are not significant. Every run was executed once, with no significance tests.
- Internal inconsistency: Sec 4.1 samples the instruction template per batch, while Sec 4.2 says it is sampled per instance.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[InstructBLIP Instruction-Aware Query Transformer]] — related (instruction tuning on a different base model)
- [[LLaVA Visual Instruction Tuning]] — related
