---
title: Gittins Index and Bayesian Optimal Bandits
tags: [data-analytics, bayesian-analysis, concept]
summary: "The Bayesian optimal bandit policy minimises regret averaged over a prior: it is computable by backwards induction for one arm, and for discounted problems with independent arms it is the Gittins index rule, though it is brittle when the prior is wrong."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch34-foundations-bayesian-learning.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch35-bayesian-bandits.md
---

# Gittins Index and Bayesian Optimal Bandits

*Bandit Algorithms*, ch. 34-35. A Bayesian bandit environment samples the environment from a prior Q at the start and hides it from the learner. Bayesian regret is BR_n = the regret integrated over Q; the Bayesian optimal regret BR*_n(Q) is its infimum over policies.

## Foundations (ch. 34)

- A pointwise bound R_n <= f(nu) gives BR_n <= E[f(nu)], but a Bayesian regret bound does not generally give a frequentist one. The authors advise analysing the frequentist regret of Bayesian algorithms.
- The Bayesian-optimal policy itself may have positive Bayesian regret, because at the outset it has no way of knowing which arm is best.
- By Sion's minimax theorem, the minimax regret is the largest Bayesian-optimal regret taken over all priors.
- Conjugate updates used by bandit algorithms:
  - Bernoulli rewards, Beta(alpha, beta) prior: with S_t successes in t observations the posterior is Beta with parameters alpha + S_t and beta + t - S_t; the predicted chance of success is alpha + S_t over alpha + beta + t.
  - Gaussian prior with mean mu and variance sigma^2, unit-variance Gaussian rewards: the posterior mean is (mu/sigma^2 + S_t) divided by (1/sigma^2 + t), and the posterior variance is the reciprocal of (1/sigma^2 + t).
  - A product Beta prior over k Bernoulli arms stays a product, each arm updated with its own successes and pulls (see [[Beta-Binomial Updating and Credible Intervals]]).
- Exponential weights at learning rate 1 coincides with the Bayesian posterior over experts; under a uniform prior over k experts the regret for log loss is no more than log k. The authors caution against reading too much into the analogy.
- In practice, favour a prior with a posterior you can compute or sample cheaply, rather than one chosen purely to express belief.

## Bayesian optimal regret (ch. 35)

- The optimal Bayesian regret BR*_n(Q) never exceeds the minimax regret, hence is at most a constant times root kn, and some prior reaches a constant times root kn. Theorem 35.1: for any one prior the ratio to root n has limsup zero, yet some prior makes the ratio to n^(1/2 - eps) diverge in the liminf for every eps > 0. With sufficiently regular priors the rate is log^2 n (Lai 1987, reported).
- One-armed Bayesian bandit (second arm a known constant mu2): a retirement policy solved by backwards induction on sufficient statistics. With Bernoulli rewards and a Beta prior the cost is order n^2, versus order n for a usual frequentist stopping rule. Experiment 35.1 (horizon 500, known arm mean 1/2, uniform Beta(1,1) prior on the other arm): the frequentist rule does well when mu1 exceeds 1/2 and badly when it is below, and on average over the prior it is beaten by the Bayesian-optimal policy.
- Exact finite-horizon dynamic programming only scales to small problems: with horizon 50 and five Bernoulli arms under Beta priors there are roughly 10^11 states.

## Gittins index

For k independent arms with a factorised prior and geometric discounting alpha in (0,1), the index g(x) is the infimum of the charges gamma at which the value v_gamma(x) of playing is zero, i.e. the smallest charge leaving the learner indifferent between retiring and playing. Equivalently it is the supremum, over stopping times of at least 2, of expected discounted reward divided by expected discounted time. Theorem 35.9: always playing the arm with the largest index of its current state maximises total expected discounted reward among all policies.

- The result breaks under non-geometric discounting or several simultaneous plays, and the best finite-horizon policy is in general not an index rule.
- Varaiya's algorithm obtains every index of a finite chain in order |S|^4 operations using Gauss-Jordan elimination, or |S|^(3+eps) with eps up to 0.373 given faster matrix inversion.
- The undiscounted index g_n(s), a supremum over stopping times between 2 and n of expected summed reward over expected tau - 1, is not Bayesian optimal for k arms but works well as a heuristic; in the Gaussian case it has UCB-like frequentist regret (Lattimore 2016a) and behaves like the KL-UCB index asymptotically (Burnetas and Katehakis, reported).

## Limits

- In general, computing the finite-horizon Bayesian-optimal policy for k arms is intractable, though no computational lower bound has been proved.
- A wrong prior makes Bayesian policies fragile. Gittins' theorem requires geometric discounting, independent arms under a product prior and one play per round, and its asymptotic version carries no regret guarantee.
- Experiment 35.1 is one configuration, with regrets appearing only in a figure. Theorem 35.1 and a number of lemmas are set aside as exercises.
- The measure-theoretic parts of ch. 34 (rigorous posterior, exponential-family measure theory) are background and not summarised here.

## See Also
- [[Thompson Sampling and Bandit Regret]] — related (posterior sampling instead of the optimal policy)
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for
- [[Best-Arm Identification, Track-and-Stop and Sequential Halving]] — related
