---
title: LLMSelector Per-Module Model Assignment
tags: [infra, pattern]
summary: "LLMSelector picks a different model for each module of a fixed multi-call pipeline by coordinate search with an LLM diagnoser that scores each module separately; the authors report 5-70 point gains over the best single model on six tasks, with two synthetic tasks driving the top end (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2025-optimizing-model-selection-compound-ai.md
---

# LLMSelector Per-Module Model Assignment

Chen et al. (arXiv 2502.14815, a preprint) ask which model should run which module of a compound AI system, meaning a fixed pipeline of several LLM calls. The baseline is the usual choice of one model for every module. LLMSelector starts from a random assignment, cycles through the modules, tries each candidate model in a module, and keeps the one that scores best; it stops after a full pass with no change.

## Why a diagnoser

Scoring only the end-to-end answer makes the search stall: in the authors' two-module TableArithmetic study, GPT-4o mini in both modules was a local optimum where changing one module alone did not help. LLMSelector instead asks an LLM diagnoser (Gemini 1.5 Pro in that study) to judge each module's output separately, using the gold answer, and mixes that estimate with the end-to-end score. On that study it reached the best assignment after trying 10 of the 25 possibilities, whereas random search had to try all of them, a 60% saving (self-reported).

## Results (self-reported)

Setup: three static pipelines (self-refine with 3 modules, multi-agent debate with 6, locate-solve with 2), ten candidate models (GPT-4o and mini, GPT-4 Turbo, Claude 3.5 Sonnet and Haiku, Gemini 1.5 Pro and Flash, Llama 3.1 405B and 70B, Qwen 2.5 72B), six datasets, half of each for search and half for evaluation.
- Compared with the best single model on each task, LLMSelector scored: 95 against 89 on LiveCodeBench, 84 against 75 on CommonGenHard, 28 against 21 on SimpleQA, 70 against 65 on FEVER, and 100 against 30 and 44 on the two synthetic table tasks. No model was best on every task.
- DSPy MIPROv2 prompt optimisation with GPT-4o alone gained 1 point on SimpleQA, against 7 for LLMSelector.
- In qualitative single examples, mixing models gave debaters diverse first answers, while one model as generator and critic repeated its own mistake.
- Theorem: the search converges to the best assignment on the training data under strong assumptions (unique optimum, binary scores, monotone modules) that the authors say do not always hold.

## Limits

- Fixed pipelines only: no run-time routing, tool-using agents or loops, and every module is an LLM call.
- The two locate-and-solve tasks are synthetic with 100 questions each and most single models near 0%; the extraction calls the 70- and 56-point gains upper-end, not typical.
- No cost, latency or token figures are measured; only the number of API calls during search is counted. No seeds or intervals; models are early-2024 vintage.
- The diagnoser needs gold answers; no standalone diagnoser accuracy was found. The text names GPT-4o as best on FEVER while the table has Llama 3.1 405B at 65% against 64%.

## See Also
- [[Cheap-First Gating and Model Cascades]] — prerequisite-for
- [[AutoMix Self-Verification Routing]] — related
- [[HSE and Router Robustness in Model Societies]] — related (asks whether a pool is different enough to be worth routing over)
- [[DSPy]] — alternative-to (prompt search rather than model search)
