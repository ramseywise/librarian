---
title: "Latent Class Analysis for Mixed Data"
tags: [foundations, concept]
summary: "Latent class models each group as a recipe of per-column distributions fit by EM; BIC can answer no groups, but correlated columns inside a class break local independence and inflate the class count."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--05b-clustering-categorical-and-mixed-data.md
---

# Latent Class Analysis for Mixed Data

Every distance method minimises a distance. **Latent class analysis (LCA)** assumes instead that each customer has a hidden class, each class a mean per number and level shares per category, with columns independent within a class (**local independence**). Fit is expectation-maximisation, the loop of [[Expectation-Maximisation for Gaussian Mixtures]]: guess recipes; E step gives each customer's class probabilities; M step re-estimates recipes weighted by them; repeat from several random starts because it can stop at a poor optimum.

Being a likelihood model, class counts compare by BIC, including one class (no groups). BIC by k = 1..7 (lowest marked):

| World | BIC by k | Lowest |
|---|---|---|
| Both | 33095, 30979, 29779, 29254, 29416, 29586, 29746 | k=4 |
| Control (columns shuffled) | 33095, 33255, 33241, 33417, 33568, 33739, 33905 | k=1 |
| Correlated | 34071, 32525, 31642, 31266, 30939, 30799, 30632 | k=7, still falling |

It is the only method here where "no groups" is a possible answer. Do not over-read that: the control is built from normal numbers, the model's home ground, and a Gaussian mixture's BIC picked k=7 on shuffled skewed columns. With a within-group size factor the independence assumption breaks and BIC invents classes to explain the correlation. Check residual correlation, drop or merge columns. Simulation studies found BIC the best information criterion but state mixed continuous and categorical outcomes need more study; a review reports BIC underestimating classes below about 300 cases, with guidance of 300 to 500.

In the benchmark LCA topped three of four worlds (0.957 both, 0.659 categorical, 0.791 numeric) because the generator is its model; with correlation it scored 0.351 and FAMD led (0.448).

## See Also
- [[Clustering Categorical and Mixed Data]] — prerequisite-for
- [[Mixture Models and Label Switching]] — related
- [[Model Selection Criteria]] — related
- [[Validating Clusters Without Labels]] — related
