---
title: NeuralLinear Thompson Sampling
tags: [data-analytics, bayesian-analysis, pattern]
summary: "NeuralLinear does Bayesian linear regression on a network's last hidden layer and samples from it for Thompson sampling; in a 2018 benchmark of about 15 approximate-posterior methods on contextual bandits it was robust and easy to tune, while methods that tie representation to uncertainty suffered online."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-riquelme-2018-deep-bayesian-bandits.md
---

# NeuralLinear Thompson Sampling

Riquelme, Tucker and Snoek (ICLR 2018) ask how approximate-posterior quality affects Thompson sampling in contextual bandits.

## Setup

Eight real-data contextual bandits (including Statlog, Mushroom, Jester, Financial) and the synthetic Wheel bandit, whose need for exploration grows with delta. Roughly 15 method families take part, among them linear models, NeuralLinear, RMS greedy and Bayes-by-Backprop, plus dropout, black-box alpha-divergence, a bootstrap, SGFS, constant SGD, parameter noise and a GP. Each appears with default settings and with two Bayesian-optimised hyperparameter sets. All neural methods share one 2x100 ReLU network. Cumulative regret and simple regret (averaged over the final 500 steps) are reported relative to a Uniform policy, across 50 shuffled runs.

**NeuralLinear:** the final hidden layer's output serves as features for a Bayesian linear regression. The posterior covariance is the inverse of X'X plus the prior precision Lambda_0, and the mean is that covariance times (Lambda_0 mu_0 + X'Y). The network and the regression are updated on different time-scales.

## Results (self-reported)

- Wheel, delta = 0.99, Uniform = 100: NeuralLinear's cumulative regret is roughly 50 on that scale, and RMS and its variants sit close to or over 100. Among the rows read, SGFS has the smallest value in that column. At delta = 0.5 NeuralLinear is near-optimal.
- NeuralLinear nearly solves Statlog (n = 43500), where linear approaches fail, and beats its RMS base on Mushroom (n = 50000), but is no better than RMS on Jester.
- Mean rank across five datasets: NeuralLinear scores 22, trailing the exact linear methods, LinFullPost at 13.9 and LinFullDiagPrecPost at 14.3. Tuned parameter noise improves rank over its RMS base.
- On linear data, BBB with 20 to 1000 epochs per step improves slowly but never matches the exact mean-field solution; in linear Thompson sampling, a diagonal approximation of the precision matrix performs far better than a diagonal approximation of the covariance.
- The hyperparameter search for BootstrappedNN settled on 2 and 3 networks where the hand-set version used 10, with no loss in performance.
- NeuralLinear is fast relative to the others (time normalised to RMS = 100).
- Conclusion: slowly converging uncertainty estimates hurt online; decoupling representation from uncertainty helps.

## Limits

- No baseline with dropout only in training, so exploration and training benefit are not separated.
- Tuned-on-Mushroom or Statlog versions are not independent of the evaluation sets; the GP uses only the first 1000 observations.
- Only contextual bandits, not full RL; the reason for NeuralLinear's success is a suspicion, untested. Datasets are small (Financial n = 3713).
- Mean rank favours exact linear methods; the case for NeuralLinear is qualitative and strongest on Wheel, though SGFS scores lower at delta = 0.99.
- Code was promised but not available at writing; no hardware or compute stated.

## See Also
- [[Thompson Sampling and Bandit Regret]] — prerequisite-for
- [[Gaussian Processes and Bayesian Optimisation]] — related (a GP is one of the baselines)
