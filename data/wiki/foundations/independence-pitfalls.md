---
title: Independence Pitfalls
tags: [foundations, concept]
summary: "Pairwise independence does not give mutual independence, and two correlated events can be independent given a third; checking variables two at a time cannot prove there is no joint structure, and a shared cause creates correlation that vanishes when conditioned on."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--02-probability-foundations.md
---

# Independence Pitfalls

A and B are independent when P(A and B) = P(A) P(B), equivalently when knowing one leaves the other's probability unchanged. It is an assumption about the world and in analytics it is usually the one most at risk.

## Pairwise is not mutual

Take two fair coins A and B and let C be their exclusive-or. P(C=1 | A=1) = 0.5 and P(C=1 | B=1) = 0.5, so C looks independent of each alone, yet P(C=1 | A=1, B=1) = 0 and C is fully determined by the pair. Checking variables two at a time cannot prove there is no joint structure. Tests of the hashing schemes that assign users to experiments must check for exactly this kind of dependence between experiments.

## Correlated overall, independent given a cause

If 30% of users are "engaged" and open emails with probability 0.6 against 0.1 for others, then opening Monday's and Tuesday's emails correlate at +0.28 across all users but at +0.002 among engaged and 0.000 among others. This is the structure of confounding: a shared cause induces correlation that vanishes when you condition on it. Neither independent nor conditionally independent implies the other.

## Where independence breaks in analytics

- Rows in one group resemble each other: [[Pseudoreplication and Intraclass Correlation]].
- A customer's next state depends on the current one (a Markov chain).
- Repeating the same test is not new evidence in [[Bayes Rule and the Base Rate Fallacy]].

## See Also
- [[Pseudoreplication and Intraclass Correlation]] — related
- [[Bayes Rule and the Base Rate Fallacy]] — related (evidence accumulation assumes independence)
- [[Regression Covariate Adjustment]] — related (conditioning on a cause removes spurious correlation)
