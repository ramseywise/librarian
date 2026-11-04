---
title: "Rare-Class Benchmark Quotas and Reweighting"
tags: [foundations, pattern]
summary: "A production-mix benchmark learns almost nothing about a rare class; equal quotas fix the spread but bias the headline unless each class's accuracy is reweighted back to its production share."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--11-choosing-a-metric.md
---

# Rare-Class Benchmark Quotas and Reweighting

With 1,000 labelled rows and a class at 0.5% of traffic, drawing in the production mix yields about 5 rows of that class. Simulation (20,000 draws, a made-up five-class mix with known per-class accuracy: 70% at 97%, 20% at 92%, 8% at 85%, 1.5% at 70%, 0.5% at 50%; true production accuracy 0.944):

| Class (share) | Rows, production mix | SD of accuracy | Rows, equal quota | SD of accuracy |
|---|---|---|---|---|
| Largest (70%) | 699.844 | 0.006 | 200 | 0.012 |
| 20% | 200.066 | 0.019 | 200 | 0.019 |
| 8% | 80.087 | 0.040 | 200 | 0.025 |
| 1.5% | 14.990 | 0.123 | 200 | 0.032 |
| Rarest (0.5%) | 5.012 | 0.253 | 200 | 0.035 |

Headline accuracy: production mix 0.9440 (SD 0.0072); equal quota unweighted 0.7880 (bias -0.156) because it counts each class as a fifth of traffic; equal quota reweighted 0.9439 (SD 0.0094). So the quota cut the rare class's SD about sevenfold at a small cost to the headline's precision.

**Reweight:** measure accuracy per class, multiply by production share, sum (0.70 x 0.97 + 0.20 x 0.92 + 0.08 x 0.85 + 0.015 x 0.70 + 0.005 x 0.50 = 0.944). Report each class's accuracy alone plus the reweighted headline. Equal quotas are not special: spend rows where a wrong answer costs most. When the mix moves, reweight with new shares and no new labels, provided per-class accuracy holds.

## Sizing a quota

Set the half-width 1.96 x sqrt(p(1-p)/n) equal to margin m: n = 1.96 squared x p(1-p) / m squared. Rows needed: largest class (p 0.97) 12, 45, 125 for margins of 10, 5, 3 points; rarest class (p 0.5) 97, 385, 1,068. p(1-p) peaks at 0.5, so plan with 0.5 absent an estimate. The Wald interval fails near 0 and 1 (twelve rows at 97% usually show no errors). A 200-row quota gives the rarest class about +/-7 points; random draws would need about 20,000 rows for ~100 of them. With zero errors in n rows, the rule of three bounds the error rate near 3/n.

## See Also
- [[Choosing a Metric From the Cost of Errors]] — related
- [[Imbalance Remedies Versus a Tuned Threshold]] — related
- [[Train, Validation and Test Discipline]] — related
