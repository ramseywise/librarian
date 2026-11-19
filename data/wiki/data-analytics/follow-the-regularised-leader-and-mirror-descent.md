---
title: Follow-the-Regularised-Leader and Mirror Descent
tags: [data-analytics, bayesian-analysis, concept]
summary: "Two potential-based update rules for online linear optimisation: choosing the potential to fit the action set's geometry recovers exponential weights on the simplex and gives an efficient sqrt(d)-better adversarial linear bandit algorithm on the unit ball."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch28-follow-regularised-leader-mirror-descent.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch26-foundations-convex-analysis.md
---

# Follow-the-Regularised-Leader and Mirror Descent

Both algorithms are defined by a convex (usually Legendre) potential F, also called the regulariser, and a learning rate eta (*Bandit Algorithms*, ch. 28).

- **Mirror descent:** the next point minimises eta times the inner product with the latest loss plus the Bregman divergence D_F from the current point, starting at the minimiser of F. Implementation is two-stage: an unconstrained step in the dual space through the inverse of the gradient of F (the mirror map), then a Bregman projection onto A.
- **Follow-the-regularised-leader (FTRL):** the next point minimises eta times the cumulative past loss, plus F; that is, the action best in hindsight once the loss is regularised.
- They give the same iterates only when F is Legendre, its domain lies within A and eta is constant.
- Unregularised follow-the-leader has linear regret on adversarial sequences, which is why the regulariser is used.

## Preliminaries (ch. 26)

- The Bregman divergence D_f(x, y) measures how far f(x) lies above the tangent approximation at y. It is non-negative, zero when x = y and convex in x, but it is not symmetric and has no triangle inequality.
- For f equal to half the squared norm it is half the squared Euclidean distance; for the unnormalised negentropy, on the simplex, it is relative entropy.
- The Bregman projection of x onto A is the point of A with the smallest divergence D_f(y, x). For negentropy on the simplex, projecting y gives y divided by its l1 norm (Exercise 26.11b).
- The chapter's key inequality bounds the inner product of x - y with a vector u, less D_f(x, y)/eta, by (eta/2) times the squared norm of u in the inverse-Hessian norm at some point between x and y.
- With a Legendre f, constrained minimisation over a closed convex A gives the same point as projecting the free minimiser onto A in the Bregman sense.
- The chapter states these facts without proofs.

## Choosing the potential

| Action set | Potential | Result (setup) |
|---|---|---|
| Unit ball, full information | F = 1/2 ||a||^2 | eta = sqrt(1/n), regret at most sqrt(n); online projected gradient descent is this case |
| Simplex, losses in [0,1]^d | unnormalised negentropy | eta = sqrt(2 log(d)/n), regret at most sqrt(2 n log d); the update is exponential weights |
| Simplex, same losses | Euclidean | rate O(sqrt(nd)) instead of O(sqrt(n log d)): the wrong potential costs a factor sqrt(d/log d) |

With bandit feedback, feed the update an unbiased importance-weighted loss estimate and play a random action with the iterate as its mean (Algorithm 16). Exp3 follows from negentropy mirror descent on the simplex, with tuned-eta regret at most sqrt(2 n k log k) (an exercise).

## FTRL on the unit ball

On the unit ball, against adversarial linear losses of norm at most 1, Algorithm 17 uses the potential minus log(1 - norm of a) minus the norm, an estimator proportional to d times A_t times the observed loss over (1 - norm of the iterate), and a ball shrunk to radius 1 - 2 eta d, which stops the estimator's variance blowing up near the boundary. With eta the root of log n over 3dn the regret is at most twice the root of 3nd log n. That improves on the continuous exponential-weights bound of order d root(n log n) by a factor of root d ([[Exp3 for Adversarial Linear Bandits]]).

Price of bandit information: on the unit ball an extra sqrt(d log n) over full information; on the simplex similar up to logs; in general as large as Theta(d). For k-armed adversarial bandits, FTRL with the potential minus twice the sum of square roots of the coordinates (INF) has regret at most the root of 8kn (an exercise, from Audibert and Bubeck 2009).

## Guidance from the chapter

- Pick a potential suited to the action set: Euclidean for the ball, negentropy for the simplex.
- If the horizon is not known, shrink the learning rate over time; the chapter generally prefers FTRL to mirror descent in that case.

## Limits

- The chapter is theory only: no experiments, empirical comparison or compute figures.
- Nothing tells you which potential to use, especially for bandits (Note 6), and the dependence of regret on dimension is poorly understood for general action sets.
- Guarantees for non-oblivious adversaries do not carry over to bandit feedback; that regret needs empirical-process tools and is of order root n only if the variance is of order n.
- Tuning eta in the unit-ball algorithm needs the horizon n.

## See Also
- [[Exp3 for Adversarial Linear Bandits]] — alternative-to (continuous exponential weights, a sqrt(d) worse rate on the unit ball)
- [[Combinatorial Bandits and Follow-the-Perturbed-Leader]] — extends (mirror descent and FTPL on the hypercube)
- [[Non-Stationary Bandits and Tracking Regret]] — extends (clipped-simplex mirror descent)
- [[Thompson Sampling and Bandit Regret]] — related (the Bayesian adversarial analysis uses the same potentials)
- [[Exp3 Adversarial Bandit Algorithms]] — prerequisite-for
