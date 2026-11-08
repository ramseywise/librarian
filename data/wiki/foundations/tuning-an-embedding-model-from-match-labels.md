---
title: "Tuning an Embedding Model from Match Labels"
tags: [foundations, pattern]
summary: "A frozen pretrained encoder scored below a character n-gram baseline on code-heavy records; about 1,000 labelled pairs with in-batch softmax lifted recall@10 from 0.134 to 0.908, but a held-out product family dropped it to 0.715, so measure frozen, tuned and held-out against a character baseline."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-science--05-time-series-and-recommenders--notes--05-learning-a-similarity-function.md
---

# Tuning an Embedding Model from Match Labels

Setup: a small pretrained sentence encoder (about 90 MB), short part descriptions that are mostly codes, grades and dimensions, 400 training steps, batch 32, learning rate 2e-5, temperature 0.05 (about 35 seconds a run), catalogues of about 1,700 records, recall@10 over all other records (denominator capped at 10), means over three seeds. Tuning uses in-batch softmax without a logQ term (records are not drawn by popularity; see [[Two-Tower Retrieval with logQ Correction]]).

## Frozen against tuned

| Setup | Pairs | Recall@10 | Look-alikes in top 10 |
|---|---:|---:|---:|
| Character TF-IDF, no training | 0 | 0.456 | 0.089 |
| Frozen pretrained | 0 | 0.134 | 0.030 |
| Tuned | 100 | 0.799 | 0.371 |
| Tuned | 300 | 0.881 | 0.476 |
| Tuned | 1000 | 0.908 | 0.494 |
| Tuned | 3000 | 0.912 | 0.501 |

Frozen was the worst row: the encoder saw English sentences, not codes. Do not read 13.4% to 90.8% as what tuning does in general; it is the gap on text where the frozen model has least to work with. Published gains range from none to large (one vendor measurement moved recall@10 from 0.293 to 0.552 on one set and 0.849 to 0.884 on another, and an untuned larger model at 0.95 beat a tuned one at 0.884). So measure frozen against a character baseline on your own text; a frozen score below the baseline signals the encoder misses what the text carries, while above it settles nothing.

## Building batches from labels

Close the labelled pairs into groups (A-B and B-C imply A-C), then build each batch with at most one pair per known group so no known match is a negative. This removes only *known* matches: an unlabelled match in the batch is a **false negative**, reducible not removable. Split straight after closing labels, before building batches, and hold out whole specs ([[Entity-Disjoint Splits and Group Scores for Pair Matchers]]).

## How many pairs

Recall gains 0.082 from 100 to 300 pairs, 0.027 from 300 to 1,000, 0.004 from 1,000 to 3,000 (inside seed noise of about 0.01). That curve is generated data; a quoted "1,000 to 5,000" figure traced to a vendor blog with no study. In entity-matching evidence a contrastive encoder's F1 lead over the best baseline was 8.84 points at about 3,000 pairs and 0.84 at about 68,000: gains are largest where labels are scarce. Train at 100, 300 and 1,000 and read your own curve; when the last step gains less than seed noise, more labels of the same kind will not pay.

## A family it never saw

Removing one family from training and scoring only it: recall 0.917 trained on all families, 0.715 without that family (bearing 0.861 to 0.578, bolt 0.947 to 0.782, o-ring 0.944 to 0.784), still above TF-IDF on every family. Generator families share code format and vendor names, so a new real product line with new vocabulary may fall further (untested). On a real benchmark a contrastive encoder had F1 82.15 on seen products and 53.31 on unseen, while cross-encoders held 67.94 and 69.75. Report a held-out-family score next to the headline.

## What tuning does not replace

- The attribute check: after tuning about half the top 10 are look-alikes ([[Similar vs Interchangeable in Matching]]).
- A reranker, until compared: label-free tuning narrowed but did not close the gap to a cross-encoder (45.2 frozen, 51.5 tuned without labels, 54.7 for a lexical retriever plus cross-encoder, nDCG@10), and cross-encoders and bi-encoders are similar when train and test data are similar, differing when they differ. Labelled tuning against a reranker was not tested here.
- Loss choice matters less than the papers suggest: under a fair protocol on vision data, newer losses beat a 2006 contrastive loss marginally (CUB mAP@R 26.70 best against 26.53, triplet 23.69, pretrained 14.21). Start with in-batch softmax and spend time on labels and the split.

Temperature acts as soft mining: recall 0.913 at 0.05, 0.848 at 0.20, 0.776 at 1.00.

## See Also
- [[Hard-Negative Mining and Measuring What It Fixes]] — extends
- [[Entity-Disjoint Splits and Group Scores for Pair Matchers]] — prerequisite-for
- [[Similar vs Interchangeable in Matching]] — related
- [[Two-Tower Retrieval with logQ Correction]] — prerequisite-for
- [[GritLM (Generative Representational Instruction Tuning)]] — related (one model trained for both embedding and generation)
- [[Llama2Vec Unsupervised LLM Adaptation for Dense Retrieval]] — related (unsupervised adaptation of a decoder LLM into an embedder)
- [[Syntriever Synthetic Retriever Training]] — alternative-to (synthetic data from an LLM instead of match labels)
