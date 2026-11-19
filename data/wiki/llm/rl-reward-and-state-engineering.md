---
title: RL Reward and State Engineering
tags: [llm, reinforcement-learning, concept]
summary: "Practitioner guidance from an industrial-RL textbook on spotting an RL problem, then engineering the environment, state, actions, exploration and reward, including its reward-clipping and discretisation cautions."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch09-practical-reinforcement-learning.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch11-conclusions-and-the-future.md
  - data/raw/papers/2026-11-08-winder-reinforcement-learning-ch01-why-reinforcement-learning.md
  - data/raw/papers/2026-11-08-winder-reinforcement-learning-ch02-markov-decision-processes-dynamic-programming.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch03-temporal-difference-learning-q-learning-and-n.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch04-deep-q-networks.md
---

# RL Reward and State Engineering

Winder's chapters 9 and 11 are a practitioner's account of what an RL project involves. Most of it is advice, not measurement. The formal setting is in [[Reinforcement Learning Foundations]]; for LLM-specific reward failures see [[Reward Hacking and Overoptimization]].

## Is it an RL problem

Winder and chapter 1 advise RL when decisions are sequential and strategic, where machine learning is single-step and myopic, and the simplest solution that works otherwise. Chapter 9 lists indicators: sequential, strategic, entity, environment, state, action and quantifiable success; state success in the stakeholder's own units, money for example. Chapter 1 favours supervised learning whenever ground truth is obtainable. Early RL results should be expected to trail an existing ML solution. Chapter 11 puts most RL failures down to a poor fit between problem and RL rather than the algorithm (author's experience, no data).

## Environment and state

- Build the environment first, behind a Gym-style interface, to understand the data and escape the "improvement shotgun" (trying assorted ideas in hope that one works).
- Use an existing simulation unless owning one is a competitive differentiator. Do not trust it too far: a policy that works perfectly there can fail in real life.
- Work on making the state a good representation and leave the solving to the policy, rather than hand-building features that solve the task. State engineering is also called state representation learning. In a cited robotic-grasping study (Kalashnikov et al., QT-Opt) adding a gripper-height measurement to an image state raised pick-up of unseen objects by 12% (reported; baseline not described).
- Limit state and action counts to reduce the exploration space. For continuous states, linear approximators over polynomial, Fourier or radial bases retain convergence guarantees, and for Q-learning you can discretise by binning, tile coding or hashing. The chapter says no convergence proofs exist (as of 2020) for nonlinear approximators.
- Discretisation has a cost: in a ride-share example the grid cells were about 2 miles across, so even an optimised vehicle might be 2 miles from the customer.
- Chapter 3 says most practical effort goes on how the state is represented and how reward is defined, with the algorithm secondary. In chapter 4's CartPole run, tabular Q-learning matched DQN only after feature engineering left about 150 discrete states.

## Actions and exploration

When taking a softmax over actions, feed it advantages instead of raw values. For continuous actions, predict a distribution's mean (and std), with a large std at the start. With a huge action space, use policy gradients or embeddings, or rank the top-k items instead of choosing combinations. Intrinsic motivation comes after other options such as better algorithms, intermediary rewards, denser rewards and imitation ([[Imitation Learning and Inverse RL]]).

## Reward

- Keep the reward as simple as possible and quantitative; complex rewards let algorithms exploit flaws. Chapter 1's examples: a maze robot that spun for three days, a basket agent that added every product, a moose stuck in a tree after fermented apples.
- Chapter 9's guidelines say a reward should arrive quickly, track the true reward, be denoised, carry nonfunctional requirements, account for time, avoid plateaus, and be smooth and simple.
- Normalise rewards; clip with care. Winder claims that clipping rewards to +/-1, which DQN recommends, makes Pac-Man dots and fruit equivalent, while normalising makes the agent hunt ghosts and fruit (no numbers or citation given).
- Chapter 11 swaps sparse rewards for smooth ones like distance to goal, and removes outliers and discontinuities.
- Use reward shaping to give more frequent feedback under delayed reward (chapter 1).
- Chapter 11's framing advice: watch a random policy and play the task yourself, then build baselines in sequence: a random agent, the cross-entropy method, then a simple Q-learning or policy-gradient agent.

## Data and training hygiene (chapter 11)

Standardise observations to zero mean and unit variance and decorrelate them; track the spread of rewards, the inputs, value predictions, gradients, how random the actions are, and KL divergence; increase the time between actions (frame skipping); use learning-rate schedules; develop against a range of environments and seeds. Engstrom et al. is cited for code-level optimisations explaining most of the PPO-versus-TRPO gap, and a zeroed-array bug in OpenAI's random-network-distillation work, once fixed, improved performance dramatically (no numbers).

## Limits

- Practitioner's opinion: almost no experiments or numbers of the author's own; the claims are opinion or taken from cited work.
- The book dates from 2020: offline RL is called an open research problem, and nothing here touches LLMs or RLHF.
- By the author's own admission the guidance is domain-specific and reflects what he thinks reasonable.
- Chapter 2's discount-rate advice (0.9 to 0.99 in nontrivial problems) is stated without data.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Reward Hacking and Overoptimization]] — related (the proxy-reward failure in LLM training)
- [[Imitation Learning and Inverse RL]] — related (learned rewards as an alternative)
- [[Operational Reinforcement Learning]] — related (what follows a working prototype)
