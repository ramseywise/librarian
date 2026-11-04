---
title: "Ranking Metrics as the Confusion Table Along a List"
tags: [foundations, concept]
summary: "Precision and recall at k are the confusion table with k as the threshold; MRR and NDCG summarise across cut-offs and can disagree, so pick by whether one good answer or several are needed."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--11-choosing-a-metric.md
---

# Ranking Metrics as the Confusion Table Along a List

Precision and recall at k are the confusion table at one cut-off. One simulated query (100 documents, 5 relevant at positions 1, 2, 8, 10, 50):

| k | TP | FP | FN | Precision | Recall | Accuracy |
|---|---|---|---|---|---|---|
| 1 | 1 | 0 | 4 | 1.00 | 0.2 | 0.96 |
| 5 | 2 | 3 | 3 | 0.40 | 0.4 | 0.94 |
| 10 | 4 | 6 | 1 | 0.40 | 0.8 | 0.93 |
| 20 | 4 | 16 | 1 | 0.20 | 0.8 | 0.83 |
| 100 | 5 | 95 | 0 | 0.05 | 1.0 | 0.05 |

Accuracy is 0.96 at k=1 though four of five relevant documents are missed: true negatives are the rest of the corpus, so a system maximising accuracy looks good by calling everything non-relevant. Any metric true negatives can inflate is suspect.

- **MRR** averages 1/rank of the first relevant result and ignores everything after.
- **NDCG** sums gain per position discounted by depth and divides by the ideal ordering; graded relevance. Discount conventions differ (log base b of rank vs log2(rank+1) in most libraries), so figures across tools may not agree.

Two rankers built to differ (500 queries, 100 documents, 5 relevant): a "finder" lifting one relevant document by 4 SDs scored MRR 0.952, NDCG@10 0.375, recall@10 0.272; a "broad" ranker lifting all five by 1.7 scored 0.816, 0.588, 0.614. The lifts were constructed to disagree, so this shows metrics can diverge, not how often. If one good answer ends the search, MRR measures that; if the answer needs several sources, NDCG and recall do. Compare with the popularity baseline.

## The same table in four jobs

| | Credit model | Retrieval | LLM judge | Guardrail |
|---|---|---|---|---|
| Positive | Will default | Chunk relevant | Output passes | Input is an attack |
| False positive | Good customer declined | Irrelevant chunk spends context | Judge passes a bad output | Benign message blocked |
| False negative | Defaulter approved | Relevant chunk missed | Judge fails a good output | Attack gets through |

State the positive class first (the judge row flips it), set the threshold from error costs.

## See Also
- [[Choosing a Metric From the Cost of Errors]] — related
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Precision-Recall vs ROC and Average Precision]] — related
