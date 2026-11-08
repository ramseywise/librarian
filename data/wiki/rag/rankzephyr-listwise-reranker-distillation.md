---
title: RankZephyr Listwise Reranker Distillation
tags: [rag, pattern]
summary: A 7B open listwise reranker distilled in two stages from RankGPT teachers; reported to match or beat the GPT-4 teacher in-domain, trail it out of domain on strong first stages, and stay stable when the candidate order is shuffled.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pradeep-2023-rankzephyr.md
---

# RankZephyr Listwise Reranker Distillation

RankZephyr fine-tunes Zephyr-beta (a 7B model) to output a ranking such as "[4] > [2]" over a window of passages. The recipe has two stages: distillation from RankGPT3.5 orderings, using BM25 top-20 lists for 100K MS MARCO queries, then distillation from RankGPT4 orderings on a 5K-query subset. The authors estimate full GPT-4 data for 100K queries would cost over $10K. Training ran 3 epochs at batch 64 with a 5e-6 learning rate, taking roughly 40 hours (8 RTX A6000 GPUs). Training windows vary in size (up to 20 passages, three random subsets of each 20). Inference slides a 20-passage window with stride 10 across the top 100. All results are the paper's own (self-reported).

## Reported results

| Setup | Result (self-reported) |
|---|---|
| SPLADE++ ED top 100, TREC DL19 / DL20, nDCG@10 | 0.7816 / 0.8159 vs RankGPT4 0.7464 / 0.7076 (RankGPT4 averaged over 3 runs) |
| Same with 3 progressive passes | 0.7855 / 0.8255 |
| Same first stage, unseen sets DL22, NEWS, COVID | 0.6692, 0.5060, 0.8535 vs RankGPT4 0.7175, 0.5327, 0.8792 |
| BM25 top 100, unseen DL21 / DL22 / NEWS / COVID (3 passes) | RankZephyr: DL21 0.7114, DL22 0.5164, NEWS 0.5333, COVID 0.8377. RankGPT4: DL21 0.7073, DL22 0.5078, NEWS 0.5069, COVID 0.8471 |
| Shuffled SPLADE++ candidates, DL19 | RankGPT3.5 0.7504 to 0.6028; RankZephyr 0.7816 to 0.7670 |
| Output well-formed rate at window 10/5 | 38.74% when trained on fixed windows of 20; 100% with variable-size training |
| NovelEval-2306 (21 queries, single window) | nDCG@1 0.9286 vs 0.8571 for RankGPT4; nDCG@10 0.8934 vs 0.9045 |

The paper also reports a gain over the pointwise RankLLaMA-13B without human labels (DL19 0.7816 vs 0.7567), though those runs use different first stages. Reranking BM25 gives a 45% to 55% improvement across metrics against 7% to 20% for SPLADE++ ED. The authors explain the out-of-domain gap by the 4096-token training context and lower Judged@10, as guesses.

## Limits

- English passage ranking only (MS MARCO v1/v2, two BEIR sets, 21-query NovelEval). No latency or cost figures; progressive reranking costs three times the calls and this is not reported.
- Teacher and baselines are 2023 GPT models. The authors say listwise runs outside the TREC judgment pools make scores a lower bound.
- The RepLLaMA vs SPLADE++ reranking result is only partly explained.
- Internal inconsistency the extraction found: the text cites a "row (9)" of Table 1 that does not exist, probably row 8.

## See Also
- [[RAG Reranking]] — prerequisite-for
- [[Pairwise Ranking Prompting (PRP)]] — alternative-to
- [[Learning to Rank: Pointwise, Pairwise, Listwise and LambdaMART]] — prerequisite-for
