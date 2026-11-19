---
title: Thompson Sampling and Bandit Regret
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Thompson sampling draws one sample from each arm's posterior and pulls the highest, so exploration is automatic and fades with evidence; regret measures the cost, and which rule wins depends on the gaps and horizon, so simulate your own."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--03-priors-and-bandits.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--04-bayesian-ab-testing.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch03-statistical-experiments-significan.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch36-thompson-sampling.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch34-foundations-bayesian-learning.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch35-bayesian-bandits.md
  - data/raw/papers/2026-11-07-riquelme-2018-deep-bayesian-bandits.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch02-multi-armed-bandits.md
---

# Thompson Sampling and Bandit Regret

An A/B test is a bandit that explores uniformly until a fixed N and then exploits. A bandit reallocates traffic as it learns.

## Algorithm

Each round: draw X_b from each arm's Beta(1 + wins_b, 1 + losses_b); pull the arm with the largest draw; update that arm. Uncertain arms yield widely spread draws, so they still win sometimes; losers are chosen at a decreasing rate, never discarded. With true rates 0.85, 0.60, 0.75, 1,000 pulls gave [926, 26, 48] and posterior sds [0.011, 0.091, 0.061]: just enough learning about the losers to stop paying for more.

## Regret

Regret is the cumulative gap between the best arm's rate and the chosen arm's. Any good strategy's regret grows at least logarithmically in horizon, and Thompson sampling and Bayes-UCB (a rising posterior quantile) both achieve that for binary rewards. Simulated on rates 0.15, 0.20, 0.10 with 300 runs:

| Rule | Regret at 100 | at 500 | at 2000 |
|---|---|---|---|
| random | 5.0 | 24.9 | 100.0 |
| max posterior mean | 2.9 | 8.8 | 28.3 |
| 95% upper bound | 3.3 | 8.6 | 14.6 |
| Thompson | 3.8 | 12.4 | 22.8 |

Random pays at a constant rate. Here the plain 95% bound beat Thompson over this horizon. Do not read it as a ranking: the order depends on gaps and horizon, and 300 runs are noisy. Thompson's appeal is no quantile to choose and direct extension to the variants below.

## Extensions

- Minimise: take argmin of draws.
- Non-stationary arms: decay evidence with a rate below 1 (wins = rate * wins + result). Two arms swapping rates halfway through 4,000 pulls: reward per pull 0.162 with no forgetting, 0.179 with rate 0.99, about 10% more. Forgetting costs a little when the world is stationary.
- Comment ranking: each item an arm with Beta(1 + up, 1 + down); sample a score per item per page load and sort, so new items still get seen (see [[Ranking by Lower Credible Bound]]).

## Bandit or fixed test?

Use a bandit when showing a loser is costly, arms change or there are many. Use a fixed-horizon test when you must report an unbiased effect, make a one-off decision or read guardrail metrics: adaptive allocation starves the early-looking-bad arm, so its estimate stays noisy and tends to stay low. A week-long price test with weekend effects confounds timing with price; a fixed split over whole weeks is the honest answer.

## Book framing of bandits

*Practical Statistics for Data Scientists* (chapter 3) describes a multi-arm bandit as a slot machine with several arms standing in for a multi-treatment experiment, and advises bandits when the goal is the best treatment rather than significance. Its epsilon-greedy rule shows A or B by a fair coin with probability epsilon and otherwise the offer with the best response rate so far; setting epsilon to 1 reproduces an ordinary A/B test and 0 is fully greedy. Its illustration, hypothetical, has arm A winning 10, arm B 2 and arm C 4 after 50 pulls per arm.

## Theory (Bandit Algorithms, ch. 36)

Lattimore and Szepesvari describe Thompson sampling (Algorithm 23) as drawing, every round, one environment from the posterior and playing the action that is optimal there. Three views are equivalent: pick the arm with the posterior probability of being optimal; sample an environment and act optimally for it; with independent arms, sample each mean and take the largest. The conjugate updates behind the arm posteriors, and the Bayesian-regret definition, are on [[Gittins Index and Bayesian Optimal Bandits]]. Exploration comes from randomisation and shrinks as the posterior concentrates.

| Setting | Result (setup) |
|---|---|
| Finite arms, any prior, 1-subgaussian arms with means in [0,1] | Bayesian regret O(sqrt(kn log n)), via the UCB argument together with the fact that, given the history, A* and A_t are identically distributed; an exercise drops the log factor |
| Gaussian arms, unit variance, Gaussian Thompson sampling | lim R_n/log n = sum of 2/Delta_i over suboptimal arms (asymptotically optimal) and worst case R_n <= C sqrt(nk log n); not minimax optimal (Agrawal and Goyal 2013a, reported) |
| Linear bandit, any prior, sub-Gaussian noise | Bayesian regret at most 2 plus twice the root of 2dn times beta^2 times a logarithm whose argument is 1 + n S^2 L^2/d, of order d root(n) times the root of log n log(n/d); same order as LinUCB |
| Bayesian adversarial k-armed bandit, rewards in [0,1], any prior | BR_n <= sqrt(kn log(k)/2) by an information-ratio argument with negentropy; a sqrt potential gives sqrt(2nk) (exercise) |

Contextual linear Thompson sampling needs posterior variance inflated by Theta(d) in the frequentist analysis, losing sqrt(d) against LinUCB, and Hamidi and Bayati show the inflation is necessary (reported); the authors note r = 1 often works well in practice. Linear Thompson sampling takes a single posterior draw plus a linear optimisation; LinUCB must maximise over a confidence set, which is frequently intractable when the action set is large. For finite-armed bandits the authors say Thompson sampling's advantages are limited, while for linear bandits it gains in computation and empirical performance. With a suitable prior, Thompson sampling is asymptotically optimal for one-parameter exponential families (reported), whereas linear Thompson sampling is not.

Experiment 36.1 used two Gaussian arms with means (1/5, 0), unit variance, horizon 2000 and 100,000 runs. Gaussian Thompson sampling's expected regret was 29.9, compared with 23.8 for AdaUCB, and its regret varied far more.

The prior matters: an arm the prior undervalues may never be played, so no data arrives to correct it (unlike classical Bayesian statistics). The authors point to BayesUCB (a posterior quantile as the bound) as an alternative.

For Thompson sampling with a neural network, see [[NeuralLinear Thompson Sampling]], which compares approximate posteriors on contextual bandits. Related bandit pages: [[Best-Arm Identification, Track-and-Stop and Sequential Halving]] (when exploring is free), [[Non-Stationary Bandits and Tracking Regret]] (tracking regret) and [[Follow-the-Regularised-Leader and Mirror Descent]] (adversarial bandits).

## Testbed comparison (Sutton and Barto, ch. 2)

Setup: the 10-armed testbed, 2000 random bandits with q*(a) drawn from N(0,1), unit-variance Gaussian rewards, 1000 steps. Under greedy selection, only about a third of tasks ever settled on the optimal action; epsilon = 0.1 never chose it more than 91% of the time; UCB with c = 2 beat epsilon = 0.1 except in the first k steps; and optimistic greedy (Q1 = +5, alpha = 0.1) started worse than epsilon-greedy but ended better. For exact Bayesian-optimal exploration, with just two actions and two rewards the tree over 1000 steps reaches 2^2000 leaves, and the chapter names the Gittins index and Thompson sampling as the Bayesian approaches.

## Limits

- The Sutton and Barto testbed is stationary, Gaussian and has k = 10; its parameter study (Fig 2.6) is shown only as a plot, and the authors admit these methods fall well short of a satisfying answer to the exploration-exploitation problem.
- The Practical Statistics chapter describes bandit algorithms and Thompson sampling in outline only, with no regret or simulation results.
- The frequentist theorems in Bandit Algorithms assume realisable Gaussian rewards, whereas Agrawal and Goyal's bounds cover rewards in [0,1]. Constants in Thm 36.1 and 36.3 are left unspecified.
- Experiment 36.1 covers only one two-armed instance. The information-theoretic method yields Bayesian bounds rather than algorithms for the adversarial case.
- The authors state that the gain or loss from Thompson sampling's randomisation remains unclear, with the conditions for near-optimality still open.

## See Also
- [[Bayesian A/B Testing with Expected Loss]] — alternative-to (fixed allocation)
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for (the arm posterior)
- [[Gaussian Processes and Bayesian Optimisation]] — related (explore versus exploit with a surrogate)
- [[NeuralLinear Thompson Sampling]] — instance-of (posterior sampling with a neural network)
- [[Gittins Index and Bayesian Optimal Bandits]] — alternative-to (the Bayesian optimal policy)
- [[Best-Arm Identification, Track-and-Stop and Sequential Halving]] — alternative-to (pure exploration)
- [[Non-Stationary Bandits and Tracking Regret]] — related
- [[Follow-the-Regularised-Leader and Mirror Descent]] — related
- [[Exp3 for Adversarial Linear Bandits]] — related
- [[TopRank and Click Models for Ranking Bandits]] — related
- [[Combinatorial Bandits and Follow-the-Perturbed-Leader]] — related
- [[Partial Monitoring Games]] — related
- [[UCRL2 Average-Reward Regret]] — related (optimism for MDPs)
- [[REINFORCE with a Baseline]] — related (the gradient bandit is the same update)
- [[Exp4 and Oracle-Based Contextual Bandits]] — related (contextual regret against policy classes)
- [[Exp3 Adversarial Bandit Algorithms]] — related
- [[Explore-Then-Commit Bandit Policy]] — related
- [[Bandit Regret Lower Bounds]] — related (the logarithmic regret floor)
- [[Upper Confidence Bound Bandit Algorithms]] — alternative-to (optimism instead of sampling)
- [[LinUCB and Linear Bandit Confidence Ellipsoids]] — alternative-to (linear case)
