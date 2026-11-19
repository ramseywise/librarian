---
title: Best-Arm Identification, Track-and-Stop and Sequential Halving
tags: [data-analytics, bayesian-analysis, concept]
summary: "When exploring is free and only the final recommendation counts, cumulative-regret policies are the wrong tool: fixed-confidence identification has an instance lower bound that track-and-stop matches, and fixed-budget identification uses sequential halving."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch33-pure-exploration.md
---

# Best-Arm Identification, Track-and-Stop and Sequential Halving

*Bandit Algorithms*, ch. 33. In pure exploration the learner pays nothing for exploring and is judged on a recommendation A_{n+1}.

## Criteria

- **Simple regret:** the expected gap of the recommended arm.
- **Best-arm identification (BAI):** rewarded only for naming an exactly optimal arm. Two regimes exist. In the fixed-confidence one the learner must be right with probability 1 - delta or more and wants the fewest samples, with a random stopping time tau. In the fixed-budget one n rounds are given and the aim is to minimise the probability of recommending a suboptimal arm.
- The authors doubt that exact identification is a practical goal, because an arm with a small enough gap for the budget is good enough, which simple regret expresses better.

## Simple regret

- Uniform exploration (Algorithm 20) has worst-case simple regret O(sqrt(k log k / n)) for 1-subgaussian arms; the log k is tight for it.
- Sampling the recommendation from the empirical distribution of arms a cumulative-regret policy played gives simple regret equal to its regret divided by n, so minimax simple regret is of order root(k/n).
- Cumulative-regret-optimal algorithms are poor for BAI: the probability of a suboptimal pick decays only polynomially in n (Bubeck et al. 2009). Empirical means from such a run tend to be negatively biased.

## Fixed confidence: track-and-stop

A sound learner's expected stopping time is at least c*(nu) times log(1/(4 delta)), where the reciprocal of c*(nu) is the best allocation's worst-case (over alternative bandits nu') allocation-weighted KL divergence. Track-and-stop (Algorithm 21, Garivier and Kaufmann 2016) pulls the arm with the largest gap between its target count under the estimated optimal allocation and its actual count, forces a pull of any arm with under root t pulls, and stops once the generalised likelihood-ratio statistic Z_t passes a threshold beta_t(delta) of the form k log(t^2 + t) plus a function of delta. For unit-variance Gaussian arms with a unique best arm it is sound and the ratio of expected stopping time to log(1/delta) tends to c*(nu) as delta goes to 0. With two such arms the reciprocal of c* is (mu1 - mu2)^2/8 and the optimal allocation is half each.

## Fixed budget: sequential halving

Algorithm 22 (Karnin et al. 2013) divides the budget over ceil(log2 k) phases; in each, every surviving arm gets the same number of pulls and the worse half (by that phase's samples) is dropped. Its probability of error is capped by 3 log2(k) times the exponential of minus n over 16 H2 log2(k), with H2 is the maximum over suboptimal arms of its rank (best first) divided by its squared gap; H2 <= H1 <= (1 + log k) H2, H1 being the sum of the inverse squared gaps with each capped at the smallest gap's.

- All gaps equal: H2 = k/Delta^2 and uniform exploration is moderately better.
- One arm with small gap Delta and the rest at gap 1: sequential halving's exponent is Theta(n Delta^2) against Theta(n Delta^2/k), so it is significantly better.

## Limits

- Track-and-stop is optimal only as delta goes to 0 and is analysed for unit-variance Gaussian arms; neither the forced-exploration threshold nor the stopping threshold has a principled tuning, and the authors say nothing is fundamental about the root t choice.
- Fixed budget has no asymptotically matching bounds; sequential halving is only roughly optimal.
- Successive elimination, LUCB and lil'UCB are not covered; no experiments.
- Instance-dependent simple-regret bounds are unstudied.

## See Also
- [[Thompson Sampling and Bandit Regret]] — alternative-to (cumulative regret; exploration is paid for)
- [[Gittins Index and Bayesian Optimal Bandits]] — related
- [[Upper Confidence Bound Bandit Algorithms]] — alternative-to (cumulative-regret policies)
- [[Bandit Regret Lower Bounds]] — prerequisite-for
