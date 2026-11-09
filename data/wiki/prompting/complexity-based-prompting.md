---
title: Complexity-Based Prompting
tags: [prompting, pattern]
summary: Choose the chain-of-thought exemplars with the most reasoning steps, and vote only among the longest sampled chains; helps large models on math, little on small ones.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-fu-2022-complexity-based-prompting-multi-step.md
---

# Complexity-Based Prompting

Two linked ideas from Fu et al. The first, complexity-based prompting, picks the eight training-set examples whose chains have the most reasoning steps (a step is a line; where no chains exist, the longest questions are chosen and annotated by hand). The second, complexity-based consistency, samples N chains (N=50) and votes only among the K longest; K equal to N recovers self-consistency.

## Reported results (self-reported)

- Complex-chain prompts averaged 9.0 steps on GSM8K against 3.4 for handcrafted and 2.8 for random exemplars.
- Codex (code-davinci-002), 8-shot with "Let's think step by step", greedy: the largest gain was +18 points on MathQA over handcrafted CoT; new best results were claimed for GSM8K, MultiArith, MathQA, Penguins and (with voting) GSM8K.
- On the GSM8K 200-item dev split, complexity-based selection beat random, centroid and retrieval selection; on MathQA, retrieval beat it (69.5 against 42.5), which the authors tie to near-duplicate questions and annotation of the full training set.
- Eight complex exemplars beat 24 simple ones that total the same number of steps (72).
- Best K was below N, typically 30 to 40 with N=50; voting among the simplest K chains was always worse than voting among all.
- The advantage appeared on simple test cases rather than hard ones.
- Newline splitting was the best step format on GSM8K dev.

## Limits

- No variance, seeds or tests; dev-split differences of 1 to 2 points are within noise.
- The gain disappeared on small models (the 6.7B GPT-3 curie and Flan-T5 11B), which the authors call emergent.
- Gains were negligible for GPT-3 on Date Understanding (-0.4) and for Codex on StrategyQA (+0.8).
- Why complex prompts help simple cases is left open; K is tuned on dev with no rule; sampling temperature and token limits not stated; no prompts or code released in the text.
- Only GPT-3 and Codex-era models (code-davinci-002 is now deprecated) and mostly math tasks.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Self-Consistency]] — prerequisite-for
- [[Few-Shot Prompting]] — related (exemplar selection)
- [[Aggregation of Reasoning (AoR)]] — related (uses a complexity-based baseline)
