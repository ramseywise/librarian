---
title: Contrastive Chain of Thought
tags: [prompting, pattern]
summary: Contrastive Chain of Thought adds an invalid rationale to each few-shot demonstration, built by shuffling the objects in the valid one, and reports gains over plain CoT on three reasoning sets with one model; a toy theory paper offers partial support.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-chia-2023-contrastive-chain-thought-prompting.md
  - data/raw/papers/2026-11-08-cui-2024-theoretical-understanding-chain-thought.md
---

# Contrastive Chain of Thought

Every few-shot example is paired with a second, invalid rationale beside the valid one. The wrong rationale is generated automatically: objects such as numbers and entities are extracted with spaCy and shuffled, giving an incoherent chain. The model sees both what to do and what to avoid. See [[Few-Shot Prompting]] for the base technique and [[Chain of Thought]] for the reasoning format.

## Reported results

Setup: GPT-3.5-Turbo (0301 snapshot), 4-shot, test sets capped at 500 items. All figures are (self-reported).

- Gains over standard CoT: +9.8 on GSM8K, +16.0 on Bamboogle, +14.4 on SVAMP.
- Combined with [[Self-Consistency]]: 86.2 against 71.0 on GSM8K, 71.7 against 55.9 on AQuA, 58.4 against 40.8 on Bamboogle.

## Theory and a second study

A separate paper analyses a one-layer linear-attention model. It finds coherent CoT beats stepwise in-context learning, and that noise in the demonstration's final answer adds only o(1/D) loss. It then tests error-aware demonstrations with hand-written incorrect paths. Gemini Pro on Tracking Shuffled Objects (7) goes from 58.20 to 64.80, and DeepSeek 67B on Penguins scores 80.14 against 73.97 (all self-reported). Gains on GSM8K are small or negative.

## Limits

- One model for the main study, with no decoding settings or seed counts reported; results are noisy.
- The theory is a toy model, and the incorrect paths in the second study are hand-written.
- No variance reported in either.

## See Also
- [[Chain of Thought]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
- [[Self-Consistency]] — related (used in combination)
