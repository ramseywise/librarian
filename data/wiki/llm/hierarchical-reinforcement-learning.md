---
title: Hierarchical Reinforcement Learning
tags: [llm, reinforcement-learning, concept]
summary: "Hierarchical RL splits a policy into low-level skills and a high-level planner; a textbook survey covers HIRO, DIAYN and HAAR, and when hierarchy is worth it, alongside the MDP variants (POMDP, contextual MDP) that precede it."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch08-improving-how-an-agent-learns.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch11-conclusions-and-the-future.md
  - data/raw/papers/2026-11-08-murphy-rl-ch07-other-topics-rl.md
---

# Hierarchical Reinforcement Learning

In chapter 8 of an industrial-RL textbook, Winder defines hierarchical RL (HRL) as splitting a problem into subtasks: low-level policies act on the environment while high-level policies plan. The chapter is a survey with no experiments of its own. Foundations are in [[Reinforcement Learning Foundations]].

## Methods

- **HIRO**: the policy is split in two. The low-level policy receives an intrinsic reward, a distance to a target state set by the high-level policy; the high-level policy gets the environment reward and acts less often. Nachum et al. rewrite the high-level goals stored in the replay buffer so off-policy data is not stale. The example is a simulated legged robot.
- **DIAYN**: encourages unsupervised discovery of low-level skills that are diverse and distinguishable, for example HalfCheetah running, crawling and sitting.
- **HAAR**: uses the high-level advantage estimate, rather than Euclidean distance to a state, as the reward for retraining pretrained low-level skills.

## When it helps

Winder claims HRL pays off when the agent itself is complex, and may not when the complexity sits in the environment. Practical guidance: design the hierarchy manually when concerns separate cleanly before reaching for learned hierarchies, and consider an initial skill library or pretraining, which could improve learning speed. Chapter 11 adds that solving disparate skills independently should be considered before HRL.

## MDP variants that come first

Before adding hierarchy, the chapter says to check the MDP assumptions.

- A **POMDP** adds observations and an observation function because the agent cannot see the state. Adding an estimator that predicts a belief state restores an MDP; the usual simplest choice is an RNN at the tail of the state-representation function. Atari benchmarks stack four frames to keep some history. In a cited simulated four-way intersection (Qiao et al., 2018), an LSTM policy with an engineered reward learns when to set off and avoids collisions.
- A **contextual MDP** models context that is fixed within an episode.
- Chapter 11 advises adding working memory such as a recurrent network only when states have to be visited in a particular order, after first checking whether some shortcut action makes it unnecessary.

## Options and feudal RL in Murphy's overview

Murphy's chapter 7 (a brief survey) defines an option as an initiation set, an intra-option policy and a termination probability. In feudal RL, managers set goals for the workers beneath them and only the top manager sees the environment reward. He reports feudal designs are easier to train but can end up worse than a flat policy, whereas options can reach the flat policy's optimum. Option-critic and double actor-critic can degenerate to changing option at nearly every step; adding a cost for each deliberation discourages switching and speeds learning, at the risk of a worse final policy. He also recommends hindsight relabeling (HIRO, HAC) against non-stationarity.

## Limits

- Murphy's chapter is brief and mostly reports cited work without data. It notes subgoal discovery needs discrete subgoal spaces, skill chaining needs explicit goal states, and option-critic works poorly under sparse reward.
- No experiments, hyperparameters or numbers of the author's own; results are qualitative accounts of cited papers.
- Written in 2020, so the HRL work cited is pre-LLM; the chapter does not discuss LLM agents.
- Some statements are the author's opinion, flagged as such.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Multi-Agent Reinforcement Learning]] — related (same chapter's multi-agent survey)
- [[Imitation Learning and Inverse RL]] — related
