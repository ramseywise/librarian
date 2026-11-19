---
title: Exp3 for Adversarial Linear Bandits
tags: [data-analytics, bayesian-analysis, concept]
summary: "Exponential weights over a finite action set, with least-squares loss estimates and an exploration mixture, gets regret that grows with dimension d and log of the action count instead of the action count; the same chapter group relates this adversarial model to stochastic linear bandits."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch27-exp3-adversarial-linear-bandits.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch29-relation-between-adversarial-stochastic-linear-bandits.md
---

# Exp3 for Adversarial Linear Bandits

In an adversarial linear bandit the learner picks an action A_t in a set A of vectors in R^d and sees only the scalar Y_t = <A_t, y_t>, never the loss vector y_t. Regret is measured against the best fixed action in hindsight. Lattimore and Szepesvari (*Bandit Algorithms*, ch. 27) adapt exponential weights so that information is shared across actions.

## Algorithm

Algorithm 15 keeps exponential weights over the finite action set, with a loss estimate for every action built from one observation:

- Build a loss-vector estimate by least squares: the inverse of the matrix Q_t (the P_t-weighted sum of outer products of actions) applied to A_t Y_t. Conditional on the history it is unbiased.
- Sample from P_t = gamma * pi + (1 - gamma) * (exponential weights on the cumulative estimates), where pi is an exploration distribution.
- Take pi from the Kiefer-Wolfowitz theorem, which gives g(pi) at most d. Mixing it in keeps Q_t invertible and the estimates bounded. Dropping the mixture (gamma = 0), which is fine for finite-armed Exp3, can give very poor regret here.

Setup: k actions, n rounds, losses bounded by 1 in absolute value for every action. Take gamma equal to eta times g(pi), and eta equal to the square root of (log k divided by (2 g(pi) + d) times n). The regret is then at most twice the square root of 3dn log k: it scales with the logarithm of k and the square root of dn, not with k. The proof rests on the estimates' second moment being at most d. A direct implementation costs order kd + d^3 per round, plus the one-off computation of pi.

## Large and continuous action sets

- Replacing a continuous action set with a finite cover C (log of its size at most d log(6dn)) gives regret of order d times the root of n log(nd), but the cover is exponentially large in d, so this is intractable.
- A continuous version of exponential weights, again with Kiefer-Wolfowitz exploration and run over a compact convex set of positive volume, has regret 2d times the root of 3n(1 + log+(2n/d)). The authors caution that, with the parameters the theory justifies, the samplers for convex bodies are hardly practical.
- Hypercube corners give |A| = 2^d, so such combinatorial sets need different algorithms ([[Combinatorial Bandits and Follow-the-Perturbed-Leader]]).
- The square-root dependence on the horizon is unimprovable. Dependence on d that is linear is suboptimal for some action sets (the unit ball) and optimal for others; [[Follow-the-Regularised-Leader and Mirror Descent]] reaches the root of dn log n on the unit ball.

## Relation to stochastic linear bandits (ch. 29)

- A stochastic linear bandit on a fixed action set becomes an adversarial one if the adversarial policy is run on every action extended by a constant coordinate 1 (dimension d+1), with the adversary's vector made of theta and the noise term. The loss must stay within [-1, 1] almost surely; Gaussian noise is handled by truncation at 1 plus the root of 4 log n, leaving failure probability at most 1/n.
- On the unit ball the extended action set is no longer a ball, which strengthens the adversary; this fits the stochastic lower bound of order d root n, set against the adversarial bound of order root(dn log n).
- In a stochastic model with parameter noise (theta_t drawn independently from a fixed distribution nu), the noise variance depends on the action: A_t' Sigma A_t. With uniform play on the sphere and nu supported on the unit sphere the expected noise variance is 1/d, where the standard 1-subgaussian model has 1; the chapter says this explains the gap of a factor root d. If the adversary's loss vectors may lie on a sphere of radius root d, regret again grows linearly in d.
- The adversarial model includes parameter-noise stochastic bandits as a special case; the latter can be easier since the noise restricts how far the adversary can set the signal-to-noise ratio.
- With changing action sets in the stochastic setting, LinUCB's regret against the per-round best action is about d root n. For the corresponding adversarial benchmark over continuous parameter sets no algorithm with small regret is known, so the authors favour stochastic algorithms such as LinUCB there.
- When it is unclear that the environment is stochastic, they suggest applying the adversarial algorithm to the unmodified action set with its tuning adjusted.

## Limits

- Both chapters are theory with no experiments; the results are regret upper bounds or reductions.
- Algorithm 15 requires a finite action set, whose size k can be exponential in d, and the exploration distribution must be computed; any pi whose g(pi) is bounded will do. The action set must span R^d and losses must be bounded; exercises relax these.
- The ch. 29 reduction assumes bounded losses and an existing minimiser.
- How action-set geometry and the adversary's choices affect regret is poorly understood beyond l_p balls. A meaningful adversarial regret for changing action sets is open, with no efficient algorithm known, and the authors say they are unaware of any systematic treatment of parameter noise for stochastic bandits.

## See Also
- [[Follow-the-Regularised-Leader and Mirror Descent]] — alternative-to (a sqrt(d) better rate on the unit ball)
- [[Combinatorial Bandits and Follow-the-Perturbed-Leader]] — extends (hypercube action sets)
- [[Thompson Sampling and Bandit Regret]] — related (Bayesian regret for linear bandits matches LinUCB)
- [[Exp3 Adversarial Bandit Algorithms]] — prerequisite-for (the finite-armed case)
- [[G-Optimal Design and Phased Elimination]] — prerequisite-for (the Kiefer-Wolfowitz exploration distribution)
- [[LinUCB and Linear Bandit Confidence Ellipsoids]] — alternative-to (the stochastic linear approach)
