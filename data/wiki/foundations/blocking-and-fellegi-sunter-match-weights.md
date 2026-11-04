---
title: "Blocking and Fellegi-Sunter Match Weights"
tags: [foundations, pattern]
summary: "Entity matching first cuts candidate pairs with cheap blocking keys, whose recall caps everything downstream, then scores each pair by summed log(m/u) evidence with a three-way link, review, reject decision."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--04-entity-matching-and-learning-to-rank.md
---

# Blocking and Fellegi-Sunter Match Weights

**Entity matching** decides that records from different sources describe the same real thing when no shared key says so (record linkage, deduplication). Worked example: a generated ledger of 4,000 invoices and 4,343 bank lines (17,372,000 pairs), true links 4,268, where some payments are batches paying several invoices, some are part payments, about one line in ten has no invoice, a processor hides the supplier name on 15% of lines and a reference appears on 45% of those that can carry one.

## Blocking

Compare only pairs sharing some cheap property; the surviving pairs are a **block**. Pairs outside it are implicit non-links decided without looking, so blocking raises one error (missed matches) in exchange for fewer comparisons. Read reduction ratio only beside recall.

| Block | Pairs | Reduction | Recall |
|---|---:|---:|---:|
| Date window only | 3,614,233 | 0.7920 | 1.0000 |
| window + amount within 3% | 68,305 | 0.9961 | 0.7498 |
| window + name | 283,789 | 0.9837 | 0.8421 |
| window + reference | 1,755 | 0.9999 | 0.3964 |
| window + amount or name | 340,786 | 0.9804 | 0.9634 |
| window + amount, name or reference | 340,885 | 0.9804 | 0.9733 |

No single key is enough: amount misses part payments and batches, name misses the hidden processor, reference is near perfect but usually absent. The union keeps 97.3% of true links at about 78 candidates per line. A rare specific key (reference) adds almost no pairs and a point of recall. Going from 44 to 78 candidates per line bought 0.33 points of recall, from 157 to 250 nothing: widening thresholds cannot reach links that need a new kind of key. Recall is uneven by kind of payment (batch 0.8707, part 0.9235, single 0.9981), and that per-kind recall is the ceiling on every later step. A date window encoding a real process has a readable threshold: 30 days gave recall 0.3397, 60 days 0.7795, 90 days 0.9663, 120 days 0.9733, because payment terms were 14 to 60 days plus lateness, counted from issue date.

## Fellegi-Sunter weights

Describe each pair by a comparison vector of field agreement levels. For each level, m = P(level | match) and u = P(level | non-match). Under conditional independence the evidence adds on a log scale: weight = sum over fields of log2(m/u), in bits, so each bit doubles the odds. Rare agreements weigh more, disagreement is negative, a missing value carries zero. Learned weights on the ledger: amount exact 5.52 bits, within 3% -0.59, far -1.79; reference all digits 11.27, one digit off 8.95, missing 0.0, other -12.04; date near due 1.16, later -2.54, far -5.87. A reference one digit off still carries nearly 9 bits (odds times about 500), which an exact join would throw away. Weights can also be estimated from file frequencies with no labels.

Caution: a weak name match scored -3.9, worse than none (-0.36), because m and u describe pairs *given the block*, which already selected on the same fields.

## Link, review, reject

Sort by weight and use two thresholds: above the upper, link; below the lower, non-link; between, possible link for a person. For fixed error tolerances the optimal rule minimises the middle region, since manual review is the expensive part. On the ledger (link at 9.25 bits, reject below -2.00): 305 pairs linked at precision 1.000, 6,864 to review of which 7.3% true, 57,176 rejected losing 17 of 824 true pairs. Independent per-pair weights know nothing about the other candidates on the line, which ranking fixes ([[Learning to Rank: Pointwise, Pairwise, Listwise and LambdaMART]]). Where to stand on the review curve is a pricing decision ([[Calibrated Score, Deterministic Decision Rule]]).

A language-model pair scorer (serialise each record, classify the pair as a cross-encoder) helps most on dirty text (F1 from 53.8 to 85.69 on the hardest dirty benchmark), but was trained on general English, may fit numeric-heavy matching poorly, and returns only yes or no per pair.

## See Also
- [[Learning to Rank: Pointwise, Pairwise, Listwise and LambdaMART]] — extends
- [[Match Errors Are Not Classification Errors]] — extends
- [[Three-Level Duplicate Classification]] — instance-of (a deterministic three-route variant)
- [[Bayes Rule and the Base Rate Fallacy]] — prerequisite-for (the odds form behind the weights)
