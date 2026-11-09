---
title: Elastic Weight Consolidation
tags: [foundations, method]
summary: "Elastic weight consolidation adds a quadratic penalty weighted by the diagonal Fisher information, anchoring parameters that mattered for an old task so a fixed-capacity network learns tasks in sequence."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-kirkpatrick-2017-overcoming-catastrophic-forgetting-neural-networks.md
---

# Elastic Weight Consolidation

Networks trained on one task after another lose what they knew about the earlier ones (catastrophic forgetting). The paper asks whether sequential learning is possible without replaying old data or growing the network. Its hypothesis is that making the weights that mattered for an earlier task harder to move lets a single network of fixed size retain the earlier tasks.

## Mechanism

Elastic weight consolidation (EWC) adds a quadratic penalty to the loss on the new task B, pulling each weight toward its value after task A with a stiffness set by the diagonal Fisher information (a Laplace approximation of the task-A posterior) and a multiplier lambda. Experiments: permuted-MNIST fully connected networks, and a DQN agent with HMM-based task recognition across ten Atari games. The authors claim compute grows linearly with parameter count and number of examples under the diagonal approximation.

## Results

- Trained with plain SGD, the Atari agent learns only a single game and its summed human-normalized score stays under one; with EWC it acquires several games (self-reported). Setup: DQN with task recognition, ten games in sequence.
- Using inferred task labels costs EWC only a small amount compared with using the true labels (self-reported).
- On permuted MNIST EWC keeps old-task accuracy while L2 cannot learn task B and SGD forgets task A; this is qualitative, from a figure. Setup: 2x400 ReLU net, learning rate 1e-3, 20 epochs per dataset.
- Ten separately trained DQNs score higher than the one EWC agent (self-reported). The Atari Fisher multiplier lambda was 400 (self-reported), chosen by hyperparameter search.
- Noise scaled by the inverse Fisher damages performance less than isotropic noise, yet noise along the Fisher nullspace is just as damaging, which the authors read as the Fisher underestimating uncertainty (self-reported). Setup: single-game DQN on Breakout.

## Limits

- Using only the diagonal of the Fisher as a point estimate understates parameter uncertainty, which the authors name as the main weakness.
- The body text reports few numbers; scores appear mostly in figures.
- A known task boundary is required, and each task adds a stored Fisher and anchor, so memory scales with the number of tasks.
- Only small MLPs and a small DQN were tested; no language or vision-language models and no fine-tuning of pretrained models.
- The penalty is applied only to games in which the agent has seen at least 20M frames.

## See Also
- [[Harmful Fine-Tuning of Aligned Models]] — related (fine-tuning can overwrite earlier behaviour)
- [[Vision-Language Model Training Families]] — related (fine-tuning a pretrained model risks forgetting)
