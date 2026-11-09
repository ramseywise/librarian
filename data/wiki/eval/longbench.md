---
title: "LongBench"
tags: [eval, reference]
summary: "LongBench is a bilingual multitask long-context benchmark of 21 datasets in 6 categories, with a length-balanced LongBench-E subset; it also found retrieval helped a 4k model but hurt long-context models (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-bai-2024-longbench.md
---

# LongBench

The benchmark covers 21 datasets in six categories (single-document QA, multi-document QA, summarization, few-shot learning, synthetic tasks, code), in English and Chinese, scored automatically. LongBench-E rebalances 13 English datasets into 0-4k, 4k-8k and 8k+ word bins. Eight models were run zero-shot (except few-shot tasks) with greedy decoding and middle truncation to the model maximum.

## Findings (self-reported)

- GPT-3.5-Turbo-16k had the best overall score of the eight. On LongBench-E its score fell 17% in relative terms between the 0-4k and 8k+ bins (51.5 to 42.4). Two 32k-extended 6-7B models were the most robust to length.
- Retrieval (best of three retrievers, 200x7 or 500x3 chunks) raised a Llama2-7B-chat-4k QA average from 19.9 to 24.0 but lowered GPT-3.5-Turbo-16k (40.7 to 39.9) and a 32k model (36.1 to 34.4); the 4k model with retrieval still trailed the long-context models without it. Smaller chunks with more retrieved chunks did better, and two of the three retrievers beat BM25.
- Summarization-based compression lowered GPT-3.5-Turbo-16k summarization scores except on the longest dataset, and Llama2-7B-chat-4k collapsed.
- A model with no context still scored high on Wikipedia-derived multi-document QA, indicating memorisation; the paper proposes the with-minus-without-context delta as an indicator.
- Synthetic tasks discriminated strongly between models; summarization and code did not.

## Limits

- Automatic metrics (ROUGE-L, F1) may underrate longer responses, and scores are coupled to instruction following (authors).
- Only eight models, mostly 7B open models plus one API model, all 2023, none above 32k. The retrieval and compression studies cover only QA and summarization tasks respectively; single run, no variance.
- Chinese lengths are in characters, not comparable to English words. PassageCount is near random for most models.

## See Also
- [[Evaluating Context]] — prerequisite-for
- [[NeedleBench]] — related
- [[Lost in the Middle]] — related
- [[Context Retrieval Strategies]] — related
