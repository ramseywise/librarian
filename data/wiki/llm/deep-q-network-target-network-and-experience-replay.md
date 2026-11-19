---
title: Deep Q-Network, Target Network and Experience Replay
tags: [llm, reinforcement-learning, concept]
summary: "A Deep Q-Network fits a neural network to the Bellman target and keeps that training stable with a lagged target copy, a replay table sampled at random and stacked frames; a textbook chapter implements it on Breakout and contrasts it with a policy-gradient agent on CartPole."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch09-deep-reinforcement-learning.md
---

# Deep Q-Network, Target Network and Experience Replay

A textbook chapter asks how deep networks fit into reinforcement learning, through policy gradients and Deep Q-Networks (DQN). The Q-function Q(s, a) is the best discounted future return attainable by taking action a in state s, and the Bellman equation expresses it recursively as the expected reward plus gamma times the best next-state Q. A DQN trains a network toward that recursive target: the chapter's loss sums, across episodes and steps, the squared difference between Q(s_t, a_t) and the reward plus gamma times the best Q at the next state. Its code sets the target to (1 - terminal) times gamma times the next state's maximum Q plus the reward. The general setting is in [[Reinforcement Learning Foundations]].

## What stabilises it

- **Target Q-network**: a duplicate of the prediction network whose parameters trail behind, used to compute the training target.
- **Experience replay**: every experience is stored as an (s, a, r, s') tuple and batches are sampled at random to break correlation between consecutive steps; old experience is evicted.
- **Frame stacking**: the last 4 frames go in as channels so the network sees velocity. DRQN replaces the stack with a recurrent layer.
- **Exploration**: annealed epsilon-greedy, high at first and lower later. The chapter says typical runs lower epsilon from 0.99 to 0.1 across 10,000 scenarios, and that a fixed epsilon performed poorly.
- **Discounting**: gamma between 0.97 and 0.99 so the agent values reward soon.

## The policy-gradient contrast

The chapter's policy-gradient agent minimises minus the sum of return times log probability of the taken action. On CartPole-v0 (two 16-unit hidden layers, Adam at 1e-3, 5,000 episodes) it compared 8 explore-exploit settings; annealing epsilon-greedy from 1.0 to 0.001 did best, while fixed epsilon of 0.05 and of 0.9 did poorly (read from a figure, no numbers). For actor-critic it advises the advantage R_t - V(s_t) in place of the raw return, as A3C approximates it. Its DQN agent on Breakout-v0, trained for 1,000 episodes, shows an upward reward trend (figure only); the chapter says superhuman Atari play typically needs several days of training.

The chapter reports (secondhand) that A3C learns Breakout in under 12 hours against 3 to 4 days for DQN, and UNREAL about ten times faster than A3C on Labyrinth.

## Limits

- The chapter prints no numeric results; performance appears only in two figures.
- Code is TensorFlow 1.x with gym CartPole-v0 and Breakout-v0, not runnable on current stacks, and it has bugs. Among them: the naive-returns loop iterates an empty range, the "solved" checks use the wrong slice of episode rewards, `sample_batch` hands back discounted returns where the terminal flag belongs, the annealing text says epsilon rises while the code lowers it, and the policy loss uses return with no baseline.
- The prose says `build_model` returns three action nodes although CartPole has two actions.
- Only methods from 2013 to 2016 appear (DQN, A3C, UNREAL, DRQN); PPO, TRPO, DDPG, SAC, double and dueling DQN, prioritised replay and RLHF are absent.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Multi-Agent Reinforcement Learning]] — related
