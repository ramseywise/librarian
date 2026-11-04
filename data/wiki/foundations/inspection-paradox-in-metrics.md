---
title: Inspection Paradox in Metrics
tags: [foundations, concept]
summary: "A metric sampled one way and quoted another differs: sampling by member weights each group by its size, so per-session averages exceed per-user averages and the two can move in opposite directions."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--01-descriptive-statistics-and-eda.md
---

# Inspection Paradox in Metrics

An average depends on whose perspective samples it. In the class-size version, a college with an average class of 24 finds its students report a larger figure, because large classes contain more students and so more students sit in them. Sampling by person weights each class by its size.

## Mechanism

If groups have sizes s_i, the mean per group is sum(s_i)/k, but the mean seen by a randomly chosen member is sum(s_i^2)/sum(s_i). The second is always at least the first and is much larger when one group is large.

A toy table makes it concrete: nine users with 20 sessions each and one with 500. The mean sessions per user is 68.0. A randomly chosen session belongs to a user with 372.9 sessions on average, because the heavy user owns most sessions.

## When it bites

The same arithmetic applies to any metric sampled one way and quoted another:

- Per-session and per-user metrics can move in opposite directions in an experiment, and which one you quote changes the story.
- Anything weighted by activity (latency per request against per user, error rate per event against per account) over-represents the heavy members.

State the denominator every time. The remedy is to decide the unit the decision is about (see the row-unit step of the [[EDA Audit Loop]]) and aggregate to it before summarising.

## See Also
- [[EDA Audit Loop]] — related (fixing what one row is)
- [[Delta Method for Ratio Metrics]] — related (per-session ratios need the user as independent unit)
- [[Pseudoreplication and Intraclass Correlation]] — related (sessions inside users are not independent rows)
