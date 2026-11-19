---
title: Upper Confidence Bound Bandit Algorithms
tags: [data-analytics, bayesian-analysis, pattern]
summary: "UCB plays the arm with the highest empirical mean plus a confidence bonus, acting as if the world were as good as plausible; the confidence level sets the variant (horizon-based, anytime, minimax, KL), and each fixes a weakness of the one before."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch01-introduction.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch04-stochastic-bandits.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch07-upper-confidence-bound-algorithm.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch08-ucb-asymptotic-optimality.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch09-ucb-minimax-optimality.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch10-ucb-bernoulli-noise.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch13-lower-bounds-basic-ideas.md
  - data/raw/papers/2026-11-08-auer-2002-finite-time-analysis-multiarmed-bandit.md
---

# Upper Confidence Bound Bandit Algorithms

The optimism principle: choose as though the environment were as favourable as the data allow. The index of an arm is its empirical mean plus an exploration bonus taken from a confidence bound ([[Sub-Gaussian Tail Bounds and Confidence Radii]]). Compared with [[Explore-Then-Commit Bandit Policy]] they need no knowledge of the gaps and work with more than two arms.

## Regret setup

Regret of a policy on a stochastic bandit is n times the best mean minus the expected total reward. Lattimore and Szepesvari's decomposition lemma (Lemma 4.5) states that for a finite or countable action set it equals the sum over arms of the suboptimality gap times the expected pull count, so a policy keeps regret small by playing larger-gap arms proportionally less. Pull counts are random even for a deterministic policy, because each choice depends on random past rewards. Learning means regret grows sublinearly, so R_n / n goes to 0. Pseudo-regret replaces the realised rewards with the means of the chosen arms; the authors argue it filters out reward noise and measures policy skill better than random regret. For stochastic Bernoulli bandits worst-case regret of order sqrt(n) is stated as both unavoidable and achievable.

## UCB(delta), horizon-based

The index is infinite for an unplayed arm (so each arm is tried once), else mu_hat_i + sqrt(2 log(1/delta) / T_i), with T_i the arm's pull count. For a k-armed bandit with 1-subgaussian rewards and horizon n known, delta = 1/n^2 gives (Theorems 7.1 and 7.2):

- instance-dependent: R_n <= 3 sum_i Delta_i + sum over suboptimal i of 16 log(n)/Delta_i;
- worst case: R_n <= 8 sqrt(n k log n) + 3 sum_i Delta_i.

A union bound over the n rounds is the reason delta has to be somewhat below 1/n. The additive sum of gaps cannot be avoided, since any sensible algorithm plays every arm at least once. In the book's experiment (n = 1000, k = 2, unit-variance Gaussian arms with means 0 and -Delta) tuned-per-gap ETC beat UCB only by a small margin (read from a figure).

## Anytime and asymptotically optimal

Replacing log(1/delta) by log f(t) with f(t) = 1 + t log^2 t removes the horizon from the index (Algorithm 6). For 1-subgaussian rewards, Theorem 8.1 gives limsup R_n / log n <= sum over suboptimal arms of 2/Delta_i, the optimal constant (optimality rests on lower bounds from chapters 15 and 16, not covered here). A looser form choosing eps = Delta_i/2 in the finite-time bound does not give that constant. For Gaussian rewards, f(t) = t or something growing more slowly is enough. The authors warn that lower-order terms can dominate in every practical regime, so the asymptotic constant says little about practical performance.

## Minimax: MOSS

MOSS uses the index mu_hat_i + sqrt((4/T_i) log+(n/(k T_i))), with log+(x) = log max{1, x}, and removes the log factor from the worst case: R_n <= 39 sqrt(kn) + sum_i Delta_i for 1-subgaussian rewards and known n (Theorem 9.1). The proof uses a maximal inequality derived from Doob's submartingale inequality and a peeling argument over a geometric grid. Two drawbacks are given:

- On a Gaussian instance with n = k^3, mu_1 = 0, mu_2 = -sqrt(k/n) and mu_i = -1 otherwise, UCB's regret is O(k log k) while MOSS's is Omega(k^2) (stated; the proof is described as delicate and not given).
- MOSS's regret distribution is unstable: on a two-armed Gaussian bandit, delta = 1/(n Delta^2) gives a second moment of failure regret of Omega(n), while delta = (n Delta)^-2 keeps that second moment O(1) while paying a little extra regret (an informal heuristic).

As a milder alternative the authors propose the index with log+(n/T_i), which an exercise has the reader prove matches or beats UCB and achieves O(sqrt(nk log k)) regret without distributional assumptions, and adaptive confidence levels such as optimally confident UCB and AdaUCB. MOSS's asymptotic constant is sum 4/Delta_i, and a modified version with 2 in place of 4 reaches the optimal sum 2/Delta_i (cited to Garivier 2013, no proof).

The minimax target: chapter 13 gives a heuristic two-instance argument that no policy can keep regret below c sqrt(kn) on every Gaussian bandit with unit variance and means between 0 and 1, with the rigorous proof deferred to chapter 15. The second instance is made by lifting the mean of the arm the policy is expected to play least; the argument assumes E[T_1(n)] is about the same under both instances, which is not proven there.

## KL-UCB for Bernoulli rewards

The Bernoulli relative entropy is d(p, q) = p log(p/q) + (1-p) log((1-p)/(1-q)). The Chernoff bound P(mu_hat >= mu + eps) <= exp(-n d(mu + eps, mu)) inverts to a confidence bound, and the KL-UCB index is the largest mu~ in [0, 1] with d(mu_hat_i, mu~) <= log f(t)/T_i, f(t) = 1 + t log^2 t (Algorithm 8). Its asymptotic regret is limsup R_n / log n <= sum Delta_i / d(mu_i, mu*). Since d(mu_i, mu*) >= 2 Delta_i^2 (Pinsker), KL-UCB is never worse than subgaussian UCB with sigma = 1/2, whose constant is sum 1/(2 Delta_i). For small gaps d is about Delta_i^2 / (2 mu_i (1 - mu_i)), so the gain appears when means are near 0 or 1. The interval is asymmetric: with mu_hat = 3/4, n = 10 and 90 per cent confidence the bound a = log(1/delta)/n is about 0.23, where Hoeffding's upper bound is vacuous, and as mu_hat approaches 1 the Hoeffding width stays fixed while the KL width goes to 0. The index has no closed-form inverse; the chapter advises Newton's method. The bound extends to any rewards supported on [0, 1], though not tightly; the CLT does not justify treating a Bernoulli arm as Gaussian with matched variance.

## UCB1 and its relatives (Auer, Cesa-Bianchi, Fischer)

UCB1 uses the bonus sqrt(2 ln n / n_j), with n the plays so far and n_j the arm's plays, for rewards in [0, 1]. Theorem 1: expected regret at most 8 sum over suboptimal arms of ln n / Delta_i plus (1 + pi^2/3) sum_j Delta_j, for every n with no knowledge of the reward distributions. The Lai-Robbins constant is 1/D(p_j || p*) with D >= 2 Delta_j^2, so UCB1's constant 8/Delta^2 falls short of the asymptotic optimum, and 2 cannot be improved on.

- UCB2 (Theorem 2, 0 < alpha < 1, n >= max 1/(2 Delta_i^2)): the leading constant approaches 1/(2 Delta^2) as alpha shrinks, but the additive constant c_alpha diverges as alpha goes to 0.
- UCB1-Normal handles Gaussian rewards whose means and variances are both unknown (Theorem 4), with regret bound 256 (log n) sum sigma_i^2/Delta_i + ...; the proof depends on two conjectures verified only numerically.
- UCB1-Tuned replaces the bonus by sqrt((ln n / n_j) min{1/4, V_j}), with V_j an empirical variance estimate plus sqrt(2 ln t / s). Self-reported: it beat UCB1 by a wide margin in nearly every experiment, comparably to a well-tuned eps_n-greedy and not very sensitive to arm variance, but has no proved bound; UCB2 was similar but always slightly worse, and insensitive to small alpha (alpha = 0.001 used). Setup: seven Bernoulli distributions, 2 arms and 10 arms, 100,000 plays averaged over 100 runs.

## Limits

- UCB(delta) with delta = 1/n^2 needs the horizon; the 1-subgaussian analysis assumes a known constant. Unknown variance and heavy tails are left to exercises.
- Instance-dependent bounds are meaningless if a single gap is tiny; the worst-case bound covers that.
- Optimism does not always work: the book says it fails when an action tells you nothing about itself or tells you about other actions (linear bandits, chapter 25).
- Chapters 7 to 10 have almost no experiments: one two-arm, n = 1000 Gaussian experiment, with runs and seeds not stated; chapters 8 to 10 only suggest simulations as exercises.
- Optimality of 2/Delta_i is asserted through lower bounds deferred to chapters 15 and 16. The Lai-Robbins bound is only cited in chapter 10, and the Omega(k^2) MOSS claim and the chapter-13 lower bound are unproved here.
- The exponential-family result (E[T_i(n)] about log(n)/d_inf + 1/d_min) appears only as an exercise comment; the lower-order term may dominate for all reasonable n.
- Auer et al.: UCB1-Tuned, the best empirical variant, has no regret bound; Theorems 1 to 3 need rewards in [0, 1] and stationary arms; experiments are Bernoulli only with no variance reported in the text.
- The two sources give different constants for UCB: 16 log(n)/Delta_i (1-subgaussian, delta = 1/n^2) against 8 ln n / Delta_i (UCB1, rewards in [0, 1]); the setups differ.

## See Also
- [[Sub-Gaussian Tail Bounds and Confidence Radii]] — prerequisite-for
- [[Explore-Then-Commit Bandit Policy]] — alternative-to
- [[Exp3 Adversarial Bandit Algorithms]] — alternative-to (adversarial rather than stochastic rewards)
- [[Thompson Sampling and Bandit Regret]] — alternative-to (posterior sampling instead of a confidence bonus)
- [[Gaussian Processes and Bayesian Optimisation]] — related
- [[Bandit Regret Lower Bounds]] — related
