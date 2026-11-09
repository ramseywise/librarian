---
title: GeM-CoT
tags: [prompting, pattern]
summary: Routes each question to a typed demonstration pool by embedding similarity, falls back to zero-shot CoT for unmatched questions, and grows the pool by clustering cached fallbacks into auto-built demonstrations.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zou-2023-generalizable-chain-thought-prompting-mixed.md
---

# GeM-CoT

GeM-CoT handles mixed-task input streams, where fixed demonstrations from one dataset break on another. In the paper's pilot (100 shuffled questions), gold-demo few-shot reached 78.0 and zero-shot 66.0, while fixed single-dataset demonstrations collapsed to 27.0 (self-reported).

## Mechanism

1. Embed the question with Sentence-BERT and match it to a typed demonstration pool by dot product.
2. Above a threshold (0.35 worked best), use that type's few-shot CoT demonstrations. Otherwise answer with zero-shot CoT and cache the item.
3. Once the cache is large, cluster it with OPTICS. Large clusters yield 6 auto-built demonstrations each (k-means plus Auto-CoT-style filtering), which join the pool.

## Reported results (self-reported)

- Ten reasoning datasets, GPT-3.5-Turbo: 82.3 against 81.4 for few-shot CoT, 82.1 for Auto-CoT, 79.4 for zero-shot CoT and 80.7 for General-CoT. GPT-4 on AQuA, GSM8K and SVAMP: 86.6 against 85.5 and 81.0.
- Diversity-based selection beats similarity and random on AddSub (93.7 against 90.1 and 92.2).
- An LLM task classifier with 10 demonstrations is only 42% accurate, while category+form typing reaches 99%. Using an LLM as the type classifier reaches similar accuracy (AddSub 93.4, Strategy 64.5) at the price of extra API calls; an oracle with gold types gets AddSub 90.1 and Strategy 65.0.
- BBH streaming, 2000 questions in five batches: from the second batch on, GeM-CoT is ahead of zero-shot CoT.

## Limits

- Does not improve the reasoning itself; efficiency of demonstration selection is left open.
- Wrong type matches derail reasoning. Single runs on OpenAI models at temperature 1.0. The demonstration pool is seeded from the ten datasets.

## See Also

- [[Zero-Shot Chain-of-Thought]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Complexity-Based Prompting]] — alternative-to
