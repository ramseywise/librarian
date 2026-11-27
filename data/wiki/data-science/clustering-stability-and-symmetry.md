---
title: "Clustering Stability and Symmetry"
tags: [data-science, classical-ml, concept]
summary: "In the large-sample limit, a centre-based or spectral clustering is stable when the objective has a unique best solution and unstable when a symmetry of the data swaps equally good ones, so stability under resampling does not tell you whether k is right."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-ben-david-2006-sober-look-clustering-stability.md
---

# Clustering Stability and Symmetry

Ben-David, von Luxburg and Pal ask what stability under resampling measures when it is used to pick the number of clusters k. Their hypothesis is that for large samples it reflects whether the clustering objective has a unique minimiser, not whether k is right. The paper is theoretical: its support is theorems and hand-built examples, with no experiments on real data.

## Definition

Stability of an algorithm A on a distribution P is the limit superior, over sample size m, of the expected clustering distance between the clusterings A produces on two independent samples of size m. A is stable on P when that is zero. One distance used is the pair-counting (Hamming) distance: the probability that two random points are together in one clustering and apart in the other. The results are asymptotic, so finite-sample variance instability is set aside.

## What decides stability

- **Unique minimiser implies stable (Theorem 10).** If P has a unique risk minimiser, any algorithm that exactly minimises empirical risk and converges in probability to the optimum is stable on P. This covers k-means and k-medians.
- **Symmetry implies unstable (Theorem 15).** If the risk and distance are ODD (invariant under every symmetry that preserves P), P has n distinct minimisers, and some symmetry g that leaves P unchanged displaces each minimiser, then such an algorithm is unstable on P.
- **Conjecture 11 is unproved.** It says multiple minimisers alone imply instability. The authors know no counterexample but prove only the symmetry case.
- **Spectral clustering.** Two spectral variants get parallel results. Normalised spectral clustering (a Shi-Malik relaxation followed by k-means on the embedding) is stable when its limiting clustering is unique (Theorem 16, proof only sketched). The kernel-k-means relaxation is stable when that objective has one optimiser (Theorem 17). A graph automorphism repeats an eigenvalue and so leaves the eigenvectors ambiguous: a square of four vertices, whose Laplacian eigenvalues are 0, 1, 1 and 2, admits two symmetric clusterings.

## Worked examples

- Uniform on [0,1]: for any k, both k-means and k-medians have a single minimiser, the equal-width split, so both stay stable whatever k is.
- Uniform on [0,4] together with [12,16], k = 3: the optimal centres can be the set (2,13,15) or the set (1,3,14), mirror images under g(x) = 16 - x, so both algorithms are unstable. Shifting weight so the first interval holds a little under half the mass leaves one optimal triple and both become stable at the same k.

## Consequences

What sets stability is the symmetry of the distribution, a property independent of k, so passing a stability check says nothing about whether k is right. A constant clustering, such as a single cluster, is stable on any distribution. The authors treat success of stability-based selection of k as an exception, not the rule. They believe, without proof, that real data are seldom perfectly symmetric; a finite sample of symmetric data is nearly symmetric, so a small perturbation picks one of the tied solutions.

## Limits

- Asymptotic only; the finite-sample, variance kind of instability is not analysed.
- The theorems assume the algorithm exactly minimises the empirical risk, so k-means local minima are not covered.
- Conjecture 11 is unproved; Theorem 16 and the spectral symmetry argument are sketches.
- No real-data experiments; the belief that real data are seldom symmetric is not tested.
- Only centre-based and spectral clustering are covered; what makes stability work on real data is left open.
- The authors say the results do not contradict stability results in supervised learning.

## See Also
- [[Validating Clusters Without Labels]] — related (a stable clustering can still recover nothing, shown there on a shuffled control)
- [[Choosing k and Naming Clusters Honestly]] — related (reseeding agreement as one criterion for k)
- [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]] — prerequisite-for
