---
title: Non-Stationary Bandits and Tracking Regret
tags: [data-analytics, bayesian-analysis, concept]
summary: "When the best arm can change, regret is measured against a sequence with at most m-1 changes; plain Exp3 fails, clipping the simplex fixes it with an efficient mirror-descent policy, and no stochastic policy can match the stationary log-regret rate under abrupt changes."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch31-non-stationary-bandits.md
  - data/raw/papers/2026-11-08-auer-2002-nonstochastic-multiarmed-bandit-problem.md
---

# Non-Stationary Bandits and Tracking Regret

*Bandit Algorithms*, ch. 31. The standard regret compares with the best single arm, which is a weak target when the best arm changes.

## The problem and the regret

- Example: two arms, losses y_t1 = I{t <= n/2} and y_t2 = I{t > n/2}. The Exp3 bound is vacuous here, and a uniform-random policy's expected cumulative loss of n/2 is about what the Exp3 guarantee amounts to.
- Tracking regret R_nm is measured against the best sequence from Gamma_nm, the length-n action sequences that change at most m-1 times.
- Exp4 with an expert for each sequence in Gamma_nm has regret at most the root of 2nk log|Gamma_nm|, which is of order root(nmk log(kn/m)); its running time is linear in the number of experts, enormous even for small m. The lower bound of order root nmk applies even to policies told where the changes are, so ignorance of the locations costs only logarithmic factors.

## Clipped mirror descent

Plain Exp3 does not work (an exercise shows R_n2 >= c n on the two-segment problem). The chapter's efficient policy runs online stochastic mirror descent with unnormalised negentropy on the clipped simplex A = P_{k-1} intersected with [alpha, 1]^k, with importance-weighted estimates and a uniform start. Every arm keeps probability at least alpha, so a change can still be discovered. Theorem 31.1 bounds the tracking regret by three terms: alpha n (k-1), then m log(1/alpha) divided by eta, then eta n k over 2.

- m known: alpha equal to the root of m over nk, with eta the root of 2m log(1/alpha) over nk, gives the root of mnk log(nk/m) plus the root of mnk.
- m unknown: alpha equal to the root of 1/(nk), with eta the root of log(1/alpha) over nk, multiplies the regret by a factor of order root m.

## Exp3.S (Auer et al. 2002)

Exp3.S bounds regret against any action sequence, scaled by its hardness H, which is 1 plus the number of arm changes. With alpha = 1/T and a suitably tuned gamma the regret is at most H times the root of KT log(KT), plus 2e root(KT/log(KT)), for every sequence simultaneously. Details of the algorithm are on [[Exp3 Adversarial Bandit Algorithms]].

## Stochastic setting

- Given the change points, a fresh UCB in each interval has regret of order (m + mk/Delta_min) log(n/m) with unit-variance Gaussian rewards, where Delta_min is the smallest gap across all blocks.
- Theorem 31.2 (two Gaussian arms): a policy whose regret on a stationary problem with gap Delta is o(n) has, on some bandit with at most two changes, regret of at least n divided by 22 times that stationary regret. So logarithmic stationary regret forces regret of order n/log n in the worst case against two changes. The stated reason: an algorithm anticipating abrupt change must keep exploring every suboptimal arm to check that nothing changed.
- Discounted UCB (discount factor gamma) and sliding-window UCB (window length tau) both discard old data. No choice of gamma or tau reaches minimax regret of order root(n log n), yet both have empirical backing when the stochastic assumption is true.
- If the means' total variation (the sum over rounds of the largest coordinate change) is at most V, a policy reaches regret of order n^(2/3) times the cube root of V k log k (reported), close to minimax and without knowing V. If arm means drift as reflected Brownian motion, regret is necessarily linear.
- The authors suggest checking whether adding context (for example time of year in ad serving) makes the problem stationary before using a non-stationary algorithm.

## Limits

- No experiments; the chapter's only comparison is an exercise (Exp3, Exp3-IX and the clipped variant, k = 2, n = 1000).
- Regret theorems for discounted and sliding-window UCB are left to Garivier and Moulines 2011, and no change-point detector is described.
- No adversarial algorithm is known that copes with an unknown number of switches at regret of order root(mkn log n).
- Stochastic rewards are assumed Gaussian with unit variance.

## See Also
- [[Follow-the-Regularised-Leader and Mirror Descent]] — prerequisite-for
- [[Thompson Sampling and Bandit Regret]] — related (discounting evidence to track a changing world)
- [[Exp3 Adversarial Bandit Algorithms]] — prerequisite-for (Exp3.S tracks changing sequences)
- [[Exp4 and Oracle-Based Contextual Bandits]] — prerequisite-for (experts over change sequences)
- [[Upper Confidence Bound Bandit Algorithms]] — prerequisite-for (discounted and sliding-window variants)
