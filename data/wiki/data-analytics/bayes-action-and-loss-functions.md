---
title: Bayes Action and Loss Functions
tags: [data-analytics, bayesian-analysis, concept]
summary: "A posterior is not a decision: write down what each wrong answer costs, average that loss over posterior draws and pick the minimiser; squared loss gives the mean, absolute loss the median, zero-one the mode, and asymmetric losses give answers no point estimate would."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--05-loss-functions-and-decisions.md
  - data/raw/papers/2026-11-08-bayesian-methods-for-hackers-ch05-would-you-rather-lose-arm-or.md
  - data/raw/papers/2026-11-08-think-bayes-ch06-decision-analysis.md
---

# Bayes Action and Loss Functions

Accuracy measures how close an estimate is; a loss function L(theta, theta-hat) measures how bad acting on it would be. The expected loss (Bayesian risk) of an estimate is the average of L over posterior draws, and the **Bayes action** is the estimate that minimises it. With samples this is a vectorised loss plus an optimiser (or a grid).

## Standard losses and what they select

| Loss | Bayes action |
|---|---|
| Squared error | posterior mean |
| Absolute error | posterior median |
| Zero-one (as a limit) | posterior mode (MAP) |

On a right-skewed Gamma(2, scale 10) posterior an optimiser found 20.03 for squared loss and 16.85 for absolute loss, matching the sample mean and median, with the mode at 10.00. Zero-one needs a limit because every exact guess misses on a continuous posterior: count a miss as being further than a width, and shrink the width. Best guesses for widths 5.0, 1.0 and 0.2 were 10.95, 9.60 and 9.30, drifting toward the mode and getting noisy as fewer samples fall in the window (one reason a mode is hard to estimate from samples). This is why mean, median and MAP are the usual summaries ([[Maximum Likelihood and Estimator Bias]] covers the point-estimate side); when your loss is none of these, none of them is your answer.

Other losses in common use: asymmetric squared (underestimates cost more, as in capacity planning), log loss (punishes confident wrong probabilities), a bounded loss that is indifferent once far enough off, and a loss divided by theta(1 - theta) that explodes near 0 and 1 and suits someone paid for confident calls.

## Whose loss is the forecast?

A forecaster minimises their own loss, not yours. A broadcast forecaster may report a 20% chance of rain when they believe 5 or 10%, because viewers notice a missed rain forecast more than a false alarm. Ask whose loss a forecast was tuned for.

## Custom losses give custom answers

**Sign-sensitive loss.** For a true return of +0.01, squared error treats predicting -0.01 and +0.03 as equally bad, though only the first loses money. A loss that penalises the wrong direction heavily scored them 0.03 and 0.02, with predicting 0.00 scoring 0.01. In a Bayesian regression of return on a signal (slope 0.487, identical to the least-squares slope), the Bayes action at signal +0.005 was +0.0007 against a least-squares +0.0017, and at +0.02 it was +0.0060 against +0.0090. Near zero the model takes almost no position because the sign is in doubt; at +-0.05 the two agree (-0.0245 against -0.0251). The model fits no better than least squares; it makes better decisions under this loss.

**Spiky loss.** In a bidding game where overbidding gives nothing, a narrow window just under the true price wins everything, and underbidding loses the gap, the posterior mean of the price was about 20,000. Bayes-optimal bids were far lower: 14,700 when an overbid costs 30,000, falling to 11,800 when it costs 150,000, with the chance of overbidding falling from 0.070 to 0.013. The expected loss is spiky because the window pays only for rare draws, so use a grid or restarts rather than a smooth optimiser that can stop at a local bump.

## Worked examples from Davidson-Pilon and Downey

Davidson-Pilon (*Bayesian Methods for Hackers*, ch. 5) defines risk as the posterior average of L(theta, theta-hat), approximated as the mean over N samples, and minimises it with scipy's fmin when no closed form exists. His Price Is Right showcase loss charges a fixed risk when the bid exceeds the true price, a reward within 250 below it, and the shortfall otherwise. Setup: true price Normal(35000, 7500) with prize guesses Normal(3000, 500) and Normal(12000, 3000), 50,000 MCMC samples with 10,000 burn-in, bids minimised from 15,000. The Bayes action is about 14,189 at risk 30,000, falling to about 11,266 at risk 150,000, and the posterior mean the text quotes (about 20,000) is far from both. A signed stock-return loss shows why squared error is blind to sign: a prediction of -0.01 and one of 0.03 cost the same against a true return of 0.01. Under it the Bayes action can be a sparse prediction near zero when uncertainty is high.

On Kaggle's Dark Worlds (PyMC), the posterior mean for a one-halo sky landed roughly 31 pixels off the true halo, scoring 1.031 where a random guess scored 2.773; a three-halo sky scored 1.037 on the first halo only. The author admits that the loss is one more setting a practitioner could tune to get a desired result, and so advises fixing it early and showing where it came from.

Downey (*Think Bayes*, ch. 6) treats the same showcase as a decision. The prior is a Gaussian kernel density over 313 past first-showcase prices (2011 and 2012 seasons) and the contestant's guess is the data; the error of a guess is modelled as Gaussian with the standard deviation of past price-minus-bid differences. In the 2011-12 records contestants overbid 25% of the time on the first showcase and 29% on the second. A best guess of 20,000 leads to a posterior mean of 25,096; player 1's best bid is 21,000 (expected return about 16,700, above the guess) and player 2's, with a guess of 40,000, is 31,500 (about 19,400). Downey notes that summarising a posterior as a mean is often unnecessary because the payoff comes from carrying it into a decision.

## Pitfalls

- Reporting the posterior mean by habit: it answers squared loss, whether or not that is yours.
- Averaging outcomes before applying the loss: L(E[theta]) is not E[L(theta)]; apply the loss per draw, then average.
- Forgetting predictive noise: a posterior on the mean alone understates risk, so draw outcomes.
- Treating costs as objective: they are estimates with owners; show results over a range.

## The general recipe

Prior, likelihood, posterior by MCMC, then choose the prediction that minimises the expected value of the metric you are actually scored on, rather than parameter accuracy. A winning entry to a competition followed this workflow.

## Limits

- The stock data are artificial (N=100) and the Dark Worlds results rest on one or two skies with a single random-guess comparison. The showcase risk of 80,000 in the code is arbitrarily picked, fmin can stop at a local minimum, and the code is PyMC2 and Python 2.
- The Davidson-Pilon text is inconsistent: the posterior mean is given as about 20,000 and also as shifted down about 15,000, and a frequentist bid of 35,000 is quoted though the prize means sum to 15,000.
- Downey assumes both showcases have the same price in the double-win calculation and borrows error variance from bids, not guesses.

## See Also
- [[Cost-Based Decisions from a Posterior]] — extends
- [[Bayesian A/B Testing with Expected Loss]] — instance-of (loss max(pA - pB, 0))
- [[MCMC and Metropolis Sampling]] — prerequisite-for
- [[Calibrated Score, Deterministic Decision Rule]] — related
- [[Predicting from a Posterior as a Mixture]] — related
- [[Locomotive Problem: Estimators and Losses]] — instance-of
- [[Grid and Quadratic Approximation and Posterior Samples]] — related
