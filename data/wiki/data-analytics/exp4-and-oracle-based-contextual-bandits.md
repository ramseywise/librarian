---
title: Exp4 and Oracle-Based Contextual Bandits
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Contextual regret competes with the best context-to-action policy in hindsight; Exp4 gets sqrt(2nk log M) over M experts but needs memory per expert, and a coordinate-descent method calls a classification oracle sublinearly often while keeping near-optimal regret."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bandit-algorithms-ch18-contextual-bandits.md
  - data/raw/papers/2026-11-08-auer-2002-nonstochastic-multiarmed-bandit-problem.md
  - data/raw/papers/2026-11-08-agarwal-2014-taming-monster.md
---

# Exp4 and Oracle-Based Contextual Bandits

## Contextual regret and experts

Chapter 18 of *Bandit Algorithms* defines contextual regret as the shortfall against the best policy that may depend on context, chosen in hindsight: for each context, the best single arm over the rounds where that context occurred, summed over contexts and averaged. It generalises the problem to bandits with expert advice: M experts each announce a distribution over the k arms every round, and regret is measured against the best expert. A contextual bandit is the case where the experts are fixed maps from contexts to arms. The authors advise picking the competitor class to balance how meaningful the regret is against what it costs to learn, a larger class meaning larger regret.

Exp4 keeps a distribution Q over experts, plays P_t = Q_t E(t), builds an importance-weighted reward estimate for each arm, propagates it to the experts through E(t), and reweights Q exponentially. Setting gamma to 0 and eta to the root of 2*log(M)/(n*k), its expected regret against M oblivious experts is at most the root of 2*n*k*log(M), for adversarial rewards in [0,1] and known horizon n. Consequences given in the chapter:

- One anytime Exp3 per context (finite context set C, equally frequent contexts) has regret at most 2*sqrt(n*k*|C|*log k), a bound that is empty up to n = 4*k*|C|*log k, so the chapter suggests disregarding context while n is small.
- Exp4 over all functions from C to arms (M = k^|C|) recovers sqrt(2nk|C| log k). Over any finite policy class Phi the bound becomes sqrt(2*n*k*log|Phi|), even when contexts are infinitely many.
- With a learning rate that varies by round (eta_t from log M over E*_t), regret is at most a constant times sqrt(E*_n*log M); E*_n (the sum over rounds and arms of the largest expert probability) is at most n min(k, M) and measures how much the experts disagree. The proof is left as an exercise.

Auer et al. (2002), where Exp4 was introduced, give N experts that each output a distribution over the K arms and may depend on the full history. Their Theorem 7.1 bounds the gap to the best expert by (e-1)*gamma times the best expert's gain plus K ln N / gamma, which tunes to order sqrt(K T ln N), so the dependence on N is only through its logarithm (self-reported). The algorithm requires the uniform expert, one that gives every arm weight 1/K each round, to be among the experts; a footnote weakens this to the uniform expert lying in the convex hull of the experts. Per-round computation scales linearly with N. The chapter 18 bound matches their theorem with a slightly smaller constant.

For stochastic i.i.d. contexts and rewards with an argmax (cost-sensitive classification) oracle, explore-then-commit reaches regret of order n^(2/3) (Exercise 18.8); the chapter reports that Agarwal et al. (2014) reach about sqrt(nk log|Phi|) in polynomial time.

## Taming the Monster

Agarwal et al. (2014) call the algorithm ILOVETOCONBANDITS. Actions are drawn from a smoothed mixture over policies, Q^mu(a|x) = (1 - K mu) times the Q-mass of policies choosing a, plus mu, so each action has probability at least mu. At the end of each epoch it solves an optimisation problem with a regret constraint plus an inverse-propensity variance constraint for every policy, using coordinate descent, one oracle call per iteration, outputting a sparse distribution over policies. The oracle (AMO) takes context and reward-vector pairs and returns the policy in the class with the largest summed reward, a cost-sensitive classification learner.

All (self-reported), for an i.i.d. contextual bandit with finite policy class Pi, K actions and rewards in [0,1], assuming the optimisation problem is solvable each epoch:

- With probability at least 1-delta, regret after T rounds is of order sqrt(K*T*ln(T|Pi|/delta)) plus K*ln(T|Pi|/delta) (Theorem 2), described as optimal up to logs.
- Under the warm-start epoch schedule (epochs ending at 3 and 5, then tau_m = m^2) total oracle calls are about sqrt(K*T/ln(|Pi|/delta)), spread over O(sqrt(T)) solves.
- A lower bound: a constructed instance forces any distribution meeting the variance constraint to have a support at least of the order of the root of K*tau_M over ln(|Pi|*tau_M/delta), so sparser distributions cannot reduce oracle calls further.

The experiment runs Online Cover, which maintains n online cost-sensitive policies and trains all of them on doubly robust examples, on RCV1 (CCAT, 47,152 TF-IDF features, linear representation) converted from supervised to contextual bandit. Progressive validation loss (each example scored before the learner updates), best hyperparameters:

| Method | Loss |
|---|---|
| Supervised, full labels | 0.051 |
| Online Cover (best at cover size n=1) | 0.053 |
| Bagging, 16 bags | 0.059 |
| Explore-first, 2 x 10^5 exploration examples | 0.081 |
| LinUCB, random projection to 1,000 dimensions | 0.128 |
| LinUCB, diagonal covariance approximation | 0.137 |
| epsilon-greedy, epsilon = 0.1 | 0.148 |

On RCV1, LinUCB needed roughly 212,000 seconds (59 hours) where Online Cover needed 12 seconds, and the diagonal version about an hour. Online Cover runs at under 2.3 times the supervised learner's time (12 s versus 5.3 s). Compare [[LinUCB and Linear Bandit Confidence Ellipsoids]] for the linear-model alternative.

## Limits

- Auer et al.: rewards must lie in [0,1]; the paper has no experiments, and Exp4's bound is on weak regret against the best fixed expert. The extraction read its formulas from page images because the text layer dropped the math.
- Chapter 18 centres on the k-armed adversarial model, with stochastic contextual bandits only in notes and exercises. It treats no linear contextual bandit or LinUCB. Exp4 costs order M memory and order M+k time per round, which is impractical when M or k is large. Experts are assumed oblivious (the non-oblivious case only through a weaker regret). High-probability and lower bounds are not developed, and there are no experiments.
- Agarwal et al.: the analysis covers the importance-weighted algorithm, whereas the experiment runs Online Cover on a doubly robust estimator; the authors defer analysing it.
- One dataset (RCV1, converted), no repeats, seeds or error bars; hyperparameters were searched on the data they are reported on. The best cover size is n=1, so the cover is barely exercised, and the authors observe that a little decaying uniform sampling may already be enough exploration.
- Excluding the oracle, computation still scales as (KT) to the power 1.5, up to logs. The guarantees assume contexts and rewards are i.i.d., rewards lie in [0,1], and the policy class is finite (extending to VC classes is said to be simple). LinUCB ran only after a random projection down to 1,000 dimensions.

## See Also
- [[Thompson Sampling and Bandit Regret]] — related (the context-free bandit; neither page depends on the other)
- [[Exp3 Adversarial Bandit Algorithms]] — prerequisite-for (Exp4 reuses Exp3's importance-weighted exponential weighting over experts)
- [[LinUCB and Linear Bandit Confidence Ellipsoids]] — alternative-to (linear rewards instead of a policy class)
- [[Counterfactual Evaluation with Inverse Propensity Scoring]] — prerequisite-for (the inverse-propensity estimator inside the optimisation problem)
- [[Bandit Regret Lower Bounds]] — related
