---
title: Clustering Control World Test
tags: [foundations, pattern]
summary: Before trusting behavioural clusters, run the pipeline on a control world drawn from one Gaussian: HDBSCAN's silhouette gate can pass it, UMAP-map silhouettes cannot tell structure from noise, and clusters must beat a one-line rule on a real decision.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--05-segmentation-and-rfm.md
---

# Clustering Control World Test

A synthetic study (400 businesses over three years, seed 42; none of it measures real-world performance) of whether behavioural cohorts found by clustering deserve trust. Three worlds: **planted** (five tight archetypes), **blurred** (same five at 2.5x spread), **control** (every customer from one Gaussian with the planted mean and covariance, so nothing to find). Finding planted archetypes is a weak test; watch the control. RFM rules scored ARI 0.004 on planted archetypes (no churn in the generator, so recency carries little); eight cash-flow features were used instead, log-scaled and standardised.

## HDBSCAN-then-k-means rule

The rule (HDBSCAN, fall back to k-means when silhouette is below 0.25 or noise above 50%; thresholds are design choices, not evidence) behaved as follows:
- Blurred: HDBSCAN labels everyone noise, fallback fires as designed.
- Rule picks HDBSCAN on planted though k-means recovers truth better (ARI 0.734 vs 0.480): silhouette leaves noise out, so discarding hard customers raises it.
- Noise is not junk: 40 of 54 manufacturers and 52 of 75 early-stage firms were noise because those archetypes are sparse. Noise means no dense neighbourhood at that minimum cluster size.
- The control **passes the gate**: two clusters at silhouette 0.310, the small one (16 customers) a feature artefact (largest receipt 61% of inflow). At minimum size 15 the same control returns all noise. Across five fresh controls HDBSCAN passed once; the other four fell back to two or three k-means clusters, so the rule always returns segments.

## UMAP is for looking

UMAP to 2-D then HDBSCAN: planted min size 10 gave 6 clusters, silhouette 0.857 on the map vs 0.348 on features, ARI 0.937 (best recovery). But control at min size 3 gave 48 clusters from one Gaussian, map silhouette 0.548 vs 0.073 on features. A silhouette on the map cannot separate the cases; score labels on the features. Neighbour preservation was poor (Jaccard-type measure 0.492 planted, 0.611 control). Keep UMAP for the picture.

## Stability and actionability

| World | Method | Subsample ARI | Previous-year ARI |
|---|---|---|---|
| Planted | k-means k=5 | 0.999 | 0.902 |
| Planted | HDBSCAN min 10 | 0.603 | 0.288 |
| Control | k-means k=2 | 0.906 | 0.453 |
| Control | HDBSCAN min 10 | 0.768 | 0.000 |

Subsample stability at large samples reflects whether the objective has one minimiser, not whether k is right (proved for centre-based and spectral methods); the previous-year test discriminates (0.902 with structure, 0.453 without). Actionability: rank customers by their cluster's prior-quarter burn rate and score AUC for next-quarter cash burn. Planted: k-means 0.692, rule clusters 0.678, RFM 0.526, the one line "costs exceed income" 0.545. Control: that one line 0.754 beats k-means 0.744 and rule clusters 0.578. A depth-3 tree reproduced planted k-means groups at 0.915 accuracy, making them applicable as rules.

## Checklist
Run the pipeline on a control; score clusters on features; report noise share; require a later period to agree; require beating a one-line rule on a real decision.

## See Also
- [[HDBSCAN with KMeans Fallback]] — extends
- [[Clustering Validation Against Named Baselines]] — related
- [[RFM Segmentation Validated on a Holdout]] — related
- [[Data Generating Process Simulation Check]] — related
