---
title: N-Step Bootstrapping
tags: [llm, reinforcement-learning, concept]
summary: "An n-step return sums n real rewards and then bootstraps from the value estimate n steps later, spanning one-step TD (n = 1) to Monte Carlo (n = episode length); the chapter extends it to Sarsa, off-policy importance sampling with control variates, tree backup and Q(sigma)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch07-n-step-bootstrapping.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch05-monte-carlo-methods.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch03-temporal-difference-learning-q-learning-and-n.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch10-policy-control-approximation.md
---

# N-Step Bootstrapping

Sutton and Barto's chapter 7 unifies Monte Carlo and one-step TD into a spectrum. Their hypothesis is that intermediate amounts of bootstrapping typically beat either extreme. The n-step return is

G = R₁ + γR₂ + … + γⁿ⁻¹Rₙ + γⁿ·V(Sₙ), with rewards and the final state counted forward from the state being updated

and equals the full return when the episode ends within n steps. The updated state's value then moves a step α toward G. The method is a delayed update: nothing is learned about a state until n steps later, so n-step methods need more memory and computation per step than one-step methods. The one-step method and its Monte Carlo counterpart are on [[Temporal-Difference Learning, Sarsa and Expected Sarsa]].

## Why it converges

The expected n-step return is, in its worst state, off by no more than γⁿ times the current estimate's worst-state error (the error-reduction property); that bound underlies the convergence of n-step TD. Chapter 7 credits Watkins (1989) with the origin of n-step returns and this property (see [[Q-Learning]]).

## Evidence

On a 19-state random walk (outcome -1 on the left, +1 on the right, values initialised to 0; n swept over 1, 2, 4, ... 512 against the step size; error averaged over the first 10 episodes and 100 repetitions), intermediate n worked best, better than one-step TD or Monte Carlo. The numbers appear only in a figure. In the book's gridworld picture (values start at 0, reward only at the goal, a single episode), a 10-step Sarsa update credits the last ten actions of the path, where one-step Sarsa credits just the final one.

Two further data points. On Winder's cliff gridworld (tabular, one-step baseline settings, values lost from the text), n = 2 and n = 4 Sarsa found optimal trajectories faster than one-step Sarsa, though costing more computation and memory, so n is a hyperparameter to tune. On Mountain Car with tile coding (Sutton and Barto, chapter 10, 100 runs), n = 8 beat n = 1, and n = 4 was best early among 1, 2, 4, 8 and 16; the details are on [[Semi-Gradient TD and Tile Coding]]. Winder also reports that Sarsa(λ) behaves like n-step Sarsa, with high λ leaning to Monte Carlo and low λ to one-step TD, and advises keeping λ below 1 for nontrivial tasks because λ = 1 made all first-state actions converge to about the same value on his grid; he asserts this without numbers.

## Off-policy variants

- **Importance sampling.** Scaling the n-step return by the ratio of target to behaviour action probabilities keeps off-policy learning sound, but the updates have high variance, which pushes step sizes down. If the target policy would never take an action within the n steps, the whole return gets zero weight. For action values only the actions after the first are weighted, since the first is already taken. The ordinary versus weighted forms of this ratio, introduced for Monte Carlo in chapter 5, are described on [[Reinforcement Learning Foundations]].
- **Control variates.** The per-decision return G = ρ(R + γ·G_next) + (1 − ρ)·V(S) does not change the expected update, and when the target would never take the action the target equals the current estimate (no change). The authors advise it over weighting the whole return.
- **Tree backup.** The multi-step extension of Q-learning for stochastic target policies; it needs no importance sampling; the update draws on the estimated action values of the leaf actions, each scaled by how likely the target policy is to choose it. Bootstrapping may span only a few steps when target and behaviour policies differ a lot.
- **n-step Q(sigma).** A per-step degree of sampling sigma in [0, 1]: 1 is full sampling (Sarsa), 0 is pure expectation (tree backup). The authors describe it as new to the text and do not evaluate it.

## Limits

- No numbers are printed in the text; the curves of n against α appear only in a figure. The sole experiment is the 19-state random walk, so Sarsa, importance sampling, tree backup and Q(σ) go untested.
- The authors admit the importance-sampling methods have high variance and are probably not the most efficient option.
- The setting is tabular; function approximation and eligibility traces are deferred to chapter 12.

## See Also
- [[Temporal-Difference Learning, Sarsa and Expected Sarsa]] — prerequisite-for
- [[Q-Learning]] — prerequisite-for
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Eligibility Traces and TD(lambda)]] — extends
