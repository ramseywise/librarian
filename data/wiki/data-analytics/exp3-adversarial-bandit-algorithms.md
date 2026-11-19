---
title: Exp3 Adversarial Bandit Algorithms
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Exp3 samples arms from exponential weights over importance-weighted reward estimates, giving sqrt(K T log K) regret against any reward sequence; Exp3-IX and Exp3.P add bias or confidence terms so the bound holds with high probability, not only in expectation."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch11-exp3-algorithm.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch12-exp3-ix-algorithm.md
  - data/raw/papers/2026-11-08-auer-2002-nonstochastic-multiarmed-bandit-problem.md
---

# Exp3 Adversarial Bandit Algorithms

In an adversarial bandit the rewards are an arbitrary sequence of vectors in [0, 1]^k with no statistical assumption, and the learner is compared with the best fixed arm in hindsight. An oblivious adversary fixes all rewards at the start; a reactive one lets them depend on history. Any deterministic policy (UCB and ETC are examples) suffers regret of at least n(1 - 1/k) in the worst case, because the adversary can zero the reward of whichever arm it will choose and set the rest to 1 (an exercise in Lattimore and Szepesvari). So sublinear regret needs randomisation.

## Exp3

Keep a cumulative estimate S_i of each arm's reward. Play arm i with probability proportional to exp(eta * S_i), observe only the chosen arm's reward, and update.

- Importance weighting: the estimate for arm i is I{A_t = i} X_t / P_ti, unbiased given the past; its variance is x_ti^2 (1 - P_ti) / P_ti.
- The book's Algorithm 9 uses a loss-based variant, adding 1 - I{A_t = i}(1 - X_t)/P_ti to S_i, since that form never exceeds 1, a property the proof's exp(x) <= 1 + x + x^2 step requires.
- Auer et al.'s original (Fig 1) mixes the weight distribution with uniform exploration: p_i = (1 - gamma) w_i / sum w + gamma/K, with w_j multiplied by exp(gamma xhat_j / K).

Bounds, for rewards in [0, 1], horizon n (T), k (K) arms:

| Setting | Expected regret bound |
|---|---|
| eta = sqrt(log k / (nk)), no extra exploration (Thm 11.1) | 2 sqrt(nk log k) |
| eta = sqrt(2 log k / (nk)) (Thm 11.2) | sqrt(2 n k log k) |
| Auer et al., gamma tuned with g >= G_max, g = T when T is known (Cor 3.2) | 2.63 sqrt(g K ln K) |

The authors give a lower bound of order sqrt(nk) (the book states a universal constant c; Auer et al. give (1/20) min{sqrt(KT), T}), so the upper bound is off by a sqrt(log k) factor, and closing it is an open problem in Auer et al. Full-information exponential weights (Hedge) get sqrt(n log(k)/2). The book reaches its lower bound by embedding stochastic Bernoulli bandits in the adversarial class. Auer et al. note that theirs is consistent with O(ln T) stochastic rates, because the reward distribution in their construction depends on K and T.

## Regret does not concentrate

Exp3's expected regret is close to optimal but its distribution is not. Auer et al. argue, without proof, that estimator variance (up to about 1/p_i) could push regret as high as T^(3/4). Exercise 11.6 in the book states a two-armed bandit, for large n and reasonable eta, where the chance that realised regret reaches n/4 exceeds 1/131. In a simulation (k = 2, n = 10^4, eta = sqrt(2 log(k)/(nk)), 500 repetitions, alpha near 0.28 to 0.30) regret ranged from about -1,000 to 4,000 (read from a figure).

## High-probability variants

- **Exp3-IX** (implicit exploration, Algorithm 10): the loss estimate is I{A_t = i} Y_t / (P_ti + gamma). It is biased downward (optimistic), and most for small P_ti, so arms with low probability keep being sampled. The bias is exact: the difference between biased and unbiased cumulative estimates is gamma times the sum of estimates (Lemma 12.4). With probability at least 1 - delta each estimate error is at most log((k+1)/delta)/(2 gamma) (Lemma 12.3). Taking gamma = eta/2 and eta = sqrt(2 log(k+1)/(nk)) gives one algorithm that serves every delta. Taking eta = sqrt((log k + log((k+1)/delta))/(nk)) instead bounds regret by 2 sqrt((2 log(k+1) + log(1/delta)) nk) + log((k+1)/delta) with probability 1 - delta. Headline: O(sqrt(nk log(k/delta))). The anytime version uses eta_t = sqrt(log(k)/(kt)) and gamma_t = eta_t/2 (stated without proof).
- **Exp3.P** (Auer et al.): adds an upper-confidence term to the estimates; with probability at least 1 - delta, regret is at most 4 sqrt(KT ln(KT/delta)) + 4 sqrt((5/3) KT ln K) + 8 ln(KT/delta). It needs T and holds for delta >= K T e^(-KT), T >= (20/3) K ln K.
- **Restart versions** remove the need for T or G_max: Exp3.1 gives 10.5 sqrt(G_max K ln K) + 13.8 K + 2K ln K for any T. Exp3.P.1 carries a probability bound and, for any f growing without limit, has regret that is almost surely o(sqrt(T ln T f(T))).

## Other variants in Auer et al.

- **Exp4**: N experts each give a distribution over arms; regret against the best expert is O(sqrt(K T ln N)), so it grows only logarithmically in N. The uniform expert must be among the experts, or in their convex hull.
- **Exp3.S**: regret against any action sequence, scaled by its hardness H = 1 + number of arm changes; setting alpha = 1/T and gamma = min{1, sqrt(K ln(KT)/T)} bounds regret by H sqrt(KT ln(KT)) + 2e sqrt(KT/ln(KT)), simultaneously for all sequences.
- Exp3.P.1 is Hannan-consistent in an unknown repeated game; with Exp3.1 on an unknown payoff matrix the row player's expected per-round payoff approaches the game value.

## Limits

- The two sources use different notation and tunings (loss and eta against reward and gamma with uniform mixing), so constants are not comparable; the book also says extra uniform exploration is unnecessary.
- Exp3 needs the horizon (or a bound on G_max) to tune; the book points to the doubling trick or a decreasing rate.
- Rewards must lie in [0, 1]; other ranges rescale, and the unbounded case gives only weak results.
- Regret against the best fixed arm builds in stationarity and fits non-stationary bandits poorly; no sublinear policy regret is possible against reactive adversaries without a memory limit.
- Exp3-IX's chapter gives no explicit counterexample that Exp3 has no high-probability bound, only the variance argument; it defers the delta-free versus delta-tuned trade-off to chapter 17, and the simulation settings in its figures (runs, seeds) are only sketched.
- Auer et al. have no experiments; extending the results to adaptive adversaries is asserted, and checking it is left to the reader. The Exp3.P restriction on T and delta is stated as a "without loss of generality" assumption. Formulas in that extraction were read from page images.

## See Also
- [[Upper Confidence Bound Bandit Algorithms]] — alternative-to (stochastic rewards, deterministic policy)
- [[Counterfactual Evaluation with Inverse Propensity Scoring]] — related (importance weighting of a chosen action's reward)
- [[Thompson Sampling and Bandit Regret]] — related
- [[Exp4 and Oracle-Based Contextual Bandits]] — extends
- [[Non-Stationary Bandits and Tracking Regret]] — extends
