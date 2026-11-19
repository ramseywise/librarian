---
title: Partial Monitoring Games
tags: [data-analytics, bayesian-analysis, concept]
summary: "In partial monitoring the learner sees a signal instead of its loss; finite adversarial games fall into exactly four regret classes (0, sqrt n, n^(2/3), linear), decided by whether neighbouring actions are locally or globally observable."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch37-partial-monitoring.md
---

# Partial Monitoring Games

*Bandit Algorithms*, ch. 37. A finite adversarial game is a loss matrix L (k actions by d outcomes) and a feedback matrix Phi of signals; the learner plays A_t, gets loss L[A_t, i_t] unseen, and receives signal Phi[A_t, i_t]. A bandit game has Phi = L; a full-information game reveals the outcome in every row.

## Classification

Each action a has a cell C_a, the set of outcome distributions where it is optimal. Dominated actions have empty cells; Pareto optimal actions have cells of dimension d-1; two Pareto optimal actions are neighbours when their cells meet in dimension d-2.

- A neighbouring pair (a, b) is **globally observable** if some function f exists whose sum over actions c of f(c, signal of c under outcome i) equals the loss difference L_ai - L_bi, for every outcome i, and **locally observable** if f(c, .) = 0 for every c outside the pair's neighbourhood N_ab.
- Minimax regret is 0 (trivial: no neighbouring actions), Theta(sqrt n) (easy: locally observable), Theta(n^(2/3)) (hard: globally but not locally observable) or Omega(n) (hopeless), and nothing else (Theorem 37.11, reported). Lower bounds: c_G n^(2/3) for hard games from two indistinguishable alternatives with gap about n^(-1/3); c_G sqrt n for easy games.
- Example 37.3: matching pennies with a costly revealing action (cost c > 1/2) gives every policy regret of order n^(2/3), via an adversary whose p is 1/2 plus or minus n^(-1/3).

## Algorithm 26

Exponential weights over Pareto optimal actions, with exploration chosen by a convex program rather than a fixed epsilon: at each round solve for the sampling distribution P_t and a loss-difference function f_t balancing information against regret, sample A_t, observe the signal and use the importance-weighted estimate f_t(A_t, sigma_t)/P_{t,A_t}. Tuned, it gets O(sqrt n) regret on locally observable games (with k^(3/2) dependence) and O(n^(2/3)) on globally observable ones. It recovers the bandit bound and the full-information bound as special cases. An adaptive learning rate, the smaller of 1/B and a root-log-k term shrinking with the accumulated V values, avoids having to compute the optimum.

## Guidance

- The chapter lists costly-information settings as partial monitoring: a human labelling spam, medical testing, factory quality checks and dynamic pricing.
- Hard games force the learner to play clearly suboptimal actions just to gather information, so exploration should be paid for only when needed.

## Limits

- Big-O notation conceals the dependence on k, d and m; the constants v_glo and v_loc depend on the game alone but may be exponentially large in d.
- The authors say partial monitoring is still quite poorly understood and the lower bounds are surely very conservative.
- Computing the optimum is hard (not convex in q) and numerically unstable for small eta or large k, d. The contextual version and infinite action or outcome sets are not covered.
- The authors state that core proofs in Foster and Rakhlin 2012 and Bartok 2013 contain errors.

## See Also
- [[Exp3 for Adversarial Linear Bandits]] — related (exponential weights with importance-weighted estimates)
- [[Thompson Sampling and Bandit Regret]] — related
