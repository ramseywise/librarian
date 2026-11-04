---
title: Ratio Metrics and the Denominator Trap
tags: [foundations, concept]
summary: "When treatment can change a ratio's denominator, the ratio can fall while the numerator and the business improve; never report a ratio without its parts, choose ratio of averages or average of ratios deliberately, and take the standard error with the user as the independent unit."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--02-metrics-and-kpi-design.md
---

# Ratio Metrics and the Denominator Trap

When the denominator responds to the treatment, a ratio metric can move for reasons unrelated to its numerator. House rule: never report a ratio without its numerator and denominator.

## Examples

- Moving a page module up cut click-through per user by 40%, yet clicks rose 74%, impressions 200%, page-level click-through stayed flat and revenue rose: the denominator grew faster.
- A new-tab feature seemed to slow a page by 8.32%; it had reduced loads by 7.8%, and the vanished loads were fast cache reloads, so the remaining average was slower while no page was.
- In a simulated checkout test with a reminder email, conversion was +13.9% and revenue per user +10.3%, but sessions per user rose 20.2% and revenue per session fell 8.2% (conversion per session -5.2%) because the email brought low-intent extra visits. Someone reading session columns calls it a failure; both readings are arithmetically right, so the decision rests on the metric definition. Revenue per user factors exactly into conversion times orders per buyer times value per order, a cheap pipeline check.

Check before celebrating: revenue per click up 6% with clicks down 5% is about 1.06 x 0.95 = 1.007, close to flat.

## Two ways to compute it

- Ratio of averages: total numerator over total denominator. Weights heavy users; matches the site-wide dashboard figure.
- Average of ratios: compute per user, then average. Each user counts once; usually more sensitive, more outlier-resistant and less prone to metric SRM, with a simple variance.

Choose deliberately and write it into the definition.

## Standard error

Sessions are not independent: the user is the unit. For the ratio of averages, linearise with the [[Delta Method for Ratio Metrics]]. On the example, the delta-method SE was 0.0490, a user-level bootstrap 0.0491 ([[Bootstrap Resampling and Its Failures]]), and the naive per-session formula 0.0282, about 40% too small. With the proper SE, neither ratio version of the revenue-per-session decline was significant (p = 0.2010 and 0.2743), while conversion was clearly up (p = 0.0033) and revenue per user had the right sign but was too noisy (p = 0.1450).

## See Also
- [[OEC, Guardrails and North Star Metrics]] — related
- [[Delta Method for Ratio Metrics]] — extends
- [[Pseudoreplication and Intraclass Correlation]] — related
