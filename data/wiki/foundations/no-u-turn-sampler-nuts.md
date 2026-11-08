---
title: No-U-Turn Sampler (NUTS)
tags: [foundations, pattern]
summary: NUTS extends Hamiltonian Monte Carlo so the number of leapfrog steps is chosen per iteration by doubling a trajectory until it turns back, and dual averaging tunes the step size during burn-in.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-hoffman-2011-no-u-turn-sampler.md
---

# No-U-Turn Sampler (NUTS)

Hamiltonian Monte Carlo (HMC) needs a step size and a number of leapfrog steps L, and its efficiency depends on both. Hoffman and Gelman's 2011 preprint proposes NUTS, which drops the hand-set L, and pairs it with Nesterov dual averaging so the step size is also set automatically. The figures below are the authors' own (self-reported) and come from one preprint.

## Mechanism

- **Doubling.** Each iteration builds a binary tree of states by doubling the trajectory (1, 2, 4, ... steps), choosing forward or backward in time at random at each doubling. A slice variable decides which visited states are eligible.
- **U-turn stop rule.** Doubling halts when, for any balanced subtree, the line from its leftmost to its rightmost state has a non-positive dot product with the momentum at either end, meaning the fictional particle has started to double back.
- **Why a tree.** The paper states that the simpler rule (stop as soon as the dot product goes negative along a single path) is not time-reversible, so it is not guaranteed to converge to the target distribution. Building a balanced tree is what restores correct sampling.
- **Memory.** A naive implementation keeps every visited state, which grows exponentially with the number of doublings. The efficient version keeps only a number of states linear in the tree depth, by preferring the newer half-tree with an acceptance-style probability. The gradient cost per iteration is roughly the number of states visited.
- **Acceptance statistic.** There is no single accept/reject step. The adaptation statistic is the average acceptance probability HMC would assign to the states visited in the final doubling.

## Step-size adaptation

Dual averaging runs during burn-in (M_adapt iterations) and the step size is then frozen at the averaged iterate. Reported settings: gamma = 0.05, t0 = 10, kappa = 0.75 (self-reported), used for all experiments but hand-picked on the stochastic volatility model. An initial-step heuristic doubles or halves the step until a Langevin proposal's acceptance crosses 0.5, and the shrinkage target is log(10 x initial step), which biases the search toward larger, cheaper steps. The paper reports that the averaged step size settles after a few hundred iterations on three models, while stochastic volatility takes longer.

## Reported results (self-reported)

Setup: the metric is effective sample size (ESS) per gradient evaluation. HMC is represented by its best result over 10 trial simulation lengths. Each run is 2000 iterations (the first 1000 for burn-in and adaptation), with 10 seeds, on four targets (a 250-D multivariate normal, a 25-parameter German-credit logistic regression, a 301-parameter hierarchical logistic regression, and a 3001-parameter stochastic volatility model).

- On the two logistic regressions NUTS roughly matched tuned HMC; on the multivariate normal and stochastic volatility targets it was about 3x better in ESS per gradient (self-reported, delta = 0.6).
- The best HMC simulation length varied about 100x across the four problems (0.17 to 17.62), which is why HMC needs preliminary tuning runs (self-reported).
- Best target acceptance rate delta was about 0.65 for HMC and about 0.6 for NUTS, with NUTS results insensitive anywhere in 0.45 to 0.65 (self-reported, delta swept from 0.25 to 0.95).
- Informal demo on a 250-D correlated normal: random-walk Metropolis and Gibbs, each given 1,000,000 iterations or sweeps, left parts of the space unexplored, while NUTS ran 2,000 iterations (delta = 0.5). Plotted on the first two dimensions only.
- Scaling with dimension D is cited from earlier theory, not measured here: HMC cost per independent sample grows like D^1.25, random-walk Metropolis like D^2.

Scope: like HMC, NUTS applies to continuous variables without constraints and a smooth target. Bounded parameters need a transformation, and discrete ones need marginalising or a Gibbs step. If a trajectory enters an impossible region, HMC spends the full path there, while NUTS ends the doubling early and samples from what it has.

## Limits

- Compared only with basic HMC, not its extensions; only an identity mass matrix was used, and mass-matrix adaptation is not in the paper.
- Adaptation constants were hand-tuned on one model and the authors say they may not transfer to other statistics or samplers. Adaptation is weakest on the stochastic volatility model.
- Four targets, none with a funnel or multimodal geometry; no divergence diagnostics discussed.
- The authors speculate, untested, that some of the improvement over HMC could come from averaging acceptance over many states instead of making one accept or reject decision, rather than from path length alone.
- Cost is counted in gradient evaluations, not wall-clock time. The extraction notes the ESS estimator truncates autocorrelation at 0.05, a cutoff the authors call somewhat arbitrary.
- The extraction notes the paper's own delta values (0.65 in one figure, 0.5 in another) differ from its recommendation, and that current libraries use different defaults; that is the extractor's knowledge, not the paper's.

## See Also

- [[MCMC and Metropolis Sampling]] — prerequisite-for
- [[Divergences and Non-Centred Parameterisation]] — related (the funnel geometry this paper does not test)
- [[Prior Choice and Prior Predictive Checks]] — related
