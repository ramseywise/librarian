---
title: Predicting from a Posterior as a Mixture
tags: [data-analytics, bayesian-analysis, pattern]
summary: "A prediction should average the outcome distribution over the whole posterior of the rate, not plug in its best value; a Poisson goal model gives win, tie and series probabilities this way, and uncertainty in a rate matters when the response is non-linear."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-bayes-ch07-prediction.md
  - data/raw/papers/2026-11-08-think-bayes-ch08-observer-bias.md
---

# Predicting from a Posterior as a Mixture

## Goals as a Poisson process

Downey's *Think Bayes* (1st edition), chapter 7, models goals as a Poisson process with time between goals exponential. The prior over goals per game is roughly Gaussian across 2010-11 NHL teams, mean 2.8 and sd 0.3. From the first four finals games (the Bruins scored 0, 2, 8 and 4 goals, the Canucks 1, 3, 1 and 0) the likeliest rate is 2.9 for the Bruins and 2.6 for the Canucks. Goals in the next game follow a Poisson mixture with weights from the rate's posterior (built with a meta-Pmf, a distribution whose values are themselves distributions).

- Bruins next game, regulation: win 46%, loss 37%, tie 17%.
- Sudden-death overtime: Bruins win 52% (exponential time to first goal, mixed over the posterior); overall win probability 55%.
- Series win (win the next two, or split and win the third): 57% under the low-variance prior; with a prior from pair-by-pair regular-season averages (mean 2.8, sd 0.85) it is 80%. With so little data the results move with the prior.

Downey's advice: predict with a mixture, not a plug-in estimate; begin simple and iterate; put effort into the prior when data are thin.

## Uncertain arrival rate and a non-linear decision

Chapter 8 predicts the wait for a Red Line train from observed passenger counts. Passengers see gaps oversampled in proportion to length (observer bias): if 5- and 10-minute gaps are equally common, the real average is 7.5 minutes but riders experience 8.33. On the collected data (southbound Kendall Square, 4 to 6 pm, 5 weekdays) the mean gap z is 7.8 minutes and the observed zb is 8.8, about 13% higher.

With the arrival rate lam known at 2 per minute, 15 waiting passengers imply the next train within 5 minutes with about 80% confidence. Folding in uncertainty about lam (36 arrivals over about 18 minutes across five days) gives a very similar result to the point estimate, which Downey attributes to the response being approximately linear. He advises keeping an input's variability in the analysis when the system's response is non-linear. For a stop-or-taxi decision, accepting a 10% risk of missing the connection, wait while fewer than 30 passengers are on the platform and take a taxi above that (the three long delays a year, 30 to 50 minutes each, were added by hand).

## Limits

- The text states a prior mean of 2.8 while the Hockey class code uses 2.7, and the Gaussian helper passes its arguments in the wrong order. The Poisson model overlooks changes in scoring within a game, and the prior takes no account of the opponent.
- The Red Line rate is assumed constant across days with no special events; the delay frequency is from memory, not data; the distribution of z is assumed known; the printed wait-time code has a naming slip.
- Python 2 era code on thinkbayes.

## See Also
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for
- [[Posterior Predictive Checks]] — related
- [[Inspection Paradox in Metrics]] — related (the same length bias)
- [[Bayes Action and Loss Functions]] — related (the decision step)
