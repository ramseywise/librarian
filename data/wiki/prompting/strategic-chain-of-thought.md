---
title: Strategic Chain-of-Thought (SCoT)
tags: [prompting, pattern]
summary: One structured prompt makes the model list candidate methods and choose the most efficient as strategic knowledge before solving; a few-shot variant retrieves demonstrations by the chosen strategy.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2024-strategic-chain-thought.md
---

# Strategic Chain-of-Thought (SCoT)

SCoT's hypothesis is that valid strategies differ in error rate, so eliciting an efficient strategy before the reasoning gives steadier paths than unguided CoT.

## Mechanism

A single prompt with five parts (Role, Workflow, Rules, Initialization, Task Input). The workflow has the model enumerate candidate methods, choose the most efficient one as "strategic knowledge", and solve with that choice. The few-shot variant first collects correct zero-shot SCoT answers from a training set. At inference, one query produces a strategy, demonstrations matching that strategy are retrieved, and a second query gives the answer. No training is involved.

## Reported results (self-reported)

Unless noted: zero-shot, temperature 0, averaged over 3 runs.

- Llama3-8B: GSM8K 52.11 to 73.16; Tracking Object 44.27 to 68.40; +6.92 over zero-shot CoT averaged over eight datasets. Mistral-7B: +3.81 on average.
- 1-shot SCoT on GSM8K: 76.57 (Llama3-8B), 47.38 (Mistral-7B).
- Across seven models and three datasets: +1.11 to +24.13, except Llama3.1-8B on MMLU-math (59.63 to 56.42). On StrategyQA, Llama3.1-70B goes from 64.67 to 82.33.
- Llama3-8B ARC drops 80.60 to 78.02; single-run Self-Consistency scores 81.00. Mistral-7B ARC: 72.20 against 67.20.
- Mistral-7B AQuA ablation: CoT 29.13, +Role 32.28, +Workflow 31.89, SCoT 33.60 (0-shot), 35.04 (1-shot), 35.43 (3-shot). A Qwen2-72B auto-generated prompt scored 31.89.
- Output is 1.03 to 1.8 times as long as CoT (about 1.5 on average); Mistral-7B GSM8K is shorter (858.5 to 611.8 tokens). Gains shrink slightly as model size grows.

## Limits

- Workflow prompts are written by hand for each domain; the automatic version was a preliminary test only.
- Gains are uneven. The Self-Consistency baseline ran once, with the number of paths unstated. Few-shot SCoT was tested on 4 datasets and its retrieval method is not described.
- No code release, no significance tests.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Zero-Shot Chain-of-Thought]] — prerequisite-for
- [[Self-Consistency]] — alternative-to
- [[Least-to-Most Prompting]] — alternative-to
