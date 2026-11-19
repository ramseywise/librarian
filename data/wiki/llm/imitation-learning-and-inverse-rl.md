---
title: Imitation Learning and Inverse RL
tags: [llm, reinforcement-learning, concept]
summary: "Using expert demonstrations in RL: behavior cloning and why it is unpopular, DQfD, GAIL and SQIL, inverse RL that learns a reward from demonstrations, and the related curriculum, residual and transfer ideas, as surveyed in an industrial-RL textbook."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch08-improving-how-an-agent-learns.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch09-practical-reinforcement-learning.md
  - data/raw/papers/2026-11-08-murphy-rl-ch07-other-topics-rl.md
---

# Imitation Learning and Inverse RL

Winder's chapter 8 surveys ways to guide an agent with expert knowledge. It is an overview with no experiments of its own, and the author says each theme deserves a book of its own. The base setting is in [[Reinforcement Learning Foundations]].

## Methods

- **Behavior cloning** is supervised learning trained to pick whichever action the expert took in the states it encountered. Winder calls it unpopular because it overfits the demonstrations and fails in states nobody demonstrated.
- **DQfD** (Hester et al., 2017) and **GAIL** (Ho and Ermon, 2016) combine demonstrations with RL, the latter adversarially.
- **SQIL** (Reddy et al., 2019) is described as simplifying DQfD and GAIL: it controls the trajectories in the replay buffer, reconstructs rewards for them, and uses a loss that stays near expert trajectories. Winder's own suggestion, not a SQIL result, is to control how much expert advice is used by weighting the regularisation.
- **Inverse RL (IRL)** predicts what the reward would look like given demonstrations, replacing manual reward design. It repeatedly retrains RL, so the chapter says it stays limited to simple state spaces. Failed demonstrations can also be used, by lowering their reward. Reducing high-dimensional state by autoencoding or hashing before IRL is advised.
- **Residual RL** (Johannink et al., 2018) combines policies for robot control; it is listed with the expert-guidance methods.
- **Curriculum learning** is in the same family of expert guidance; the chapter lists it without a worked treatment in the extraction.

## Other guidance

Chapter 9 adds that imitation is one option to try before intrinsic-motivation exploration, alongside better algorithms, intermediary rewards and denser rewards.

On transfer, the chapter names three types: same task and domain, same domain with a different task, and across domains. It advises reusing earlier policies and experience instead of training from scratch.

## Behavior cloning, DAgger and offline RL in Murphy's overview

Murphy's chapter 7 points out that plain behavior cloning treats expert data as independent samples, so a small error on the expert's own states can grow large once the learner drifts to states the expert never showed. DAgger fixes this by collecting training data from the learner's own rollouts.

Offline RL learns from a fixed logged dataset with no interaction, and the main obstacle is generalising to states outside that data. Murphy lists three remedies: stay close to the logging policy, penalise uncertain estimates, or use conservative Q-learning (CQL), which pushes Q down for the learner's actions and up for logged actions. Pretraining with CQL and then fine-tuning online can spend many steps undoing the pessimism; Calibrated Q-learning targets that. The model-based methods MOPO (reward reduced by model uncertainty) and MOREL (uncertain transitions lead to an absorbing state) bound true performance from below if the uncertainty estimate bounds the model error. Return-conditioned sequence models such as the decision transformer can break badly in stochastic environments, since a high return in one trajectory may be luck.

## Limits

- Murphy's chapter is a brief survey reporting cited work; he adds that offline RL is inherently weaker than online RL, since the agent cannot explore.
- Overview chapter, written 2020; the methods are pre-LLM and the chapter says nothing about RLHF or LLM agents.
- Descriptions are qualitative and come from cited papers; there are no benchmark numbers.
- Winder's views are flagged as opinion ("I suspect", "I can imagine").

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[RL Reward and State Engineering]] — related (IRL as an alternative to hand-designed rewards)
- [[Hierarchical Reinforcement Learning]] — related
- [[Decision Transformer Return-Conditioned Sequence Modeling]] — related
