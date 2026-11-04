---
title: Markov Chain Customer Value
tags: [foundations, concept]
summary: A monthly state-transition table gives customer lifetime value in one linear solve, but a single pooled chain averages unlike customers and undervalues them (about 19% low in simulation); check the chain on a holdout and use a mixture of chains.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--08-states-and-sequences.md
---

# Markov Chain Customer Value

Model each customer-month as one of a few states (new, active, lapsed, churned). A Markov chain is a table of one-step move probabilities, assuming the next state depends only on the current one. Estimate it by counting moves and dividing each row by its total.

## Mechanics
- Churned has probability 1 of staying: an absorbing state; the others are transient. With Q the transient-to-transient block, the fundamental matrix N = (I - Q)^-1 gives expected visits to each transient state, and its row sums give expected months before absorption. A worked check with known answers (a random walk on five corners, t = 3, 4, 3) passed before use.
- Value with a reward R per state and discount d: V = R + P V / (1 + d), so V = (I - P/(1 + d))^-1 R, one solve, no simulation. With zero discount the system is singular (the churned row is all zeros).

## Why the pooled chain fails
In simulated journeys (4,000 customers, 18 months) the pooled chain put a new customer at 430.73 against a true 513.29, and months to churn at 11.31 against 13.91. No customer behaves like the average row. Value is curved in retention (staying longer also means more time to keep staying), so the value of the average customer is less than the average value of customers. Splitting by channel barely helped (439.20) because each channel is itself a mix. Pooling also hid the meaning of a lapse: pooled value of a lapsed customer was 412.61, but across true types a lapsed customer was worth 5 to 1,259.

One chain per true type averaged 515.1 over twelve other seeds against a truth of 515.0; the pooled chain averaged 415.8, about 19% low. The single-dataset overshoot (560.28) was driven by a very low churn rate: an active-row churn of 0.017 against a true 0.02 moved the steady-type value by 14%. Treat any value driven by a very low churn rate as a range.

## Checking a chain without the truth
- Markov property: if it held, the previous state would not matter. Probability of staying active was 77% after two active months and 52% after returning from a lapse; within one true type it was flat (86%, 86%, 88%). History predicts only because it reveals customer type, the signature of a mixture.
- Stationarity by holdout: fitting on months 0-8, the pooled chain reached 17.8% still present at month 17 against 24.7% observed and 94.76 revenue (months 9-17) against 126.17. Later transitions look better (lapsed-to-churned 15% to 10%) only because the worst types have already left, not because anything improved.

## Mixture of Markov chains
Fitted by expectation-maximisation, it needs no labels: it estimates several chains and each customer's membership weights. On the holdout it got 131.31 revenue (within 4% of 126.17) and overshot survival at 28.0%. Fitted to all data it valued a new customer at 571.7 with four chains; over twelve seeds it averaged 504.7 against 515.0. The result depends on the number of chains: two gave 454.3, three to five gave 572 to 592, so report the range. See [[Expectation-Maximisation for Gaussian Mixtures]] for the fitting idea.

## Inferred states
From an order log "churned" is a rule (here, four silent months), not an event: 22.0% of customers it called churned ordered again. Shorter waits err more (33.5% at two months, 13.5% at six, 6.6% at nine). Every chain result assumes the state is final, so test how the rule moves the answer.

## See Also
- [[Optimal Matching and Journey Sequences]] — related
- [[Survival Analysis for Customer Lifetimes]] — alternative-to
- [[Cohort Retention Triangle]] — related
- [[Expectation-Maximisation for Gaussian Mixtures]] — related
