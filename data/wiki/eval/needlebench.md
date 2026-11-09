---
title: "NeedleBench"
tags: [eval, reference]
summary: "NeedleBench is a bilingual synthetic long-context benchmark with information-sparse needle tasks and an information-dense Ancestral Trace Challenge; retrieval is near-solved at 128K while multi-needle reasoning is not (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-li-2024-needlebench.md
---

# NeedleBench

The benchmark is built on the idea that a model can pass needle-in-a-haystack retrieval and still reason poorly when long contexts are dense with information.

## Design

- Sparse tasks place invented needles at different depths and lengths inside essay filler text: single-needle retrieval, multi-needle retrieval and multi-needle reasoning, in Chinese and English, at 32K and 128K.
- The Ancestral Trace Challenge (ATC) is dense: a shuffled set of 2 to 512 kinship statements, no filler. ENL-50 is the largest number of needles at which exact-match accuracy stays at or above 50%.

## Results (self-reported)

- ATC, 10 repeats, greedy decoding, exact match on a boxed answer: the best long-reasoning model had an ENL-50 of 256, GPT-4.1 64, GPT-4o 8, and a 32B distilled model 4. Most models fail entirely beyond 64 needles.
- Under-thinking, where reasoning halts midway believing nothing more can be inferred, was 60.2% of annotated errors (for strong models, only about 10% of the errors on eldest-ancestor questions).
- 128K: one 72B model scored 99.89 on single retrieval but 43.92 on multi-needle reasoning; the best multi-needle reasoning score was 74.13. At 32K the best multi-needle reasoning score was below 50%.
- Realistic Wikipedia-based multi-needle reasoning collapsed on synthetic tasks (88.5 to 16.9 for a 7B model); the memorization explanation is not isolated from difficulty differences.

## Limits

- Synthetic. ATC contexts are short (about 9.6K tokens at most), so ATC tests dense reasoning more than length. The error taxonomy comes from partial manual annotation.
- Closed model sizes and versions unspecified; no max-token setting and no significance tests.

## See Also
- [[Evaluating Context]] — prerequisite-for
- [[Lost in the Middle]] — related
- [[LongBench]] — related
- [[Why Context Is Finite]] — related
