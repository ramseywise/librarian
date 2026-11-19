---
title: Explore-Then-Commit Bandit Policy
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Explore-then-commit plays every arm m times, then commits to the best empirical mean; its regret is m times the gaps plus a commitment-error term, and the best m depends on the unknown gap, which is the problem UCB removes."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch06-explore-then-commit-algorithm.md
  - data/raw/papers/2026-11-08-auer-2002-finite-time-analysis-multiarmed-bandit.md
---

# Explore-Then-Commit Bandit Policy

## The policy

Lattimore and Szepesvari's Algorithm 1 takes an exploration length m. In rounds 1 to mk it plays the arms in round-robin order, so each arm is played m times. After that it plays, for every remaining round, the arm with the largest empirical mean from the exploration phase (ties broken arbitrarily).

## Regret bound

For a k-armed bandit with 1-subgaussian rewards (see [[Sub-Gaussian Tail Bounds and Confidence Radii]]) and 1 <= m <= n/k, horizon n (Theorem 6.1):

```text
R_n <= m * sum_i Delta_i + (n - mk) * sum_i Delta_i * exp(-m * Delta_i^2 / 4)
```

The first term is the price of exploring. The second is the price of committing to the wrong arm. The proof treats the difference of two empirical means as sqrt(2/m)-subgaussian and applies the sample-mean tail bound.

## Tuning m for two arms

With k = 2 and gap Delta, the bound becomes m*Delta + n*Delta*exp(-m*Delta^2/4). Ignoring rounding, the minimising choice is m = max{1, ceil((4/Delta^2) log(n Delta^2/4))}, giving R_n <= min{n Delta, Delta + (4/Delta)(1 + max{0, log(n Delta^2/4)})}. Taking Delta <= 1, this implies a gap-free bound of 1 + C sqrt(n) for a universal constant C (an exercise). Both Delta and n must be known to set that m.

In the authors' simulation (Gaussian bandit, k = 2, means 0 and -Delta, n = 1000, Delta varied from 0 to 1, 100,000 runs per point) the empirical expected regret sits close to the tuned upper bound across gaps. A later experiment on the same setup (ETC with m in {25, 50, 75, 100} against UCB) found tuned-per-gap ETC beats the parameter-free UCB only by a small margin; with m fixed without knowing Delta, ETC usually does not outperform UCB (read from a figure; see [[Upper Confidence Bound Bandit Algorithms]]).

## Variants when the gap is unknown

- Choosing m from n alone gives regret of order n^(2/3) for any gap (an exercise in the chapter).
- A data-dependent commitment rule or an elimination algorithm can recover near-optimal regret without the gap.
- The doubling trick removes the need to know the horizon (an exercise).

## Epsilon-greedy relatives

The chapter calls epsilon-greedy a randomised relative: at round t, with probability 1 - eps_t it picks the arm that looks best so far, else an arm chosen uniformly. Auer, Cesa-Bianchi and Fischer analyse a decaying version, eps_n-greedy with eps_n = cK/(d^2 n), where d is a known lower bound on the gap between the best and second-best arm. For large c (for example c > 5) the probability of choosing a suboptimal arm at step n is of order c/(d^2 n), for n >= cK/d, and rewards must lie in [0, 1] (Theorem 3). A constant epsilon gives linear regret.

In their Bernoulli experiments (2-armed and 10-armed, seven distributions, 100,000 plays averaged over 100 runs), an optimally tuned eps_n-greedy almost always performed best but degraded rapidly when c was mistuned, and was hurt on two of the 10-arm settings (distributions 12 and 14), which have several clearly suboptimal arms (self-reported). The comparison UCB1-Tuned and UCB2 against it is on the UCB page.

## Limits

- The tuned m uses the gap, which the chapter says is seldom reasonable to know, as well as n.
- ETC is not anytime, because when it commits depends on the horizon.
- All variants assume a known subgaussian constant (sigma = 1 by normalisation).
- The chapter cites Garivier et al. (2016b) for ETC being suboptimal in the infinite-data limit, a result from chapter 16 not covered here.
- Without a cap on the reward range (Delta <= 1) the worst-case bound is infinite.
- Tuning of m in the chapter is for k = 2; Theorem 6.1 itself holds for k arms.
- eps_n-greedy needs d, a known lower bound on the gap, and no single value of c works everywhere; Auer et al. report single 100-run averages with no variance in the text.

## See Also
- [[Thompson Sampling and Bandit Regret]] — related (adaptive allocation)
- [[Upper Confidence Bound Bandit Algorithms]] — alternative-to (needs no gap knowledge)
