---
title: Decision Transformer Return-Conditioned Sequence Modeling
tags: [llm, reinforcement-learning, concept]
summary: "Decision Transformer trains a causally masked GPT on offline trajectories of return-to-go, state and action tokens and acts by being given a target return; it matched or beat model-free offline RL on D4RL and Atari Breakout but not Qbert (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-chen-2021-decision-transformer.md
---

# Decision Transformer Return-Conditioned Sequence Modeling

Chen, Lu, Rajeswaran et al. (preprint, arXiv v2, June 2021) ask whether generative trajectory modelling with a causally masked transformer, conditioned on a desired return, can replace TD-learning based offline RL. Their hypothesis is that modelling (return-to-go, state, action) sequences can optimise a policy while avoiding dynamic programming, bootstrapping and value pessimism, and that it assists credit assignment over long spans.

## Mechanism

- A GPT model reads offline trajectories as alternating (return-to-go, state, action) tokens and predicts the actions, using cross-entropy when actions are discrete and mean squared error when they are continuous.
- Each return-to-go totals the rewards still to come from a given timestep, and these are given to the model instead of the rewards themselves.
- At test time a target return is supplied and decremented by each observed reward (the algorithm's line is `R = R + [R[-1] - r]`). The last K timesteps, 3K tokens, form the context.
- Percentile behaviour cloning (%BC) is behaviour cloning on the top X% of timesteps ordered by episode return; it serves as an analysis baseline, since finding the best percentile needs environment rollouts.

## Reported results (self-reported)

- Against CQL: DT scored higher on the D4RL average without Reacher (9 settings, being 3 environments each at medium, medium-replay and medium-expert, over 3 seeds) and with it (12 settings). On Atari Breakout DT beat CQL (using 1% of the DQN-replay data, K = 30, 3 seeds), but on Qbert it was far below.
- Delayed reward (Hopper medium-replay, reward only at the final step): CQL collapses and DT barely moves.
- Key-to-Door with 1K and 10K random trajectories (full-episode context): DT compared with CQL on success, with the extraction giving no values.
- Context length: on Pong, K = 1 collapses against K = 50. %BC is weak on Atari with 1% data (Pong 10%BC against DT's 106.1).
- Graph shortest path (1,000 random walks, 20 nodes): a fraction of the generated paths are stitched and absent from the training data.
- On Seaquest, DT can be prompted above the dataset's maximum return (a claim from a figure).

## Limits

- Offline only; benefits for online RL are conjecture.
- The Atari runs draw on a 1% slice of replay data and cover four games, and the D4RL runs use medium-level datasets only.
- Return targets are hand-chosen per environment (expert level, 50% for HalfCheetah); returns are deterministic, and stochastic settings are future work.
- Compute, hardware and the number of evaluation episodes are not stated.
- The authors admit that the mistakes and downsides of applying transformers to MDPs have been little studied.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Imitation Learning and Inverse RL]] — related (behaviour cloning on filtered data is its baseline)
- [[Foundation Models as Decision Makers (MDP View)]] — related
- [[TALM Tool-Augmented Language Models]] — related (its self-play bootstrapping cites this paper)
