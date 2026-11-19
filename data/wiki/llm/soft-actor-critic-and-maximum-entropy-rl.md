---
title: Soft Actor-Critic and Maximum-Entropy RL
tags: [llm, reinforcement-learning, concept]
summary: "Maximum-entropy RL adds an entropy term, weighted by a temperature, to the reward; a practitioner textbook covers soft actor-critic, its automatic-temperature and discrete variants, grid-world demos of the temperature, and a Donkey Car build."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch07-learning-all-possible-policies-with-entropy-m.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch08-improving-how-an-agent-learns.md
---

# Soft Actor-Critic and Maximum-Entropy RL

A 2020 industrial-RL textbook (Winder, chapter 7) asks how maximum-entropy RL produces robust stochastic policies and how it compares with PPO and with Q-learning. The general setting is in [[Reinforcement Learning Foundations]].

## The pieces

- **Shannon entropy** measures the information in a stochastic variable, counted as the bits needed to encode all its states. The maximum-entropy objective rewards a policy for keeping its entropy up as well as for earning reward.
- **Temperature** is the hyperparameter that sets the entropy term's weight against the reward and so controls how stochastic the optimal policy is.
- **Soft actor-critic (SAC)** approximates the maximum-entropy objective with an off-policy policy gradient. "Soft" flags the stochastic parts; a Bellman equation lacking any entropy term could be called "hard".
- **Automatic temperature** frames the temperature as a floor on how little entropy the policy may have. The chapter gives the target entropy as minus the action count (its Equation 7-7).
- **Discrete SAC** plus automatic temperature (Christodoulou, 2019) is claimed to rival value-based methods while needing no hyperparameter tuning.

## What the temperature does

In the chapter's grid world (goal top right, start in the middle, 8 moves including diagonals, sparse reward of 1, 100-step limit), soft Q-learning used temperature 0.05. Raising it to 1 over 500 episodes let the entropy term overpower the goal reward, and the agent headed for the high-entropy middle states. Annealing it from 0.5 down to 0.005 gave early exploration, then Q-learning-like behaviour that reached the goal. These demos are qualitative figures.

## Extensions the chapter surveys

Other entropies (Tsallis and Renyi, with a policy ensemble), optimistic exploration with an upper bound for the behaviour policy, replay changes that emphasise recent experience, soft policy gradient, soft Q-learning and path consistency learning (an n-step off-policy method over soft state and action values that needs no off-policy correction). Winder notes that policy gradients with an entropy regulariser amount to soft Q-learning, and he expects value and policy methods to merge. Regularisers such as SAC's change the Bellman equality; the chapter cites Li et al. for convergence holding under any regulariser that follows some rules.

## SAC against PPO

Table 7-1 puts SAC and PPO continuous-control numbers side by side, from published papers rather than the author's runs. Numbers are taken after 1 million steps with a single column at 1.5 million, and another column taken from published images. The chapter concludes SAC mostly beats PPO on the MuJoCo environments in that sample. Its variance across SAC results is large, which Winder attributes to poorer hyperparameter tuning (no controlled test), and he gives that as the reason automatic temperature matters.

## Donkey Car build

SAC (stable-baselines) drove the Donkey Car Unity simulator from a VAE latent state rather than the 160x120 8-bit RGB pixels; the chapter claims a smaller state space turns days of RL training into minutes. To prevent skids, throttle was limited to 0.15 (it began at 5.0) and steering to magnitude 0.5 (it began at 1.0). The final policy used between five and fifty thousand environment steps, ten minutes to half an hour on a 2014 MacBook Pro. An Optuna search found that for short runs, an initial entropy coefficient of 0.1 that is then learned beat the stable-baselines default of 1.0, and that learning rates could go up tenfold; no scores were given.

A traffic work-zone-merge case study (Ren et al.) used SAC in VISSIM simulation and reports delays cut by an order of magnitude against early or late merge-sign strategies.

## Practices the chapter gives

- Search over the temperature per problem in plain SAC, or switch to the automatic variant.
- Rescale rewards, because the balance between reward scale and temperature matters to SAC.
- Anneal the temperature to explore early and become near-deterministic later.
- Oversample recent experience and use a large replay buffer to limit catastrophic forgetting.
- Constrain the action space if training gets stuck.
- Go with the simplest workable solution, and do not default to an esoteric algorithm over SAC, which has more industrial mileage.
- Re-run candidate algorithms and implementations on your own task.

## Limits

- Table 7-1 mixes numbers from different papers and implementations; the author notes that groups measure performance in different ways, seldom release raw learning curves, and that implementation details shift results. It reports averages only, not stability across runs.
- The traffic study is simulation only; the author doubts its policy network needs to be so complex.
- The grid-world and Donkey Car demos are figures and videos, lacking scores, seeds or error bars.
- The book dates from 2020, before LLM RL; SAC as presented is for continuous (Gaussian) actions.
- The author warns that extensions do not guarantee better results on your problem.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Multi-Agent Reinforcement Learning]] — related (MADDPG in the same actor-critic family)
- [[Operational Reinforcement Learning]] — related (constrained SAC appears under safe RL)
