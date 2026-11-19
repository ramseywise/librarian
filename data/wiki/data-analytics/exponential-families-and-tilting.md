---
title: Exponential Families and Tilting
tags: [data-analytics, probability-and-statistics, concept]
summary: An exponential family reweights a base density by exp(alpha times a sufficient statistic); its maximum likelihood estimate solves a moment-matching equation, and it is the structure beneath Poisson, binomial, multinomial and generalised linear models.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch05-parametric-models-exponential-families.md
---

# Exponential Families and Tilting

Chapter 5 of *Computer Age Statistical Inference* (Efron and Hastie) reviews the classic low-dimensional families and the common structure connecting them.

## Form

An exponential family takes a base density f0 and multiplies it by exp(alpha'y - psi(alpha)); alpha is the vector of natural parameters, y = t(x) holds the sufficient statistics and psi is the normaliser, a cumulant generating function (its first derivative is E{y} and its second is var{y}). Exponential tilting multiplies f0(x) by exp(alpha x) and renormalises. The expectation parameter beta = E_alpha{y} is one-to-one with alpha.

Example: the Poisson with mean 6 is a tilt of the Poisson with mean 12, with alpha = log(6/12) and psi(alpha) = lambda0 (e^alpha - 1) for base lambda0.

## Why it is useful

- Among all families, only exponential ones reduce an iid sample of any size n to a sufficient statistic ybar of fixed dimension p.
- The maximum likelihood estimate of the expectation parameter is ybar. The estimate of alpha solves E_alpha{y} = ybar, which usually needs numerics; the Poisson case has the closed form log y.
- Independent Poisson counts, once their sum is fixed, are multinomial; a multinomial whose total is itself Poisson turns back into Poisson counts. The chapter treats nonparametric analysis of discrete data as multinomial, as the bootstrap does.

## A designed family

Setup: gfr data of the book's Fig 2.1, a sufficient statistic of powers x to x^7 with f0 = 1, fitted by maximum likelihood through Lindsey's method (chapter 10). It fits the histogram closely where the normal (power 2) fits poorly. The authors advise building such specially designed families rather than staying with the tractable classics.

## Small comparisons

Binomial(30, 0.2) is already close to Poisson(6): both have mean 6, with standard deviations 2.19 and 2.45.

## Limits

- The chapter is a brief review that it says may be read lightly at first.
- Inverting psi-dot is usually not closed form; many derivations are deferred to endnotes or other chapters; GLMs come in chapter 8.

## See Also
- [[Generalised Linear Models and Deviance]] — extends
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Observed Fisher Information and Ancillary Conditioning]] — related
- [[Poisson Offsets and Overdispersion]] — related
