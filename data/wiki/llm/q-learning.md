---
title: Q-Learning
tags: [llm, reinforcement-learning, concept]
summary: "Watkins's 1989 thesis defines Q-learning as incremental value iteration over action values and proves one-step tabular Q-learning converges via a notional action-replay process; its multi-step form and the meta-stable policy problem are left without proof."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-watkins-1989-learning-delayed-rewards.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch03-finite-markov-decision-processes.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch03-temporal-difference-learning-q-learning-and-n.md
---

# Q-Learning

Watkins's 1989 thesis *Learning from Delayed Rewards* treats a family of simple learning methods (estimating values TD-fashion, learning policies directly, and Q-learning) as incremental dynamic programming, with the hypothesis that such methods reach near-optimal behaviour from experience alone and no environment model. Q-learning is the one with a convergence proof.

## The update

One-step Q-learning is a Monte-Carlo form of value iteration over action values. After observing `(x_t, a_t, r_t, x_{t+1})`:

Q(x_t, a_t) ← (1 − α)·Q(x_t, a_t) + α·(r_t + γ·max_a Q(x_t+1, a))

All other table entries stay as they were. The learning factor α is a small positive number that may vary with the state-action pair. The action-value `Q_f(x, a)` is the value of performing `a` in `x` once and then following policy `f`. Sutton and Barto's chapter 3 adds that once the optimal action values are known, the best action is picked directly and no model is needed. The Bellman optimality equation for the optimal action values, which this update samples, is on [[Reinforcement Learning Foundations]]; the contrast with the Sarsa target is on [[Temporal-Difference Learning, Sarsa and Expected Sarsa]].

## Convergence result

The thesis states sufficient conditions for convergence to the optimal action values in a finite MDP: each state-action pair is observed infinitely often, and for each pair the learning factors stay positive, fall steadily as observations accumulate, approach zero, and add up to infinity. The observations need not form a connected sequence and the action choice may be arbitrary. A corrigendum, not the printed pages 227 and 228, gives the final form of the conditions; the printed text requires monotone decrease per pair rather than along the observation sequence.

The proof builds a notional action-replay process (ARP) with layers 0 to n. Acting in layer k can replay an earlier matching observation l ≤ k with probability α_l, which moves the process to layer l − 1 and pays that observation's reward; if no replay happens, the process stops and pays the initial table value Q_0(x, a). The Action-Replay Theorem shows by induction that `Q_n(x,a)` from Q-learning equals the optimal action value of the ARP at stage n. The thesis then argues the ARP approaches the real process: the summed learning factors for a pair grow without bound, so the chance of reaching layer 0 becomes arbitrarily small, and the maximum learning factor shrinks, so the replay process's transition probabilities and mean rewards come close to the real ones.

## Beyond one step

- **Multi-step Q-learning and TD(lambda).** The thesis presents TD(λ) as a geometrically weighted mixture of corrected n-step returns, implemented incrementally with activity traces whose magnitude stays under 1/(1 − γλ). Multi-step Q-learning has no convergence proof; Watkins says a proof eluded him, because the behaviour must be free to vary almost without restriction. Sutton and Barto trace n-step returns and their error-reduction property to this thesis; see [[N-Step Bootstrapping]].
- **Meta-stable policies.** If the agent always acts on its present estimate of the best policy, learning can stall for a very long time (his example MDP has discount 0.9 and the optimal loop A-C-D-E-F). He names a random-policy trick, plus enough experimentation, as the remedy.
- **Demonstrations.** A route-finding task with a CMAC policy and value learner formed a value "mountain" and well-worn paths and adapted after an obstacle was added (gamma 0.9, alpha 0.5, reward 10; the author's own results for his own method, self-reported). In a Skinner-box simulation (gamma 0.95, 50 runs per condition), one-step Q-learning was near-optimal but not optimal, and three-step (M = 3) Q-learning outperformed M = 1 on every schedule but CVI (also self-reported). Watkins attributes slow early learning to chance correlations ("superstitions") and the initial policy, an explanation he did not test.

## Later variants and a practical comparison

Winder dates Q-learning to 1989 and credits it with kick-starting interest in the field. He lists double, delayed (2006, buffers rewards and writes to the table once a state-action pair has been visited enough times) and opposition-based variants. On his cliff gridworld double Q-learning beat the standard form and delayed Q-learning ended very good but with discontinuities, and Sarsa out-earned Q-learning online (see [[Temporal-Difference Learning, Sarsa and Expected Sarsa]]). In a live container-scaling study he cites, Q-learning and a model-based method each raised utilisation about tenfold over threshold policies at similar latency (reported, no table), the model-based one learning faster on the larger action space.

## Limits

- The proof is for one-step tabular Q-learning in finite MDPs, gives no rate, and relies on every pair being visited infinitely often. Multi-step Q-learning, policy-learning methods and CMAC function approximation are unproven.
- Watkins calls using the maximum of estimates as the estimate of a maximum "dubious statistical practice" and yet proves convergence; he says the bias is small with two actions. Maximization bias is treated as a problem on [[Temporal-Difference Learning, Sarsa and Expected Sarsa]].
- The demonstrations are one-off small simulations or 50-run averages; there are no significance tests, the only baselines are analytic optimal policies, and no code is released. The state space for the VI schedule is inadequate, and FI and CFI converge identically but suboptimally for no stated reason.
- Watkins says he has not tackled convergence for function approximation and has implemented no hierarchical control examples.
- The thesis predates neural-network Q functions, replay buffers and target networks, so it does not discuss the stability issues addressed in [[Deep Q-Network, Target Network and Experience Replay]].
- Winder's chapter 3, used above for the later variants, runs single small tabular environments with no hyperparameters, seeds or error bars in the text. His own rule-of-thumb claims are asserted rather than shown, the chapter was written in 2020, and it defers importance sampling to a later chapter.

## See Also
- [[Temporal-Difference Learning, Sarsa and Expected Sarsa]] — alternative-to (on-policy sampled target)
- [[N-Step Bootstrapping]] — extends (multi-step returns and the tree-backup form of Q-learning)
- [[Deep Q-Network, Target Network and Experience Replay]] — extends (Q-learning with a neural network)
- [[Dyna Planning]] — extends (Q-learning plus model-based planning updates)
- [[Reinforcement Learning Foundations]] — prerequisite-for
