---
title: Reinforcement Learning Foundations
tags: [foundations, llm, concept]
summary: "The MDP tuple (S, A, P, R, γ), the Markov property that makes RL tractable, the four algorithm families, and the exploration/exploitation tension — with how each maps onto LLM training and agentic tool use."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--rl.md
---

# Reinforcement Learning Foundations

Unlike supervised learning (a labeled answer key) or unsupervised learning (patterns in
unlabeled data), RL learns by **trial and error** — an agent interacting with an unknown
environment to maximize cumulative reward.

## The MDP

The mathematical foundation: a tuple `(S, A, P, R, γ)`.

| Symbol | Meaning |
|---|---|
| **S** | State space — situations the agent can observe |
| **A** | Action space — decisions available |
| **P(s'\|s, a)** | Transition function — probability of reaching `s'` from `s` via `a` |
| **R(s, a)** | Reward function — scalar feedback after acting |
| **γ** | Discount factor (0 ≤ γ ≤ 1) — weight on future vs immediate reward |

**The Markov property:** the next state depends only on the current state and action, not
the full history. This is the assumption that makes RL tractable — without it, the policy
would have to be a function of an unbounded trajectory rather than a fixed-size state.

It is also the assumption most often violated in practice by LLM agents, where "state"
is a context window that manifestly *is* the history. The practical consequence is that
what an agent can learn to do is bounded by what its state representation actually
captures — a point that recurs in [[Context Engineering]] terms as the question of what
belongs in the window.

## Core components

**Agent** (the learner), **environment** (the world), **state** (current observation),
**action** (the decision), **reward** (scalar feedback), and **policy π** — the strategy
mapping states to actions, and the thing actually being optimized. Policies are either
deterministic (`π(s) → a`) or stochastic (`π(a|s) → [0,1]`).

## Algorithm families

| Family | Learns | Examples |
|---|---|---|
| **Value-based** | Expected long-term return of states or state-action pairs, then acts greedily | Q-Learning, DQN |
| **Policy-based** | The policy directly, via `∇E[R]`, with no explicit value function | Policy gradient |
| **Actor-critic** | Both — an actor picks actions, a critic estimates value as a lower-variance update signal | PPO (dominant today) |

Cross-cutting: **model-free** agents learn purely from experience; **model-based** agents
learn `P(s'|s,a)` and plan against it — more sample-efficient, but only as good as the
learned model.

The actor-critic split is worth holding onto, because it explains a structural fact about
[[Preference Optimization Algorithms]]: the critic is the component GRPO removes (using a
sampled group's mean as the baseline instead), and the critic is one of the four resident
models that make PPO expensive.

## Exploration versus exploitation

Should the agent **exploit** the best known action, or **explore** actions that might pay
off more later? Three standard answers:

- **ε-greedy** — random action with probability ε, otherwise exploit
- **UCB** — prefer actions with high uncertainty, to reduce that uncertainty faster
- **Entropy regularization** (SAC, GRPO) — an entropy bonus in the reward, rewarding
  diverse action distributions

**In LLM contexts, temperature sampling at inference time is the primary exploration
mechanism during data collection.** This is the operational form the tension takes: too
low a temperature and the rollouts are near-duplicates carrying little training signal;
too high and they leave the region where the reward model is valid.

## Where RL enters LLM training

Two distinct stages, often conflated:

1. **RLHF alignment (post-pretraining)** — the LLM *is* the policy, each token is an
   action, the reward model scores completed responses. See [[RLHF Pipeline]].
2. **Agentic RL (tool use, retrieval, reasoning)** — the LLM takes multi-step actions in
   an environment (browser, code executor, knowledge base), with task completion as the
   reward. See [[RL for Retrieval Policies]].

The difference that matters: in (1) the environment is trivial (a single generation step)
and the difficulty is in the reward model; in (2) the reward is often obvious (did the
task complete?) and the difficulty is credit assignment across a long trajectory.

## See Also
- [[RLHF Pipeline]] — instance-of (the LLM-as-policy formulation)
- [[Preference Optimization Algorithms]] — extends (actor-critic and what each method removes)
- [[Multi-Agent Reinforcement Learning]] — extends (the same MDP with multiple interacting policies)
- [[RL for Retrieval Policies]] — instance-of (RAG as a sequential decision process)
- [[Reward Hacking and Overoptimization]] — complements (what goes wrong when the reward is a learned proxy)
