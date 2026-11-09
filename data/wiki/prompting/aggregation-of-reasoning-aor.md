---
title: "Aggregation of Reasoning (AoR)"
tags: [prompting, pattern]
summary: Replaces majority voting over sampled chains of thought with an LLM evaluation of the chains themselves, scored locally within answer buckets and globally across buckets, with dynamic sampling.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-yin-2024-aggregation-reasoning.md
---

# Aggregation of Reasoning (AoR)

Self-consistency picks the most frequent answer among sampled chains. AoR starts from the pilot observation that when majority voting is wrong the right answer is often still among the samples, so the evidence for it must be recovered by judging reasoning quality instead of counting.

## Mechanism

- Sample chains and bucket them by final answer.
- **Local scoring:** an LLM scores the chains within each bucket.
- **Global evaluation:** the top chains of different buckets are scored jointly over k rounds; the bucket with the highest mean score wins.
- **Dynamic sampling:** add batches of chains while the margin between the top two buckets is below a threshold. Batch size 5 was chosen; with epsilon=3 over 95% of chains pass, with epsilon=8 under 10%.

## Reported results (self-reported)

- Pilot: in cases where the vote was wrong, over 80% still had the right answer somewhere among the samples. Per dataset: Penguins 96.3, AQuA 96.1, Date 93.0, CSQA 81.6.
- GPT-3.5-Turbo-0301, temperature 1, six math sets: CoT-AoR(20,40) averages 90.57 against 87.48 for CoT-SC(40). ComplexCoT-AoR averages 90.70, against 88.78 for DiVeRSe and 88.25 for SC. AQuA 75.9 against 68.7; GSM8K 91.8 against 88.9.
- On AQuA with GPT-3.5, AoR(20,40) is 7.2 points above CoT-SC(40) while costing about 20% less.
- Averaged over four LLMs, the gain is +8.1% against SC and +7.6% against complexity-based CoT, with Llama-2 reaching +16.6% against SC. Using GPT-4 as the evaluator adds +2.4 (Claude-2), +3.6 (Llama-2) and +5.1 (Mistral).
- SC saturates beyond about 60 chains.

## Limits

- Relies on manual demonstrations; the context window bounds how many chains can be scored at once.
- Main numbers use GPT-3.5-Turbo-0301 only, a single run and at most 500 samples. The evaluator comes from the same model family as the generator.
- The prompts live in a GitHub repository, not in the paper.

## See Also

- [[Self-Consistency]] — prerequisite-for
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Complexity-Based Prompting]] — extends
- [[Tree of Thoughts]] — alternative-to
