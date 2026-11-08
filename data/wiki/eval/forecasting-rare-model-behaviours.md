---
title: Forecasting Rare Model Behaviours
tags: [eval, pattern]
summary: "Fit a Gumbel-tail line to the ten highest per-query elicitation scores of a 100-1,000 query eval to forecast the worst-case risk at up to roughly 1,000 times as many queries; the mean absolute log10 error on misuse worst-query risk was 1.7 against 2.4 for a log-normal fit (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jones-2025-forecasting-rare-language-model-behaviors.md
---

# Forecasting Rare Model Behaviours

Jones, Tong et al. (Anthropic, Mila and UC Berkeley, arXiv 2502.16797, 2025 preprint) observe that one
evaluation output is a yes/no event, whereas every query carries a continuous **elicitation
probability**, meaning the likelihood that a single sampled output exhibits the target behaviour. They
claim that the largest of these probabilities scale as a power law of the query count (fitted
with a Gumbel tail), which would let a small eval set forecast worst-case risk at deployment
scale, up to roughly three orders of magnitude beyond the eval size.

## Method

The elicitation probability p of each query is converted to the score psi = -log(-log p), and an ordinary
least squares line is fitted to the ten top scores in the eval set. That fit then forecasts worst-case
risk for a bigger deployment size n (in the experiments n reaches somewhere between 90,000 and 500,000).
A log-normal fit serves as the baseline.

## Results (self-reported; Gumbel-tail unless noted)

1. **Misuse worst-query risk.** Four models: Claude 3.5 Sonnet (new) and Claude 3 Haiku, plus the base
   model of each. Eval size m was 100, 500 or 1,000 and deployment size n ran from 10,000 to 90,000. Mean
   absolute log10 error is 1.7, compared with 2.4 for log-normal. In 72% of cases the forecast lands inside
   one order of magnitude. The Gumbel-tail fit underestimates in 34% of cases, versus 72% for log-normal
   (a method without bias would be at 50%).
2. **Behaviour frequency.** Nineteen substances (10 chemical, 9 biological), with 1,000 random eval sets
   for each, thresholds between 0.1 and 0.9 and m from 100 to 1,000. The log error of an individual
   forecast is 0.84 at m=100 and 0.76 at m=1,000; log-normal gives 3.31 to 4.04.
3. **Aggregate risk.** With m=1,000 and n from 10,000 to 500,000, using 10 rollouts per setting to forecast
   the probability of a single specific target output, mean log error is 1.3 versus 2.5 for log-normal
   (the table averages are 1.286 and 2.523).
4. **Misaligned actions.** Only Claude 3.5 Sonnet (new) was used, on synthetic two-choice questions about
   power-seeking, self-preservation and self-exfiltration, built from 100,000 generated system prompts. For
   worst-query risk the absolute error is 0.05 and the log error 0.06; log-normal scores 0.12 and 0.12.
5. **Red-team compute allocation.** Claude 3.5 Sonnet (new) and Claude 3.5 Haiku act as query generators,
   with Sonnet costing 10 to 100 times as much. Over 223 settings the forecast identifies the better
   generator 63% of the time, whereas the majority baseline manages 54% and chance 50%; accuracy is 79%
   when the real difference exceeds two orders of magnitude.
6. **Correctness extension.** Claude 3.5 Haiku, 100 sampled outputs per query (500 when required) over
   10,000 queries: worst-query risk has an absolute error of 0.172 with a log error of 0.17, and a maximum p over 0.5
   is called correctly 75% of the time.

## Limits

- The forecast depends heavily on the ten highest points in the particular eval set and on noisy ground
  truth; no uncertainty intervals are given, and the use of Gumbel as the extreme-value family is not
  checked against alternatives.
- Neither method is unbiased: the Gumbel-tail fit underestimates 34% of the time (23.9% for the
  misaligned-action tasks), and in red-teaming the forecasts overshoot, increasingly so for longer-range forecasts.
- The "deployment" is a simulation: ground truth sits at most three orders of magnitude above the eval,
  with queries resampled from the same pool, so larger scales are claimed but not tested. Eval and
  deployment queries are taken to share one distribution; the authors say they vary only the number of
  queries rather than distribution shift, and adaptive adversaries were not tried.
- The majority of misuse results rely on proxies (the log-probability of a particular output, or a keyword);
  only the small Haiku run checks whether outputs are correct. Misaligned-action tests are synthetic
  multiple-choice questions on a single model. Sampling many times is expensive, and the authors only suggest
  adaptive stopping and importance sampling as remedies.
- Every model and query generator is a Claude model from Anthropic.
- INTERNAL INCONSISTENCIES: the introduction says 86% of misuse forecasts fall within one order of
  magnitude (900 to 90,000 samples), but the extraction notes the paper never names which of its three
  metrics that covers, so the figure is left out of the results above.

## See Also
- [[Extreme-Risk Model Evaluation]] — related (dangerous-capability and propensity evals; this paper forecasts misuse and misaligned-action behaviours)
- [[Eval Error Bars and Sample Size]] — related (small-eval uncertainty; this method gives none of its own)
- [[Eval Non-Determinism]] — related (repeated sampling of a stochastic model)
- [[Best-of-k Headline Inflation]] — related (the extraction lists a best-of-N scaling law as a precursor)
