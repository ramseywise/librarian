---
title: Sub-Gaussian Tail Bounds and Confidence Radii
tags: [data-analytics, probability-and-statistics, concept]
summary: "A sigma-subgaussian variable has an exponentially small tail, which turns the sample mean into a finite-time confidence bound of radius sqrt(2 sigma^2 log(1/delta)/n); this is the bound a UCB index is built from, and the CLT cannot replace it."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch05-concentration-measure.md
---

# Sub-Gaussian Tail Bounds and Confidence Radii

Lattimore and Szepesvari's chapter 5 asks how quickly an average of independent identically distributed rewards approaches the true mean, in a statement that holds at a finite sample size.

## The definition and the tail bound

A random variable X is called sigma-subgaussian when, for all real lambda, E[exp(lambda X)] <= exp(lambda^2 sigma^2 / 2). A non-centred variable is called subgaussian when X minus its mean is. The tail bound comes from the Cramer-Chernoff method: apply Markov's inequality to exp(lambda X), then choose lambda = eps / sigma^2. For any eps >= 0:

```text
P(X >= eps) <= exp(-eps^2 / (2 sigma^2))
```

The left tail is symmetric, so a union bound gives a two-sided factor of 2. Closure properties (stated, proof left to an exercise): a sigma-subgaussian variable has mean 0 and variance at most sigma^2; scaling by c gives |c| sigma; adding two independent variables, one sigma1- and one sigma2-subgaussian, gives sqrt(sigma1^2 + sigma2^2)-subgaussian, while without independence the sum is only (sigma1 + sigma2)-subgaussian.

## From tail to confidence bound

If the X_i minus mu are independent and sigma-subgaussian (identical distribution is not needed), the sample mean minus mu is sigma/sqrt(n)-subgaussian, so P(mu_hat >= mu + eps) <= exp(-n eps^2 / (2 sigma^2)). Stated as a confidence bound, with probability at least 1 - delta:

```text
mu <= mu_hat + sqrt(2 sigma^2 log(1/delta) / n)
```

and symmetrically for the lower side (a union bound covers both sides). This is the form that underlies the index in [[Upper Confidence Bound Bandit Algorithms]]. The same chapter gives, with the proof left as an exercise, a maximum-of-subgaussians bound: for n possibly dependent sigma-subgaussian variables, E[max] <= sqrt(2 sigma^2 log n).

## Which variables qualify

- N(0, sigma^2) is sigma-subgaussian.
- A mean-zero variable with |X| <= B almost surely is B-subgaussian; one supported on [a, b] is (b - a)/2-subgaussian (Hoeffding's lemma gives M_X(lambda) <= exp(lambda^2 (b-a)^2 / 8)).
- Bernoulli is 1/2-subgaussian for every p; the exact constant is sqrt((1 - 2p) / (2 ln((1-p)/p))) (attributed to Kearns and Saul).
- No sigma works for an exponential variable, and a chi-squared variable is outside the class too; the chapter points to subexponential families for those.

## Other inequalities in the chapter

- Chebyshev needs only a finite mean and variance: P(|mu_hat - mu| >= eps) <= sigma^2 / (n eps^2), a polynomial rather than exponential tail.
- Hoeffding's inequality (independent, bounded, not necessarily identical) is stated without proof. Bennett and Bernstein are stated for when the variance is small; the chapter advises Hoeffding for bounded rewards and Bernstein or Bennett when the variance is small.
- A large-deviation form, for mean-zero identically distributed independent X: (1/n) log P(mu_hat_n >= eps) <= -psi*(eps), where psi* is the Legendre transform of the log moment-generating function; for N(0, sigma^2) it equals eps^2 / (2 sigma^2).
- The Gaussian tail obtained from the CLT improves the subgaussian bound slightly, by a factor of 1/sqrt(n eps^2) (approximate, since it uses the CLT limit).

## Why not the CLT

The authors caution against the n >= 30 rule of thumb: Bernoulli samples with p = 1/n approach Poisson(1), not a Gaussian. Because the CLT only describes the limit, they say it cannot guide bandit-algorithm design; a finite-sample guarantee needs an assumption such as subgaussianity. For a Bernoulli arm, the matching exponential tail in relative entropy is on the UCB page.

## Limits

- The chapter proves only the tail bound and the sample-mean corollary; Chebyshev, the closure lemma, Hoeffding, Bennett and Bernstein are left to the reader as exercises.
- The subgaussian bound is not tight for Gaussians, and the converse constant (a centred variable with P(|X| >= eps) <= 2 exp(-eps^2/2) is sqrt(5)-subgaussian) is admitted loose.
- Covers light-tailed rewards only.
- The bounds assume independent samples; samples chosen adaptively by a bandit policy need martingale versions, which the chapter defers to chapter 20.
- No bound is applied to a bandit algorithm in this chapter.

## See Also
- [[Upper Confidence Bound Bandit Algorithms]] — extends (the index is this confidence bound)
- [[Explore-Then-Commit Bandit Policy]] — extends (its regret proof uses the sample-mean bound)
- [[Expectation and Variance Rules]] — prerequisite-for
- [[Confidence Interval Coverage and Wilson]] — related (a contrasting, coverage-based interval)
