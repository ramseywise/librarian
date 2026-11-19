---
title: Dyna Planning
tags: [llm, reinforcement-learning, pattern]
summary: "Dyna runs direct RL, model learning and planning side by side: after each real step it replays n simulated one-step updates from a learned model, which cut the episodes needed on a maze from about 25 to 3; Dyna-Q+ and prioritized sweeping handle changed environments and update focus."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch08-planning-learning-tabular-methods.md
  - data/raw/papers/2026-11-08-murphy-rl-ch04-model-based-rl.md
---

# Dyna Planning

Chapter 8 of Sutton and Barto sets planning (any computation that takes a model and produces or improves a policy) beside learning from real experience and treats both as the same operation: value updates, applied to experience that is either simulated or real. The two differ mainly in which updates are made, in what order, and how long the results are kept. A **distribution model** lists every outcome with its probability; a **sample model** returns a single outcome drawn according to those probabilities. The planning discussed first is *background planning*, where simulated experience gradually improves a stored policy or value function; *decision-time planning* instead starts when a new state arrives, emits one action and usually throws the result away.

## The Dyna loop

Tabular Dyna-Q keeps a model next to its Q-table. On every real step the agent (a) acts epsilon-greedily, (b) applies the Q-learning update to the observed transition (direct RL), (c) stores that transition in the model, assuming a deterministic environment (model learning), and (d) runs n further updates, each choosing a state seen before and an action taken there, asking the model what followed, and applying the same Q-learning update (planning, which is indirect RL). The update itself is on [[Q-Learning]]. The rule for choosing which simulated transitions to replay is called search control.

On the book's Dyna maze (47 states, four deterministic actions, +1 reward only on entering the goal, discount 0.95, step size 0.1, epsilon 0.1, Q starting at 0; 30 repetitions, one seed shared across values of n):

| Planning updates per step (n) | Episodes before behaviour is optimal or nearly so |
|---|---|
| 0 (plain Q-learning) | about 25 |
| 5 | about 5 |
| 50 | 3 |

Every n gives the same first episode, about 1,700 steps, since the model starts empty. Without planning, each episode extends the learned policy by a single step; with n = 50 a sizeable policy has formed by the middle of episode 2, and it is complete and optimal when episode 3 ends.

## When the model goes stale

- A model that is too optimistic gets corrected quickly. A model that turns pessimistic (a shortcut appears) may never be corrected: in the shortcut maze, which changes at step 3,000, Dyna-Q failed to find the new route. In the blocking maze (the short path closes after 1,000 steps) both Dyna-Q and Dyna-Q+ recovered.
- **Dyna-Q+** pays a bonus of κ·√τ on simulated rewards for any transition untried for τ steps, with a small κ whose value is not given. The bonus is applied inside planning updates only and does not alter action selection.

## Spending updates where they matter

- **Prioritized sweeping** puts a state-action pair in a queue when the size of its pending change, |R + γ·max Q(S′,·) − Q(S,A)|, exceeds a threshold θ; after processing a pair it examines that state's predecessors the same way. Through Peng and Williams (1993) the chapter reports a speed-up of 5 to 10 times over unprioritised Dyna-Q on mazes from 47 to 6,016 states (n = 5 for both), and through Moore and Atkeson (1993) a rod-manoeuvring problem (four actions, 14,400 potential states) judged too large for unprioritised methods.
- **Expected versus sample updates.** An expected update takes roughly b times the work of a sample update, b being the number of successors. If the b successors are equally likely, successor values are correct and the initial error is 1, the sample-update RMS error shrinks like √((b−1)/(bt)) after t updates, so for fairly large b most of the improvement arrives within a small fraction of b updates. The authors advise sample updates for large b and many states.
- **Trajectory sampling.** On random tasks (1,000 states, b of 1, 3 or 10, two actions per state, 0.1 chance of termination per transition, epsilon 0.1, 200 tasks), planning along on-policy trajectories was faster early and slower later; at 10,000 states and b = 1, the early advantage was big and lasting.
- **RTDP** on a racetrack with 9,115 reachable states, only 599 of them relevant, converged after 127,600 updates, against 252,784 (28 sweeps) for Gauss-Seidel value iteration; both policies took 14 to 15 steps (25 seeds). It is guaranteed, with probability one, to reach a policy that is optimal on the relevant states if four conditions hold: zero values at the goal, an existing proper policy, strictly negative rewards elsewhere, and initial values no lower than optimal.

## Planning at decision time

A rollout algorithm averages simulated returns under a fixed rollout policy to estimate action values at the present state, then acts greedily on them; this improves on the rollout policy without aiming for the optimum, and the estimates are discarded afterward. MCTS loops through four stages: select a path with a tree policy (for example epsilon-greedy or UCB) down to a leaf, expand, simulate to episode end with the rollout policy, then back the return up the tree's own edges. The move chosen is the one with the highest value or the most visits. The chapter states, without citing an experiment, that MCTS lifted computer Go from a weak amateur level (2005) to 6 dan or higher (2015), and it names AlphaGo as MCTS joined with learned values.

Murphy's survey sorts model-based methods into decision-time planning (model-predictive control, MCTS, sequential Monte Carlo) and background planning (Dyna, Dreamer). Open-loop planning can be suboptimal in a stochastic environment. In his worked example (9 states, 2 actions, horizon 2, only the up action from s1 is stochastic, reaching s2 or s3 with probability 0.5), the open-loop plans score 15 for the two up-first plans and 20 for the two down-first plans, so an open-loop planner picks down for an expected 20, while closed-loop planning can guarantee 30. For learned world models, EfficientZero extends MuZero with three additions (an LSTM value prefix, leaf-value refresh, and a self-prediction loss); its authors report each helps, the self-prediction loss most (no numbers in the chapter).

## Limits

- Everything is tabular. Dyna-Q's model presumes a deterministic environment; the stochastic case is left as an exercise.
- The trajectory-sampling finding is for randomly generated tasks and the authors label it "not conclusive"; the RTDP comparison covers one racetrack and is "not definitive".
- The expected-versus-sample analysis assumes equally likely successors with correct values.
- Some experiments are taken from Sutton 1990, Peng and Williams 1993 and Moore and Atkeson 1993. The changing-maze runs omit n, κ, θ and seed counts, and MCTS and rollout performance get no figures apart from the Go remark.
- The Murphy material comes from a survey that runs no experiments itself, so each empirical statement, the EfficientZero ablation included, is cited from other work.

## See Also
- [[Q-Learning]] — prerequisite-for
- [[Temporal-Difference Learning, Sarsa and Expected Sarsa]] — prerequisite-for
- [[Reinforcement Learning Foundations]] — prerequisite-for
