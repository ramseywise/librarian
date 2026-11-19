---
title: G-Optimal Design and Phased Elimination
tags: [data-analytics, bayesian-analysis, pattern]
summary: "A G-optimal design picks a few arms to pull in proportion to a distribution that makes least-squares confidence widths uniformly small; phased elimination uses it each phase to get sqrt(d n log(nk)) regret on a fixed finite action set."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch21-optimal-design-least-squares-estimators.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch22-stochastic-linear-bandits-finitely-many-arms.md
---

# G-Optimal Design and Phased Elimination

*Bandit Algorithms* (ch. 21-22) chooses exploratory actions so that unregularised least-squares estimates are accurate for every action in the set at once.

## Design

A design is a distribution pi on the action set A where V(pi) sums pi(a)*a*a^T over actions, and g(pi) is the biggest squared length of any action measured in the inverse of V(pi). A G-optimal design minimises g; a D-optimal design maximises log det V(pi). The Kiefer-Wolfowitz theorem says the two coincide, the minimum of g equals the dimension d, and some minimiser has at most d(d+1)/2 support points (its core set).

To get confidence width epsilon for every a with probability 1-delta (fixed exploratory sequence, 1-subgaussian noise, actions spanning R^d), pull each supported action a a number of times n_a, rounded up, equal to

`2 * pi(a) * g(pi) * log(1/delta) / eps^2`. The total exploration length is bounded by the support size plus 2 g(pi)/eps^2 times log(1/delta). An approximate design with g at most (1+eps) times the minimum inflates the regret of bandit algorithms built on it by no more than the square root of (1+eps).

## Computing it

Frank-Wolfe (Fedorov/Wynn) updates move the distribution toward the point a_k with the largest ||a||^2 in the V(pi_k)^-1 norm: pi_{k+1} = (1 - gamma_k) pi_k + gamma_k times the indicator of a_k. From a uniform start on a finite set it gets g within (1+eps) of the minimum after order d*log log|A| + d/eps iterations; a more elaborate initialisation gets g within twice the minimum, with order d*log log d iterations and a core set of that same order. The chapter advises using rank-one updates of the inverse for speed.

## Phased elimination

Algorithm 12 of chapter 22 runs in phases l with eps_l = 2^-l. In each phase it computes a design on the surviving arms (the chapter states it as maximising log det V(pi), support at most d(d+1)/2), plays arm a for T_l(a) = 2d*pi_l(a)*log(k*l*(l+1)/delta)/eps_l^2 rounds, and drops every arm whose estimated gap to the best surviving arm exceeds 2 eps_l.

For a fixed set of k arms, the regret is of order sqrt(d n log(nk)) (Theorem 22.1, a claim; the proof is left as an exercise), which beats the d*sqrt(n)*log(n) of [[LinUCB and Linear Bandit Confidence Ellipsoids]] by a factor of the square root of d when k is moderate. With probability at least 1-delta regret stays under a constant times the root of n*d*log(k*log(n)/delta); taking delta near 1/n converts this to expected regret. A phase lasts at most 2d/eps_l^2 times the log term of the pull rule, plus d(d+1)/2 for rounding the support up. The algorithm tolerates a reward error f with sup norm at most eps, with regret of order sqrt(dn log(nk)) plus n eps sqrt(d) log(n). For infinite action sets it adapts using chapter 20 confidence intervals, giving d sqrt(n log(n)).

For action sets that change over time, the chapter prefers LinUCB or Thompson sampling in practice: SupLinRel and SupLinUCB reach sqrt(nd log^3(nk)) for changing sets of at most k actions, but are complicated.

## Limits

- Chapter 21 is exploration design only, with no bandit algorithm or regret bound of its own and no experiments. The exact optimal integer allocation is called likely intractable, so the n_a rule rounds up. Algorithms for infinite action sets are described as much heavier and less practical, with none given. The estimator is unregularised, needs actions that span R^d, and the actions are fixed, not adaptive.
- Chapter 22 needs one finite action set that never changes, an assumption it calls crucial. Choices inside a phase draw only on earlier phases, so the phase's own data goes unused until it ends. It does not discuss the cost of solving the design each phase, and has no experiments or figures.
- The chapter 21 step-size formula is given as printed in the text.

## See Also
- [[LinUCB and Linear Bandit Confidence Ellipsoids]] — prerequisite-for (the optimistic baseline whose regret this improves)
- [[Bandit Regret Lower Bounds]] — related (the d sqrt(n) lower bound for linear bandits)
- [[Thompson Sampling and Bandit Regret]] — related (the context-free bandit; phased elimination is the chapter's alternative to Thompson sampling only for fixed action sets)
