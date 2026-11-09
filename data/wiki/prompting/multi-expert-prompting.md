---
title: Multi-Expert Prompting
tags: [prompting, pattern]
summary: "One prompt chain simulates several experts, answers as each, then merges the answers with seven subtasks borrowed from the Nominal Group Technique; the paper reports 89.35 True% on TruthfulQA with ChatGPT at about 22.7 times the tokens of zero-shot CoT, and no gain on reasoning multiple choice (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-long-2024-multi-expert-prompting-improves-reliability.md
---

# Multi-Expert Prompting

Long, Yen, Tuan et al. (preprint, 2024) argue that a single role-played expert gives a one-sided answer, and that aggregating several experts' answers raises truthfulness and informativeness.

## Method

Step one asks the model for n experts, each with a one-sentence description, then answers once per expert. Step two puts the n answers into one prompt with seven numbered subtasks adapted from the **Nominal Group Technique**, a structured team decision process of idea generation, round-robin recording, discussion and voting: agreed facts, conflicts, resolution, isolated facts, collection, a combined answer and a best-answer selection. The model then chooses between the individual and the aggregated answers.

## Results

All numbers are the paper's own (self-reported).

- On TruthfulQA-Generation with gpt-3.5-turbo-0613 (n=3, temperature 0.0) and a fine-tuned ChatGPT judge: 89.35 True% against 80.66 for the best baseline, ExpertPrompting. Zero-shot CoT gets 70.38 on the same setup, and asking it to be more truthful moves it to 77.60.
- With Mistral-7B-Instruct-v0.2 at temperature 0.1: 87.15 against 81.88 for Self-refine.
- Ablation, ChatGPT, n=3: dropping step one gives 85.43, and the remaining ablations fall from 86.90 to 88.46. A naive "combine the responses" prompt gives 82.37, 6.98 below the seven-subtask version.
- Number of experts, ChatGPT: one gives 80.05, three is best, ten give 84.82. As judge, ChatGPT picks the aggregated answer over a single expert's on 95.44% of samples.
- On ExpertQA (528 open questions across 32 topics, ChatGPT judging), the method wins 75% of comparisons on informativeness and 76.5% on usefulness. For the ExpertPrompting comparison the judge matched a human annotator in 93% of cases.
- Cost on TruthfulQA with ChatGPT: 2345.78 average tokens against 103.31 for zero-shot CoT, and 3.8399 USD against 0.1634 (prices as of 1 Feb 2024).
- On multiple-choice reasoning it roughly matches zero-shot CoT and trails it on most tasks. It wins only on MMLU college_physics (45.54 against 37.62); on OpenBookQA it scores 71.80 against 79.20. ExpertPrompting alone scores 34.56 against 68.51 for zero-shot on ARC-Challenge.

## Limits

- Aggregation fits long-form answers; the authors suggest short-form answers need CoT thoughts alongside.
- It needs strong instruction following; all experts are weighted equally, and expert identities can be hallucinated. Three annotators checked 100 samples: ChatGPT gave one weaker expert in 27% of the three-expert sets, and two in 11%.
- Two models only (gpt-3.5-turbo-0613, Mistral-7B-Instruct-v0.2), one run, no seeds; FactualityPrompt was subsampled to 250 plus 250.
- Informativeness and usefulness come from ChatGPT as judge, validated by a small human check.

## See Also
- [[Self-Consistency]] — alternative-to (samples one chain repeatedly instead of varying the role)
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Branch-Solve-Merge]] — related
