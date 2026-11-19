---
title: Inspection Paradox in Metrics
tags: [data-analytics, probability-and-statistics, concept]
summary: "A metric sampled one way and quoted another differs: sampling by member weights each group by its size, so per-session averages exceed per-user averages and the two can move in opposite directions."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--01-descriptive-statistics-and-eda.md
  - data/raw/papers/2026-11-08-think-bayes-ch08-observer-bias.md
  - data/raw/papers/2026-11-08-think-stats-ch03-cumulative-distribution-functions.md
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

## The same bias in wait times

Downey's *Think Bayes* (ch. 8) calls this observer bias: a passenger turning up at a random moment lands in long gaps more often, in proportion to their length. If 5- and 10-minute gaps are equally common, the true mean gap is 7.5 minutes while the average experienced is 8.33. On Red Line data (southbound Kendall Square, 4 to 6 pm, five weekdays) the mean gap was 7.8 minutes and the observed one 8.8, about 13% higher. His remedy: regard the observations as length-biased and correct for that before modelling, by weighting each value by itself and renormalising. See [[Predicting from a Posterior as a Mixture]] for the wait-time prediction built on it.

## Relay-race version

Downey's *Think Stats* (ch. 3) gives a second case: a runner watching a relay sees mostly the runners who pass or are passed, and the chance of that is proportional to the speed difference, so the speeds the observer records look biased and apparently two-humped. The author's setting is a 209-mile staggered-start relay; an exercise uses James Joyce Ramble 10K speeds with an observer at 7.5 MPH. His correction, for size-biased samples and observer effects alike, is to transform the observed PMF (his UnbiasPmf). The chapter states the relay effect as a claim and gives no numeric result for it.

## Limits

- Wait-time example (Think Bayes ch. 8): the arrival rate is assumed constant across days with no special events, the frequency of long delays comes from memory, not data, and the distribution of gaps is assumed known.
- Think Stats ch. 3 is exercise-driven, leaving most numeric answers out; its code is Python 2 era, and its birth-weight and relay results are claims without numbers.

## See Also
- [[EDA Audit Loop]] — related (fixing what one row is)
- [[Delta Method for Ratio Metrics]] — related (per-session ratios need the user as independent unit)
- [[Pseudoreplication and Intraclass Correlation]] — related (sessions inside users are not independent rows)
