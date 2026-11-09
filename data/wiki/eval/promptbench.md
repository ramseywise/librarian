---
title: PromptBench
tags: [eval, benchmark]
summary: "A modular Python library that unifies LLM evaluation across standard, dynamic (DyVal) and semantic (MSTemp) protocols, adversarial prompt attacks at four levels and six prompt-engineering methods, with 12 tasks and 22 datasets; its leaderboards are given only as figures (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhu-2023-promptbench.md
---

# PromptBench

Zhu and colleagues (JMLR 2024) describe a research library for evaluating LLMs under several protocols from one interface. The workflow has four steps: load a dataset, choose a model, define the prompts, and set up input and output processing together with a metric.

## Components

- Model loading for language and vision-language models, a dataset loader, and prompts including task-oriented and role-oriented styles. Few-shot prompts use three randomly chosen training examples per task.
- Six prompt-engineering methods and adversarial prompt attacks at four levels.
- Three evaluation protocols: standard; **DyVal**, which builds complexity-tailored samples on the fly instead of relying on a static set; and **MSTemp**, which generates out-of-distribution samples with evaluator LLMs and word replacement.
- The library currently supports 12 tasks and 22 public datasets (self-reported).

## Findings from the leaderboards (self-reported)

Numbers appear only in figures, so findings are directional.

- Every evaluated model is vulnerable to adversarial prompts, measured as the average PDR (the source does not define it) across GLUE tasks, MMLU, SQuAD v2, translation and maths; ChatGPT and GPT-4 hold up best.
- On GSM8K, CSQA and the object-tracking and date tasks, using two models (GPT-3.5-Turbo and GPT-4), no prompt-engineering method outperforms the baseline everywhere.
- On DyVal, GPT-4 clearly outperforms the other three models, though the tasks on linear equations, abductive logic and max-sum paths still leave room for improvement.

## Limits

- The authors concede that some evaluation scenarios fall outside the library and that certain metrics may overlook subtle differences.
- Results are partial and figure-only: the paper gives no numbers, seeds, temperature or attack budgets, does not define PDR, and omits model versions and decoding settings.
- The counts of models and datasets date from late 2023 to 2024.

## See Also
- [[HELM Holistic Evaluation]] — alternative-to (a compared evaluation framework)
- [[Benchmark Prompt Format Sensitivity]] — related
- [[Paired Input-Perturbation Eval]] — related
- [[Counterfactual Task Variants]] — related
