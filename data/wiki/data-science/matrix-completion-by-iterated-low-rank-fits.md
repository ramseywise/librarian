---
title: Matrix Completion by Iterated Low-Rank Fits
tags: [data-science, concept]
summary: "Matrix completion imputes missing entries from a low-rank principal-component fit to the observed ones; ISLP's Algorithm 12.1 does this on USArrests with M = 1 and recovers hidden values with a correlation of 0.63, short of the 0.79 an oracle gets from the complete data."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-islp-ch12-unsupervised-learning.md
---

# Matrix Completion by Iterated Low-Rank Fits

ISLP's Chapter 12 uses principal components for imputation as well as for visualisation. **Matrix completion** imputes missing values through a low-rank (principal component) fit to the observed entries; the book's Algorithm 12.1 corresponds to what Mazumder et al. (2010) name Hard-Impute. A principal component has **loadings** phi_j1, its coefficients, and **scores** z_i1, the value of the component for observation i. The **proportion of variance explained** (PVE) of the mth component is its variance over the total variance. Fitting M components gives each entry the approximation x_ij = z_i1 phi_j1 + ... for M terms; with M = 1 it is z_i1 phi_j1.

## The USArrests experiment

On standardised USArrests (50 states, 4 variables) the first component explains 62.0% of the variance and the second 24.7%. The book hides one of the four values for each of 20 randomly chosen states, so 20 of 200 entries (10%) are missing, and runs the algorithm with M = 1. Over 100 random runs the correlation between imputed and true values is 0.63 with a standard deviation of 0.11. A gold standard that applies the first component of the complete data gives 0.79 (sd 0.08) on the same entries, which is not attainable with real missing data. In the lab (seed 15, thresh 1e-7, `np.linalg.svd`) the iteration converged in 8 steps, the mean squared error on observed entries was 0.381, and the correlation was 0.711 for that one run.

The book states the other rules as guidance: choose M by leaving out extra entries at random and picking the M that recovers them best, like a validation set; the method is advised only when values are missing at random. The book's recommender example is a ratings matrix of 480,189 customers by 17,770 movies, about 99% of it missing, with about 200 movies seen per customer (reported).

## Limits

- The method presumes values are missing at random, so missingness that carries information undermines it, and Algorithm 12.1 is not guaranteed to reach a global optimum.
- USArrests has only 4 variables, which the authors call the low end for the method, and the lab number is a single run.
- The number of components for exploratory work is chosen by eye on a scree plot, with no objective rule.

## See Also
- [[PCA, NMF and Low-Rank Factorisation]] — prerequisite-for
- [[Pandas Missing Data Decisions]] — related
