---
title: Operational Reinforcement Learning
tags: [llm, reinforcement-learning, concept]
summary: "Taking an RL prototype into production, per an industrial-RL textbook: scaling architectures, how many seeds an evaluation needs, canary and shadow rollout, logging, and the safe, secure and ethical RL checklists."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch10-operational-reinforcement-learning.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch11-conclusions-and-the-future.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch04-deep-q-networks.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch06-beyond-policy-gradients.md
---

# Operational Reinforcement Learning

Winder's chapter 10 is, by his account, the first attempt to gather operational RL knowledge together; much is extrapolated from software and ML practice and his consulting experience. It covers implementation (frameworks, scaling, evaluation) and deployment. Background is in [[Reinforcement Learning Foundations]]; LLM training stacks are in [[RL Training Frameworks for LLMs]].

## Scaling

Narrow the scope first (simpler problem, simulations, smaller models) and scale afterwards; the time taken per feedback cycle is the main development metric. Actors and learners should sit near each other, ideally on a single machine, because communication and synchronisation are the bottlenecks. The chapter's reported figures, all from cited papers on toy environments:

| Result | Setup |
|---|---|
| A3C on a single 16-core CPU machine matched Gorila using an eighth of the time | Atari, no GPU |
| Gorila ran more than 20x quicker in wall-clock time than DQN alone | Atari |
| PAAC equals A3C at an eighth of the training time (about 12 hours for many games) | Atari, one machine, one GPU |
| DD-PPO scaled almost linearly to 256 workers/GPUs | 3D navigation |
| Ape-X about 3x A3C and 4x Gorila, using 256 CPUs against 16 | Atari; unclear if the gain holds at equal CPUs |
| SEED needs about half IMPALA's training time | similar conditions |
| IMPALA an order of magnitude faster than A3C | 8 GPUs |

Chapter 4 adds a cost point from the author's Coach runs on a GCP P4 GPU VM (two Atari games, one run each, differing default hyperparameters): DQN took about 4.8 hours and $5.80 per million frames, Rainbow about 7.6 hours and $8.50, so Winder advises weighing Rainbow's gain against nearly double the compute.

## Evaluating

- Express policy performance in the problem's own units, perhaps without discounting for the final figure; use median or percentiles when rewards are sparse. Learning speed is how quickly training nears optimal behaviour, counted in whichever of environment steps, wall-clock time, training steps or compute suits the goal.
- Confirm two runs sharing a seed match exactly, having seeded every layer (Python, NumPy, Gym, the DL and RL frameworks, the replay buffer), then vary the seed.
- Run a pilot study to estimate the standard deviation, then compute the trials needed. Colas et al. report needing 15 or more reruns to show SAC ahead of TD3 on Half-Cheetah-v2; Welch's t-test is the most robust for small samples. Statistical tests fail silently. See [[Statistical Test Selection]].
- Probe robustness with adversarial perturbations of states, models and actions. Chapter 11: compare algorithms over many seeds, and distrust the result if there is no clear gap.
- Chapter 11 evaluates with a deterministic policy and exploration off, though it may be worth leaving some randomness on in the live setting if the best policy can drift.
- Chapter 6's servo example: tune hyperparameters in a simulator first; the author damaged a real servo after 5 days of development.

## Deploying

- What matters shifts with the phase: flexibility and speed in development, provenance during hardening, state preservation and monitoring in production. Get the basics right before automating.
- The chapter's architecture pieces are a serving interface, a log, a parameter server, policy servers, replay buffers, actors and critics, learning code shared with serving, and data augmentation. Its build-versus-buy advice: build what is core, buy the remainder, or adapt open source most of the way (80%).
- Record Markov state changes and data shapes in their own log, turn logs into metrics rather than free text, and tag every step with a correlation identifier so a trajectory can be traced. Unit-test incoming data against a schema, since CI/CD only covers static artifacts. Track experiments in an external system; the chapter says TensorBoard scales poorly.
- Rollout options for agents are canary (with stickiness), shadowing, bandit A/B tests and ensembles. The chapter wants the production policy changed as seldom as it can be, using stateless, immutable deployments where each policy update is a new deployment. Compare [[Production Hardening Patterns]].
- Chapter 11 favours little code and off-the-shelf parts. Its debugging advice is to log observations, actions and rewards, chart the value function, begin with a linear or one-layer network, and make runs reproducible under fixed seeds and a single thread before scaling up.

## Safe, secure, ethical

- Safe RL (maximise reward within predefined safety constraints) options: constrained optimisation, reward penalties, imitation or inverse RL, filters that keep actions inside an external safe set, and controllers that abort and reset. The chapter says none of these guarantees safety during learning.
- Secure RL begins with basics (access control, MFA, open ports), followed by monitoring data integrity and rate limiting, weighing each mitigation against how likely an attack is. In poisoning, an attacker alters training data to force an outcome they know in advance. The chapter cites Symantec 2019 for 2% web-server and 1% data-storage exploits as causes of targeted hacks.
- Ethics: during development, work through the chapter's list of questions on bias, personal impact, climate, unintended and nefarious use, legality, human rights, justification and misleading performance claims.

## Limits

- The Coach DQN and Rainbow cost figures come from two Atari games, one run each, with default hyperparameters that differ between the agents. The author says no firm conclusions follow from single episodes and calls the comparison an indicator only.
- The scaling comparisons rest on toy settings (Atari, DeepMind Lab, Google Research Football); the author tells readers to test their own problem. The Ape-X comparison is confounded by 16 times the CPUs.
- The author declines to review frameworks and tools because they date quickly. Costs are 2020 figures; no LLM post-training content.
- No shared way of computing regret exists across problems; formally constrained RL works only on toy examples, and safe RL is described as open.
- The author's view that RL products need far more compute than ordinary software, by orders of magnitude, is opinion without data.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[RL Training Frameworks for LLMs]] — related (LLM-era training stacks)
- [[RL Reward and State Engineering]] — related
- [[Safeguards Architecture — Five Protection Layers]] — related
