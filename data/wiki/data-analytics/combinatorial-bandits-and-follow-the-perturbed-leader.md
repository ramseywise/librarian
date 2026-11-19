---
title: Combinatorial Bandits and Follow-the-Perturbed-Leader
tags: [data-analytics, bayesian-analysis, concept]
summary: "A combinatorial bandit picks a subset of d components; with semi-bandit feedback mirror descent or follow-the-perturbed-leader with a geometric-resampling estimator gets regret of order sqrt(m d n) using one linear-optimisation oracle call per round."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch30-combinatorial-bandits.md
---

# Combinatorial Bandits and Follow-the-Perturbed-Leader

A combinatorial bandit is a linear bandit whose actions are binary vectors of length d, each with at most m ones (*Bandit Algorithms*, ch. 30). Examples in the chapter: online shortest path (edges are coordinates), ranking or selecting m of d ads (order plays no role), and a multitask bandit where one coordinate is picked per part and only the aggregate loss is seen.

## Feedback models

- **Bandit feedback:** only <A_t, y_t> is seen. Applying Exp3 for linear bandits gives regret of twice m times the root of 3dn log|A|, a factor m worse than the standard linear bound; the resulting m^(3/2) dependence is reported as tight (Cohen et al. 2017).
- **Semi-bandit feedback:** the vector (A_t1 y_t1, ..., A_td y_td), equivalent to seeing y_ti for every chosen component. It removes the m^(3/2) penalty.

## Algorithms (losses in [0,1]^d, regret over n rounds)

- **Mirror descent with unnormalised negentropy** (Algorithm 18, semi-bandit): divide each observed coordinate loss by that coordinate's mean play probability, then update over the convex hull of A. Regret is the root of 2nmd(1 + log(d/m)) when eta is the root of 2m(1 + log(d/m)) over nd. A reported worst-case lower bound for semi-bandits, of order root dnm for large n and m at most d/2, is matched by mirror descent with another potential.
- **Perturbed-leader method** (Algorithm 19, called FTPL below): draw a perturbation Z_t and play the action maximising the inner product with Z_t minus eta times the estimated cumulative loss. The unknown reciprocal 1/P_ti is replaced by a geometric random variable K_ti whose mean it is, giving the estimate min(beta, K_ti) times the observed coordinate loss, so no closed-form probability is required. With a Laplace-type perturbation (density proportional to exp of minus the l1 norm), beta = ceil(1/(eta m)) and eta m at least 1, the regret is m times the root of 2(1 + e^2) n d (1 + log d). The expected largest of d such coordinates is a harmonic sum, at most 1 + log d.
- Over n rounds FTPL needs order nd oracle calls in expectation, or order beta n d in the worst case when the geometric draws are capped at beta.
- For m-sets the Hessian's off-diagonal entries are non-positive, which improves the m-dependence to the root of m (an exercise); this fails for general sets, as a shortest-path counterexample shows.

## When Exp3 or mirror descent is not enough

Neither is tractable for arbitrary action sets: a repeated travelling-salesman problem is a combinatorial bandit, and an efficient learner with regret of order n^p for some p below 1 would approximate it. For shortest path with semi-bandit feedback the chapter points to Exp3 over paths with weight pushing (Takimoto-Warmuth, Gyorgy et al.); for the multitask case it suggests Exp3 or Exp3-IX per bandit.

## Limits

- Efficient algorithms are given only for semi-bandit feedback; there is no general FTPL result for bandit feedback.
- FTPL relies on an exact or approximate oracle for linear minimisation over the action set.
- Regret bounds only; no experiments, and the stochastic setting is only in the notes.

## See Also
- [[Exp3 for Adversarial Linear Bandits]] — prerequisite-for
- [[Follow-the-Regularised-Leader and Mirror Descent]] — prerequisite-for
- [[TopRank and Click Models for Ranking Bandits]] — related (adversarial document-based ranking reduces to a combinatorial semi-bandit)
- [[Exp3 Adversarial Bandit Algorithms]] — prerequisite-for
