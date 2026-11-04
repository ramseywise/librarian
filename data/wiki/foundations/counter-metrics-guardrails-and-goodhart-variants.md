---
title: Counter-Metrics, Guardrails and Goodhart Variants
tags: [foundations, concept]
summary: A guardrail is a global must-not-break; a counter-metric is paired with one target to expose hitting it badly, and it must come from a later funnel step; four Goodhart variants each need a different defence.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--11-metric-trees.md
---

# Counter-Metrics, Guardrails and Goodhart Variants

## Two jobs
- **Guardrail:** a global must-not-break (delivery speed, refunds, page load). It belongs to no one's target, applies to every change, and a breach stops the work. In an experiment it needs its own non-inferiority test ([[OEC, Guardrails and North Star Metrics]]).
- **Counter-metric:** paired with one target and names how that target could be hit badly. Ask: if a team hit this number in the laziest way, what would you see? Acquisition pairs with the repeat rate of those customers; value per order pairs with orders per customer (a bigger minimum basket raises one, lowers the other). This is a working distinction, not a standard term.

## A counter-metric must be able to move
The obvious one for acquisition, cost per new customer, sits in the same funnel step and stays calm. In a worked case one channel's cost per new customer rose 4% (64.72 to 67.60) and the marginal extra customer cost 69.39, a steady scalable-looking channel. Its 90-day repeat rate fell from 17.7% to 13.6%, so cost per customer who repeats rose from 365.56 to 498.76. Across channels, total spend rose 66.4% and marketing per repeat customer rose 60.7% (66.08 to 106.20) against a north star up 3.5%. The guardrail (95th percentile lead time of 7 days both years) correctly stayed silent: nothing was operationally broken. Test whether the pair would have moved; downstream behaviour is the pairing that catches it.

## Goodhart variants (a measure that becomes a target stops measuring)
| Variant | Mechanism | Defence |
|---|---|---|
| Regressional | Proxy is goal plus noise; picking top scorers picks noise | Longer windows; allow for noise before crediting a winner |
| Extremal | Relationship holds in the normal range, breaks at extremes | Check the metric where you plan to operate |
| Causal | Proxy and goal share a cause; moving the proxy does not reach the goal | Test the causal edge first ([[Metric Tree Decomposition]]) |
| Adversarial | Someone with their own goal exploits the measure | Tighten the definition and audit |

## The adversarial case, simulated
Splitting the largest fifth of single-order customers' orders in two on the same day (1,848 orders) took repeat customers from 4,587 to 6,435, a 40% jump with revenue unchanged; value per order fell from 52.27 to 48.64, the counter-metric for this cheat. Counting distinct order days closes the gap (4,571 before and after, removing 16 real customers whose two orders fell on one day). A cheat you can imagine is a clause to write into the definition ([[Writing a Metric Definition Two Analysts Agree On]]). This was a simulation, not an observed event.

## Pitfalls
- A counter-metric from the same step as its target: calm while the business deteriorates.
- Reading a count north star without a pair: the count rises with scale.
- Emails-opened as a driver: the worry is causal (people who intend to buy open email); pair it with unsubscribe rate and repeat rate, and test with a holdout before making it a target.

## See Also
- [[Metric Tree Decomposition]] — prerequisite-for
- [[Dashboard Design: Paired Metrics and Context]] — related
- [[Incrementality Measurement Ladder]] — related
