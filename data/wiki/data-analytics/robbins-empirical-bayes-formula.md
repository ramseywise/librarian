---
title: Robbins Empirical Bayes Formula
tags: [data-analytics, bayesian-analysis, concept]
summary: With many parallel Poisson cases, the posterior mean for one case can be read off the counts of how many cases showed x and x+1 events, with no prior assumed; a fitted parametric prior is steadier where counts are thin.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch06-empirical-bayes.md
---

# Robbins Empirical Bayes Formula

Efron and Hastie (*Computer Age Statistical Inference*, ch. 6) ask how a large collection of parallel cases can supply the prior that Bayes' rule needs, so that each case is estimated from the others. They call the Bayesian formula for one subject, estimated empirically from a collection of similar cases, empirical Bayes. They contrast direct evidence (a subject's own outcome) with indirect evidence (the relevance of the other cases).

## The formula

For counts x_k ~ Poisson(theta_k) with an unknown prior g(theta), Bayes' rule gives the posterior mean as (x+1) times f(x+1) over f(x), with f the marginal probability of each count. Robbins' empirical version swaps f for observed frequencies, giving (x+1) times y(x+1) over y(x), where y(x) is the number of cases that showed x events.

## Auto-insurance example

Setup: Table 6.1, one year of claim counts for 9,461 European auto-insurance policy holders, modelled as Poisson with an unknown prior.

- A customer with no claims this year gets an expected 0.168 next year, computed as 1 x 1317 / 7840.
- The empirical estimates for x = 1 and x = 2 are 0.363 and 0.527.
- At large x the formula is unstable because counts are tiny: x = 5 (y = 4) gives 6.00 and x = 6 (y = 4) gives 1.75, which is not monotone, while the parametric row rises smoothly.
- A gamma prior fitted by maximum likelihood gives 0.164 for x = 0 and 0.398 for x = 1.

## Smooth prior for binomial counts

Setup: nodes study, 844 cancer operations, x positive nodes out of n removed (n ranged 1 to 69, averaging 19 with sd 11), x_k ~ Bi(n_k, theta_k), with log g(theta) a degree-4 polynomial fitted by maximum likelihood. 340 of the 844 patients (40%) had an observed ratio of zero. The fitted prior puts 0.12 of its mass at or below 0.01 (the shrunken zero spike; see Limits for the raw-ratio comparison); 0.59 of its mass lies under 0.2 and 0.07 over 0.8. A patient with 3 positive nodes of 6 has raw estimate 0.50 and posterior mean 0.446.

Efron and Hastie advise Robbins' formula when the prior is unknown and many parallel cases exist, and a parametric prior fit when counts are small.

## Limits

- The nodes figures do not agree: 40% of the 844 raw ratios are exactly zero, yet the text puts 38% of raw ratios below 0.01, which cannot be lower. Treat the 38% comparison as unreliable.
- At the right end of Table 6.1, where few cases share a count, the empirical formula is erratic.
- The nodes prior takes the log-density to be a degree-4 polynomial, and its error bars are only valid if that fits. The computation is left to chapter 21.
- The chapter does not treat the winner's curse or James-Stein shrinkage here; that is chapter 7.

## See Also
- [[James-Stein Estimator and Shrinkage]] — related (the normal-means empirical Bayes estimator)
- [[Good-Toulmin Missing-Species Estimator]] — extends
- [[Small-N Trap and Shrinkage]] — prerequisite-for
- [[Partial Pooling and Multilevel Models]] — related
- [[Empirical Bayes: Tweedie's Formula and g-Modeling]] — extends
