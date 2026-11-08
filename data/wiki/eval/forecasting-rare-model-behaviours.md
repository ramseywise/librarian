---
title: Forecasting Rare Model Behaviours
tags: [eval, pattern]
summary: "Fit a Gumbel-tail line to the ten highest per-query elicitation scores of a 100-1,000 query eval to forecast the worst-case risk at up to roughly 1,000 times as many queries; the mean absolute log10 error on misuse worst-query risk was 1.7 against 2.4 for a log-normal fit (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jones-2025-forecasting-rare-language-model-behaviors.md
---

# Forecasting Rare Model Behaviours

Jones, Tong et al. (Anthropic, Mila and UC Berkeley, arXiv 2502.16797, 2025 preprint) note that a single
evaluation output is binary, but each query has a continuous **elicitation probability**: the chance that
one sampled output shows the target behaviour. Their claim is that the largest values of that
distribution follow a power law in the number of queries (a Gumbel-tail fit), so a small eval set can
forecast deployment-scale worst-case risk up to about three orders of magnitude larger.

## Method

Each query's elicitation probability p is turned into the score psi = -log(-log p), and ordinary
least squares is fitted on the ten highest scores of the eval set. The fit is then used to forecast
the worst-case risk at a larger deployment size n (up to 90,000 to 500,000 in the experiments). The
baseline is a log-normal fit.

## Results (self-reported; Gumbel-tail unless noted)

1. **Misuse worst-query risk.** Claude 3.5 Sonnet (new), Claude 3 Haiku and their two base models, eval size
   m of 100, 500 or 1,000, deployment size n of 10,000 to 90,000. Mean absolute log10 error 1.7 against 2.4
   for log-normal. Forecasts fall within one order of magnitude 72% of the time; the Gumbel-tail method
   underestimates 34% of the time against 72% for log-normal (an unbiased method would be 50%).
2. **Behaviour frequency.** 19 substances (10 chemical, 9 biological), 1,000 random eval sets each,
   thresholds 0.1 to 0.9, m of 100 to 1,000. Individual-forecast log error 0.84 (m=100) to 0.76 (m=1,000)
   against 3.31 to 4.04 for log-normal.
3. **Aggregate risk.** m=1,000, n of 10,000 to 500,000, 10 rollouts per setting, forecasting the probability
   of one specific target output: mean log error 1.3 against 2.5 (table averages 1.286 and 2.523).
4. **Misaligned actions.** Claude 3.5 Sonnet (new) only, synthetic two-choice questions on power-seeking,
   self-preservation and self-exfiltration with 100,000 generated system prompts. Worst-query risk: absolute
   error 0.05 and log error 0.06, against 0.12 and 0.12 for log-normal.
5. **Red-team compute allocation.** Claude 3.5 Sonnet (new) against Claude 3.5 Haiku as query generators,
   Sonnet costing 10x to 100x more, 223 settings: the forecast picks the right model 63% of the time against 54%
   for the majority baseline and 50% for chance, and 79% when the true gap exceeds two orders of magnitude.
6. **Correctness extension.** Claude 3.5 Haiku with 100 sampled outputs per query (500 where needed), 10,000
   queries: worst-query absolute error 0.172, log error 0.17, and max p above 0.5 predicted correctly 75% of
   the time.

## Limits

- Forecasts are sensitive to the ten highest points of the specific eval set and to stochastic ground truth;
  there are no uncertainty intervals, and the choice of Gumbel as the extreme-value family is not tested.
- Both methods are biased: Gumbel-tail underestimates 34% of the time (23.9% on the misaligned-action
  tasks), and in red-teaming the forecasts overestimate, more so for longer forecasts.
- "Deployment" is simulated: ground truth is at most three orders of magnitude above the eval, with queries
  resampled from the same pool, so larger scales are asserted, not tested. Eval and deployment queries are
  assumed to come from one distribution; the authors say they study only changes in query count, not distribution shift, and
  adaptive adversaries are untested.
- Most misuse results use proxies (log-probability of a specific output or keyword); only the small Haiku run
  checks correctness. The misaligned-action tests use synthetic multiple-choice questions on one model.
  Repeated sampling is costly; the authors only propose adaptive stopping and importance sampling.
- All models and query generators are Anthropic's Claude models.
- The intro states that 86% of misuse forecasts are within one order of magnitude (900 samples to 90,000); the
  extraction notes the paper does not say which of the three metrics that covers, so it is left out above.

## See Also
- [[Extreme-Risk Model Evaluation]] — related (dangerous-capability and propensity evals; this paper forecasts misuse and misaligned-action behaviours)
- [[Eval Error Bars and Sample Size]] — related (small-eval uncertainty; this method gives none of its own)
- [[Eval Non-Determinism]] — related (repeated sampling of a stochastic model)
- [[Best-of-k Headline Inflation]] — related (the extraction lists a best-of-N scaling law as a precursor)
