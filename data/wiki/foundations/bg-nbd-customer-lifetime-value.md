---
title: BG/NBD Customer Lifetime Value
tags: [foundations, concept]
summary: For non-contractual customers, BG/NBD needs only frequency, recency and observation time to estimate the chance a customer is still active and expected future orders; Gamma-Gamma adds order value, and LTV needs an explicit horizon and discount.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--09-marketing-measurement.md
---

# BG/NBD Customer Lifetime Value

Where there is no contract, a departed customer just goes quiet and no state is recorded, so a state-based model ([[Markov Chain Customer Value]]) cannot be used. BG/NBD needs three numbers per customer: repeat orders (frequency), weeks from first to last order (recency) and weeks observed (T).

## Model
While active a customer orders at a Poisson rate lambda; rates vary across customers as a gamma (r, alpha). After any order the customer leaves for good with probability p, which varies as a beta (a, b). On simulated data (3,000 customers, 11,929 orders; 28.6% with no repeat) maximum likelihood gave r 0.487, alpha 7.467, a 0.659, b 2.448 against true 0.5, 8.0, 0.7, 2.5. Probability alive averaged 0.633 (realised 0.638), AUC 0.920 and was calibrated by band (0.95 to 1.00 band: 0.999 truly alive; below 0.25: 0.100). Because the data come from the model's own generator this tests the code, not the idea.

The check that matters is a holdout: fit to June 2025, forecast 26.3 weeks: actual 1,841 orders, forecast 1,847 (+0.3%), customer-level correlation 0.717. On real data a published fit under-forecast the aggregate by about 4%, with individual correlation 0.626.

## Gamma-Gamma for order value
Assumes order value is independent of frequency (observed correlation 0.02). Each customer's mean is their own average shrunk toward the population's, more weight on their own as orders accumulate: for one-repeat customers the spread fell from 40.5 to 25.5. Library default priors misled on parameters (p 4.95, v about 30 vs true 6 and 25) while maximum likelihood gave 6.45 and 22.77; wide priors recovered 6.56, 3.93, 23.1. The implied mean order value survived (51.01 vs true 50). Compare defaults with maximum likelihood.

## LTV
Value = discounted expected orders x mean order value x margin. When a is below 1 the expected orders before dropout are infinite, so undiscounted orders never level off (repeat orders by year 1, 5, 25, 50: 1.96, 5.31, 11.74, 15.82) and a horizon and discount are required: 60 months at 1% a month gave 5.29 true orders versus 6.96 over 100 years. Posterior margin value was 173 (163 to 184) against a true 162; the interval covers sampling error only, so state a range (about 155 to 185). Horizon (136 at 36 months to 192 at 120) and discount (140 to 193) matter more than sampling error.

## CAC
CAC is spend divided by new customers; an LTV/CAC above 3 is folklore with no source. CAC credits a channel with every customer recorded, the attribution mistake: scaling by the share of credit truly caused cut paid social's ratio from 2.53 to 0.46 and left email near 3.9. Do not multiply LTV by new customers to get a channel's return.

## See Also
- [[Markov Chain Customer Value]] — alternative-to
- [[Survival Analysis for Customer Lifetimes]] — related
- [[Attribution Credit vs Causal Share]] — related
- [[Shifted Beta Geometric Retention Model]] — related
