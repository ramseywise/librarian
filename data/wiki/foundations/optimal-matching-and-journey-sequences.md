---
title: Optimal Matching and Journey Sequences
tags: [foundations, concept]
summary: Optimal matching measures how alike two customer journeys are as the cheapest edits turning one state string into another; clustering that distance describes journey shapes after the fact but cannot value or predict, and costs are a modelling choice.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--08-states-and-sequences.md
---

# Optimal Matching and Journey Sequences

Write each customer's monthly states as a string (N new, A active, L lapsed, C churned). The most common journey among 4,000 customers was one order and gone (978 customers); there were 1,466 distinct strings.

## Optimal matching (OM)
The distance between two sequences is the cheapest total cost of substitutions (swap a state) and indels (insert or delete one), found by dynamic programming (as in string alignment). With substitution cost 2 and indel 1 it reduces to a longest-common-subsequence distance: two strings sharing only the opening N differ in 17 months, distance 34. Despite the name it is unrelated to matching in causal inference; nobody is treated.

Costs are the contentious part. TRATE sets the swap cost to 2 - p(i|j) - p(j|i) so states that often follow each other are cheap; here costs ranged only 1.39 to 1.96, a summary of the same transition table (see [[Markov Chain Customer Value]]), not a deep fact. A hand implementation and a library agreed on 300 random pairs under both schemes.

## Clustering journey types
Hierarchical (Ward) clustering on the OM matrix, though Ward strictly assumes Euclidean distances. Silhouette peaked at k = 2 (0.680), flat across 4 to 6; four clusters were kept as a judgement because they read well. Adjusted Rand against the true types reached only about 0.40: a steady customer who leaves early produces the same string as a drifter (51 sit in the one-and-done cluster). The medoid, the most central real journey, is the shortest report of a cluster: one order and gone; a few on-off months then gone; on and off throughout; active throughout. Cost choice moved the result a little (ARI 0.399 TRATE indel 1, 0.364 indel 2, 0.352 constant) and the best-separated option was not the one closest to the truth.

## Description, not prediction
Feeding the clusters back into chains gave a mixture value of 901.14 against a truth of 513.29, and 3,935.66 for the best cluster against a true steady value of 1,485.93. The clusters were formed on the outcome (they contain the customers who happened to stay), so they cannot value it; a mixture model weighs evidence per customer without sorting on the result. Hazard models address the generating process; sequence analysis is descriptive and exploratory, a complement. Description fits decisions about what to name or look at (an index plot of one row per customer); it is the wrong tool for "what is a new customer worth" or "what if we changed something".

## Pitfalls
- Clustering on the outcome then predicting it.
- Reading a silhouette as the count of real types.
- Treating substitution costs as discovered facts: show how clusters move when they change.

## See Also
- [[Markov Chain Customer Value]] — related
- [[Clustering Validation Against Named Baselines]] — related
- [[Survival Analysis for Customer Lifetimes]] — alternative-to
