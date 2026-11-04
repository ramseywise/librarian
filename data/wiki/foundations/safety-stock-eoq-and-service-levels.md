---
title: Safety Stock, EOQ and Service Levels
tags: [foundations, concept]
summary: EOQ balances order and holding cost on a flat cost curve; safety stock is z times the spread of lead-time demand including lead-time variance, and a flat reorder point misses its service target in seasons where demand runs higher.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--10-operations-and-supply-chain.md
---

# Safety Stock, EOQ and Service Levels

## EOQ
Economic order quantity = sqrt(2 x annual units x order cost / holding cost per unit-year). Estimates sat near the truth; moving from an assumed eight-weeks-of-demand order to EOQ saved 8.4% (cycle cost 10,767 to 9,860, 907 a year), nothing on furniture where eight weeks happened to be right. The cost curve is flat near the optimum: ordering 25% over the best costs 2.5% more, 50% over costs 8.3%, so a rounder pallet-sized number is fine.

## Safety stock
Reorder when stock falls to expected lead-time demand plus safety stock = z x sqrt(lead time x weekly demand variance + weekly mean^2 x lead-time variance). z comes from the service level, a decision, not an estimate. About 34.4% of safety stock was owed to lead-time noise; omitting it is the commonest shortcut and a lead-time spread from 20 orders can be halved by chance. Estimates mostly ran above the truth because sample weekly variance includes the seasonal swing. Pricing service: 80%, 90%, 95%, 98%, 99% needed 452, 688, 883, 1,102, 1,249 units at 2,476, 3,770, 4,839, 6,042, 6,844 a year; 95% to 99% costs another 2,005.

## Does the buffer deliver?
Cycle service is the share of order cycles with no stockout; fill rate is the share of units served. In 200 simulated years, off-season cycle service was 94.8% against a 95% target, but in season 79.4%, because the reorder point used a year-round mean while demand runs 60% higher; the all-year 91.4% hides this, and fill rate still looked healthy (94.7%) because late stockouts lose few units. Asking for 99% lifted in-season service only to about 89%. A higher z is a costly fix for a wrong mean: making the reorder point follow the season took in-season service from 80.0% to 94.7% for about 374 a year more holding, where raising z would cost over 2,000. Report service split by period and say which service measure is meant.

## See Also
- [[Newsvendor Critical Ratio]] — related
- [[Queue Staffing with Little's Law and Erlang C]] — related
- [[Weekly Seasonality Forecasting Methods]] — prerequisite-for
