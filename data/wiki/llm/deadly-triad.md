---
title: The Deadly Triad
tags: [llm, reinforcement-learning, concept]
summary: "Instability and divergence arise whenever function approximation, bootstrapping and off-policy training are combined; Sutton and Barto show it with counterexamples (the w/2w example, Baird's counterexample) and present Gradient-TD and Emphatic-TD as remedies."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch11-off-policy-methods-approximation.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch12-eligibility-traces.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch10-policy-control-approximation.md
  - data/raw/papers/2026-11-08-murphy-rl-ch02-value-based-rl.md
---

# The Deadly Triad

Chapter 11 of Sutton and Barto asks why learning off policy with function approximation holds up worse than learning on policy. It separates two sources of trouble: the update target, which importance sampling corrects, and the distribution of updated states, which is no longer the on-policy one. The "deadly triad" names what happens when three ingredients meet: function approximation, bootstrapping and off-policy training. Instability and divergence threaten whenever all three are present, and dropping any one of them can avoid it. The chapter stresses that control, generalised policy iteration and uncertainty about the environment are not the culprits, since the problem shows up in plain prediction and in dynamic programming with a known model. To avoid off-policy training in model-free RL it suggests using Sarsa rather than Q-learning, while observing that off-policy learning is what lets many value functions be learned in parallel from a single stream of experience. It advises keeping bootstrapping anyway, since giving it up costs data efficiency and computation.

## Counterexamples

- **w and 2w**: two states with values w and 2w, zero reward, one action (so the importance ratio is 1), and a single transition updated repeatedly with nothing else. Each off-policy semi-gradient TD(0) update scales w by 1 + alpha(2 gamma - 1), so w diverges for every positive alpha once gamma is above 0.5.
- **Baird's counterexample**: a task with 7 states and 2 actions, discount 0.99, zero rewards throughout, and 8 weights on linearly independent features. The behaviour policy picks the dashed action with probability 6/7 and the solid action with 1/7, while the target policy always picks solid. The semi-gradient off-policy TD(0) update and the semi-gradient DP update both blow up whatever positive step size is used. The figure's run took step size 0.01 and began with seven weights at 1 and one weight (the seventh) at 10. Murphy's value-based RL chapter restates the same setup (7 states, 2 actions, gamma 0.99, 8 weights, behaviour probabilities 6/7 and 1/7) and notes that TD(0) diverges although the true value is 0. Swapping in an expected, DP-style update does not help; making the update distribution on-policy is enough to guarantee convergence.
- Comparable examples exist that make Q-learning diverge. Q-learning with an epsilon-greedy behaviour policy near the target has never been seen to diverge, yet no theoretical analysis covers it.
- Projecting by least squares at each DP step does not bring stability back (Example 11.1, attributed to Tsitsiklis and Van Roy).
- Stable approximators are the averagers, which never extrapolate from observed targets (nearest neighbour, locally weighted regression). Tile coding and neural networks are not averagers.

## Objectives to use instead

- Naive residual-gradient methods minimise the TD error. On the A-split example (tabular, on-policy, 3-state Markov reward process, gamma = 1) they settle at B = 3/4 and C = 1/4 rather than the true values 1 and 0. Targeting the Bellman error unbiasedly requires two independent samples of the next state (or a deterministic environment), and these methods run much more slowly than semi-gradient ones.
- Example 11.4 builds two Markov reward processes with the same data distribution but different Bellman errors, showing the Bellman error and its minimiser cannot be learned from features, actions and rewards. The projected Bellman error and the TD error can.
- **Gradient-TD** methods (GTD2, TDC) do true stochastic gradient descent on the projected Bellman error. They cost O(d) per step but need a second weight vector and a second step size, roughly doubling computation. On Baird's counterexample TDC (alpha 0.005, beta 0.05, 1000 steps) drives the projected Bellman error to zero while the value error stays near 2.
- **Emphatic-TD** weights each state by an emphasis term so the update distribution behaves like an on-policy one. Followed in expectation (alpha 0.03, interest 1), a one-step Emphatic-TD update converges on Baird's counterexample, but sampled runs vary too much for consistent experiments. To tame off-policy variance generally, the authors list momentum, Polyak-Ruppert averaging, step sizes set per parameter, and tree-backup-style methods.
- Chapter 12 adds that off-policy eligibility traces with lambda below 1 still bootstrap, so the triad covers them too ([[Eligibility Traces and TD(lambda)]]).
- Chapter 10 observes that function approximation loses the policy improvement theorem, leaving action-value methods without a local improvement guarantee. Linear semi-gradient Sarsa with epsilon-greedy action choice does not converge in the usual way, but ends up inside a bounded region near the best solution (on-policy, credited to Gordon).

## Limits

- DQN, experience replay, target networks, Atari and deep networks never appear in the chapter. It offers theory and counterexamples for linear and semi-gradient methods, so anything said about deep RL from it would be inference.
- The authors describe the field as new and unsettled, say it is unclear which methods are best or even adequate, and their 2018 preference for Gradient-TD and Emphatic-TD has probably aged.
- Murphy's chapter is a survey with no experiments of its own, and its state-of-the-art statements are as of 2024.
- The only experiments are on Baird's counterexample, with no benchmark numbers. Emphatic-TD varies a great deal in practice.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Deep Q-Network, Target Network and Experience Replay]] — related (a deep method that bootstraps off policy with function approximation)
- [[Eligibility Traces and TD(lambda)]] — related
- [[Semi-Gradient TD and Tile Coding]] — prerequisite-for
- [[Q-Learning]] — related (divergence examples and the epsilon-greedy case)
