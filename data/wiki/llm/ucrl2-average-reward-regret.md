---
title: UCRL2 Average-Reward Regret
tags: [llm, reinforcement-learning, concept]
summary: "UCRL2 learns an unknown finite MDP optimistically: it plans in an extended MDP built from L1 confidence balls and replans only when a state-action count doubles, giving regret of order D S sqrt(A n log n) against sqrt(D S A n) as the lower bound."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch38-markov-decision-processes.md
---

# UCRL2 Average-Reward Regret

*Bandit Algorithms*, ch. 38 treats a learner competing with the optimal average-reward (gain) policy in an unknown finite MDP. Setup for the results below: the MDP has S states and A actions, rewards lie in [0,1] and the reward function is given, the transition probabilities are not, and the MDP is strongly connected (finite diameter D). Regret is R_n = n rho* minus the sum of rewards.

## Background

- The diameter D(M) takes the worst state pair and, for it, the smallest achievable expected hitting time, less 1; it is at least log base A of S, minus 3.
- A memoryless policy's gain is P*_pi applied to r_pi, where P*_pi is the Cesaro limit of the powers of P_pi; its differential value function obeys rho + v = r_pi + P_pi v.
- The Bellman optimality equation sets rho plus v(s) equal to the maximum over actions of r_a(s) plus the inner product of P_a(s) with v. Any solution has rho equal to rho*, a greedy policy is optimal, and an optimal policy that is deterministic and memoryless exists; v is fixed only up to an additive constant, and its span is at most D(M).
- A linear program finds the optimal gain: minimise rho under the constraints that rho + v(s) is at least r_a(s) plus the inner product of P_a(s) with v. The chapter adds that, in practice, value or policy iteration beats the ellipsoid method.
- In the discounted case the Bellman operator contracts by gamma in sup-norm, and letting gamma approach 1 recovers the average-reward equation.

## Algorithm 28

1. In phase k, form confidence sets C_t(s,a), L1 balls around the empirical transition estimates, with radius the root of S L over (1 v T) and L equal to 2 log(4SAT(1+T)/delta).
2. Plan in the extended MDP, whose actions are pairs (a, P) with P a plausible transition vector, and take a policy greedy for the optimistic value function.
3. Follow that policy until the count of some state-action pair doubles.

Each optimistic step costs order S(A + log S): sort v, then assign probability mass greedily. At most SA(1 + log2(n/(SA))) phases occur. Replanning every round can give linear regret (dithering, shown on a two-state deterministic MDP), so the doubling phases are necessary.

## Bounds

- Theorem 38.6: with probability 1 - delta or more the regret is of order D S times the root of A n log(nSA/delta); in expectation it is at most 1 + C D S root(2 A n log n) (an exercise).
- Theorem 38.7: some MDP of diameter at most D forces expected regret of at least C root(DSAn), provided S is at least 3, A at least 2, D at least 6 + 2 log_A S and n at least DSA. The hard instance is a tree with leaf-action pairs of which one has transition probability to the good state 1/2 + Delta, reducing to a bandit with Omega(SA) arms. The upper and lower bounds are separated by a factor of at least the root of DS.
- The best expected n-round reward is no less than n rho* - D, so measuring against n rho* costs nothing important.
- Azar et al. (2017) present an optimistic episodic algorithm with regret about the root of HSAn, an improvement of a root SH factor over an adapted UCRL (reported).

## Practice and failure modes

- Restrict to strongly connected MDPs: UCRL2 has linear regret when some unreachable state pays more than the optimal gain, and any policy that is sublinear across every strongly connected MDP is linear on some MDP containing traps.
- Pick a state that is observable and Markov; adding more state slows learning.
- RiverSwim (Exercise 38.26): the right action moves up with probability 0.3, stays put with 0.6 and falls back with 0.1; reward 1 at state S under right, 0.05 for left in state 1. The chapter reports no results on it.

## Limits

- Without further structure the bounds say nothing for large state spaces; the main text assumes known deterministic rewards and covers just the average-reward setting in depth.
- The ellipsoid-based polynomial time is impractical.
- The chapter says the Agrawal and Jia 2017 proof is not quite correct and that the proof of Theorem 4 in Bartlett and Tewari 2009 is incorrect.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Thompson Sampling and Bandit Regret]] — related (posterior sampling for RL, Strens 2000, is named only in the lineage)
