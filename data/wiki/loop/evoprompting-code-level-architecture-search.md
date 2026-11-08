---
title: EvoPrompting Code-Level Architecture Search
tags: [loop, pattern]
summary: "EvoPrompting uses a language model as the mutation and crossover operator in evolutionary architecture search over code, and soft-prompt-tunes the model on its own evaluated children each round."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2023-evoprompting.md
---

# EvoPrompting Code-Level Architecture Search

EvoPrompting (Chen, Dohan and So, NeurIPS 2023) uses a language model as the variation operator in an evolutionary search over code.

## Mechanism

Each round, few-shot prompts are built from the best surviving models, the language model writes candidate architectures as code, each candidate is trained and scored, the best become the next parents, and every evaluated child also feeds a soft-prompt tuning step for the next round. Settings: 10 parents, two in-context examples, 10 rounds, 10 prompts, 16 samples per prompt.

## Findings (self-reported)

- On the CLRS algorithmic-reasoning suite, discovered graph networks beat the Triplet-GMPNN baseline on 21 of the 30 tasks at similar model size. The search used only three tasks; the best models were afterwards scored on all 30. Setup: 62B PaLM, 1,600 models per search.
- Heapsort example: out-of-distribution accuracy up 125% for a 6.68% increase in model size; the paper's own reimplemented baseline scores much lower than the published one, so the gain is smaller against it.
- MNIST-1D ablations: plain few-shot prompting did not work; random parents with prompt-tuning did no better than that; fit parents without prompt-tuning came out far below the full method. Random parents plateau after about 200 individuals.

## Limits

- The threshold alpha is called an upper threshold in the text but a lower threshold in the appendix hyperparameter table.
- Fitness uses validation error while the Pareto plots use test error.
- The introduction points to an appendix number for a result that is Table 3 in section A.6.
- The ablations are read from plots, not a numeric table; four seeds.
- Search covers only the triplet representation, with nine seeds.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Evolve Loop]] — related
- [[Train-Test Ablation Audit]] — related
