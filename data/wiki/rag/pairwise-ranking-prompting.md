---
title: Pairwise Ranking Prompting (PRP)
tags: [rag, pattern]
summary: Rerank by asking an LLM which of two passages is more relevant, then aggregating the pairwise wins; a 20B open model is reported to match much larger listwise rerankers, at the price of quadratic calls unless a sort or sliding window is used.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-qin-2023-large-language-models-effective-text.md
---

# Pairwise Ranking Prompting (PRP)

PRP is an unsupervised LLM reranking method. The prompt shows a query and two passages and asks for "Passage A" or "Passage B". The authors argue this is a simpler task than scoring one passage or ordering a whole list, so moderate open models can do it. All numbers below are the paper's (self-reported) and rerank the BM25 top 100 unless stated.

## Variants

- **PRP-Allpair** compares every pair in both orders. Each document earns one point for a win and half a point for a tie; a pair counts as a win only when both order-swapped prompts agree. Cost is O(N²) calls, and the output does not depend on input order.
- **PRP-Sorting** feeds the pairwise comparison to heapsort, O(N log N) calls.
- **PRP-Sliding-K** runs K backward passes of a bubble-sort style window, O(N) calls per pass. The paper reports one backward pass is enough for a strong NDCG@1 (57.58 NDCG@10 after one pass, 64.60 after three, 72.65 after ten, FLAN-UL2 20B, TREC-DL2019), while one forward pass gives 54.10.

The call pattern needs only generation (or log-likelihood scoring, which gave near-identical results: 72.42 vs 72.37 NDCG@10 for PRP-Allpair on FLAN-UL2, DL2019). About 0.02% of outputs were malformed (self-reported).

## Reported results

| Setup | Result (self-reported) |
|---|---|
| FLAN-UL2 20B, PRP-Sliding-10, TREC-DL2019 (43 queries) | NDCG@10 72.65 |
| Same, TREC-DL2020 (54 queries) | NDCG@10 70.46 |
| RankGPT with gpt-4 (figures taken from another paper) | 75.59 (DL2019), 70.56 (DL2020) |
| Seven BEIR sets, one prompt, PRP-Sliding-10 FLAN-UL2 | average NDCG@10 53.55 vs 53.34 for supervised RankT5 3B and 45.23 for BM25 |
| FLAN-T5-XL 3B, PRP-Allpair, DL2019 | NDCG@10 69.75 |
| text-bison, PRP-Allpair | 73.81 (DL19), 71.66 (DL20) |

On DL2019 with BM25 order inverted, RankGPT gpt-3.5-turbo falls from 65.80 to 32.77 NDCG@10, while PRP-Allpair goes from 72.42 to 72.40 (self-reported). The authors report that a listwise prompt run on FLAN-UL2 20B produced very few usable outputs.

## Limits

- The authors did not run GPT models; the GPT figures come from other papers.
- Every experiment reranks a BM25 top 100; no dense or hybrid first stage, and no latency or cost measurement.
- Pairwise judgments are not guaranteed transitive; the sorting theory is left open.
- Data leakage is not ruled out (FLAN includes an MS MARCO QA task), so the authors avoid the word zero-shot.
- Models and baselines date from 2023. Only relevance-style ranking was tested.
- The extraction notes that the paper's GPT-4 reference figure is from the RankGPT paper, and that a GPT-4 variant reranking gpt-3.5-turbo output was left out of BEIR as an ensemble.

## See Also
- [[RAG Reranking]] — prerequisite-for
- [[Learning to Rank: Pointwise, Pairwise, Listwise and LambdaMART]] — prerequisite-for
- [[RankZephyr Listwise Reranker Distillation]] — alternative-to
