---
title: LinUCB and Linear Bandit Confidence Ellipsoids
tags: [data-analytics, bayesian-analysis, pattern]
summary: "LinUCB serves the arm whose upper confidence bound from a ridge regression is highest, with an ellipsoid confidence set that gives d*sqrt(n) regret for linear rewards; a news-recommendation deployment, a per-coordinate trick for sparse parameters and a self-normalised bound for adaptive actions complete the picture."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-li-2010-contextual-bandit-news-recommendation.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch19-stochastic-linear-bandits.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch20-confidence-bounds-least-squares-estimators.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch23-stochastic-linear-bandits-sparsity.md
---

# LinUCB and Linear Bandit Confidence Ellipsoids

A feature map turns a context and an action into a vector, so that mean reward is an inner product with an unknown parameter. In the stochastic linear bandit of *Bandit Algorithms* (ch. 19), the learner picks an action A_t from a decision set in R^d each round and receives <theta*, A_t> plus 1-subgaussian noise. The chapter motivates the feature map with the tabular contextual bandit, where, with M contexts and k actions, worst-case regret is at least of order sqrt(nMk). It adds that the regret definition makes sense only if the learner's choices do little to shape later contexts.

## The algorithm

LinUCB (also called LinRel or OFUL in the chapter's terms) acts optimistically: it plays the action with the largest upper bound over a confidence set C_t that contains theta*. The estimator is regularised least squares, theta_hat = V^-1 times the sum of A_s X_s, with V = lambda I plus the sum of A_s A_s^T. For a small finite action set the choice is

`A_t = argmax_a <theta_hat, a> + sqrt(beta_t) * ||a||_(V^-1)`

so the bonus is the arm's length in the inverse covariance norm. Li et al. (2010) write the same rule per arm with a per-arm matrix built from that arm's logged features plus an identity, and a multiplier alpha on the bonus.

The chapter's practical advice: keep lambda above zero so the estimator exists even when actions do not span R^d, and maintain the inverse with Sherman-Morrison updates, costing order k*d^2 per round. With a fixed large action set it suggests running in phases that end when log det V grows by log(1+eps).

## Regret

Under the chapter's Assumption 19.1 (nondecreasing beta, mean-reward range at most one, actions of norm at most L, theta* in every C_t with probability 1-delta), pseudo-regret stays below the square root of 8*n*beta_n times the log of the determinant ratio of V_n to V_0, and that log ratio is itself at most d times log(1 + n*L^2/(d*lambda)). The proof runs through the elliptical potential lemma, which caps the summed capped squared norms of the actions at twice that log ratio. Choosing delta = 1/n gives expected regret of order d sqrt(n) log(nL). The chapter notes that the Cauchy-Schwarz step often loses a logarithm.

For a finite action set of at most k actions, the chapter reports algorithms with regret of order sqrt(d n log^3(nk)); see [[G-Optimal Design and Phased Elimination]] for a design-based route that shaves a factor of d^(1/2) when the set is fixed.

## Why the confidence set holds for adaptive actions

Chapter 20 supplies the radius. A covering argument over the unit sphere (at most (3/eps)^d points) gives a fixed-design set whose radius is twice the root of 2 times (d*log 6 plus log(1/delta)), but it fails when a bandit algorithm picks the actions. The self-normalised bound (Theorem 20.5) holds for all t at once with conditionally 1-subgaussian noise and adaptive actions: the distance from theta_hat to theta* in the V_t(lambda) norm is below sqrt(lambda) times ||theta*||_2, plus the root of 2*log(1/delta) plus the log of det V_t(lambda) divided by lambda^d. It is proved by the method of mixtures, which integrates the exponential supermartingale against a probability measure and keeps a non-negative supermartingale. The book advises the log-determinant form over the looser trace form. Note 2 says that with lambda = 1 the radius is close to what a fixed design would give, off by a root-log-n factor, and the extra root-d is unavoidable. Note 3 says that bounding the width at one input x via a confidence set over the entire parameter costs an additional root-d, and an adaptive design can force order d.

## LinUCB on a news front page

Li et al. (2010) apply the rule to article choice on the Yahoo! Front Page Today Module, fitting one ridge regression for each arm (disjoint) or letting arms share some coefficients (hybrid). They score policies offline with a replay evaluator: an event counts only when the evaluated policy would have chosen the arm that was logged. When logging is uniform random and events are i.i.d., the evaluator is unbiased, and keeping T events takes K*T logged ones on average (Theorem 1, a claim). See [[Counterfactual Evaluation with Inverse Propensity Scoring]] for the general reweighting version.

Results, all (self-reported), on the May 2009 logs (over 33 million events), evaluation week 3-9 May, as CTR relative to random traffic:

| Setting | Result |
|---|---|
| Deployment bucket, 100% of data | disjoint CTR 1.795, a 12.5% lift over epsilon-greedy; hybrid CTR 1.73, a lift of 8.4% |
| Learning bucket, 100% of data | lift 24.2% disjoint, 25.4% hybrid |
| 1% of data | hybrid has the largest lifts: 20.1% (deployment), 27% (learning) |
| Best fixed article in hindsight (context-free) | CTR 1.615 |

Using user features alone gave about 10% lift over epsilon-greedy for the seg, disjoint and hybrid variants. One article's CTR rose from 1.31 to 3.03 (132%) under the personalised policy (the paper's Figure 3(c): disjoint models, learning bucket, full data). Across five user clusters, about 85% of users have a top membership weight over 0.5, and about 40% over 0.8.

## Sparse parameters

Chapter 23 asks how to avoid paying in d when theta has few nonzeros. On the hypercube action set, selective explore-then-commit (SETC) explores each coordinate with Rademacher actions and commits to its sign once the confidence interval excludes zero, so zero coordinates cost nothing; its regret depends on the nonzero count times sqrt(n log n) rather than d, without knowing the sparsity (horizon n must be known). For general action sets, OLR-UCB converts the regret bound of an online linear regression predictor into an ellipsoid; with Gerchinovitz's sparse predictor it gets regret of order sqrt(d n m0) times log factors, which still depends on d, and the predictor is not computationally efficient. The matching lower bound is on [[Bandit Regret Lower Bounds]].

## Limits

- The regret bound is a worst-case one that barely reflects theta* or the geometry of the action set, and instance-dependent versions remain open. It says nothing for very large or infinite d, and is within logs of the lower bound only when the action set is infinite or exponentially large.
- The joint maximisation over the action and the parameter is bilinear and tractable only in special cases. The noise is fixed at 1-subgaussian and the bound on ||theta*|| is assumed known.
- Li et al.: the logging policy must be uniform random with i.i.d. events; each setting is one run with no confidence intervals; absolute CTRs are withheld and the data are proprietary. Tuned alpha and epsilon values are not printed.
- The hybrid derivation is deferred, and the regret bound O~(sqrt(KdT)) is claimed as adapted from earlier work, not proved there. Only 6-dimensional cluster features were tested, so the authors say linucb (disjoint) cannot be separated from ucb (seg) without more diverse features. Changes in user interests over time are ignored.
- Chapter 23 has no experiments. OLR-UCB needs the sparsity bound and norm bound in advance, no algorithm gets the sparse rate for all sparsity levels at once, and SETC is limited to the hypercube. The garbled formula for the OLR-UCB bound was read from the PDF by the extractor.
- Chapter 20 is theory only; the covering analysis presumes lambda of zero, independent noise and a deterministic V_t.

## See Also
- [[Thompson Sampling and Bandit Regret]] — prerequisite-for (the context-free bandit this builds on)
- [[G-Optimal Design and Phased Elimination]] — alternative-to (design-based elimination for a fixed finite action set)
- [[Bandit Regret Lower Bounds]] — related (lower bounds for linear bandits)
- [[Exp4 and Oracle-Based Contextual Bandits]] — alternative-to (contextual bandits over a policy class)
- [[Counterfactual Evaluation with Inverse Propensity Scoring]] — related (the replay evaluator is the uniform-logging case)
