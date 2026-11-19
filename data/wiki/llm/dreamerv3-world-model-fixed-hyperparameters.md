---
title: DreamerV3 World Model with Fixed Hyperparameters
tags: [llm, reinforcement-learning, concept]
summary: "DreamerV3 learns a world model from replayed experience and trains an actor and critic only on imagined latent trajectories, using symlog, twohot, free-bits KL and return-normalisation tricks so one hyperparameter table runs across 8 benchmarks, including Minecraft diamonds from scratch (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-hafner-2023-mastering-diverse-domains-through-world.md
  - data/raw/papers/2026-11-08-murphy-rl-ch04-model-based-rl.md
---

# DreamerV3 World Model with Fixed Hyperparameters

Hafner et al. test whether a single RL algorithm, run with one unchanged hyperparameter setting, can equal or exceed tuned specialists over many domains, among them collecting Minecraft diamonds from scratch. The method fits an RSSM world model to replayed experience, then trains an actor and a critic purely on imagined latent trajectories of that model. When acting in the environment, it samples from the actor and does no lookahead planning. Baselines are a PPO tuned once and then fixed, published expert results, and, for Minecraft, IMPALA and Rainbow tuned by the authors.

## Robustness techniques

The authors hypothesise that these techniques let one configuration work without retuning:

- **symlog**: sign(x) times ln(|x| + 1), inverted by symexp; a log-like transform that is symmetric about zero, applied to targets and inputs whose scale is unknown.
- **symexp twohot loss**: the network emits logits over bins spaced exponentially (symexp applied to -20 through +20) and learns from twohot-encoded targets with a cross-entropy loss.
- **KL balancing with free bits**: the dynamics and representation losses are clipped below 1 nat.
- **Percentile return normalisation** and a **1% unimix** are the other two named techniques.

Ablations over 14 tasks found every technique contributes; the KL objective matters most, then return normalisation and symexp twohot (the text gives no numbers). In a learning-signal ablation, the unsupervised reconstruction loss supplied most of what Dreamer learned from, with reward and value gradients playing a smaller part.

## Results (self-reported)

- **Minecraft Diamond** (sparse reward, default hyperparameters, no human data, 10 seeds, 100M environment steps; baselines PPO, IMPALA and Rainbow, the last two tuned by the authors): every Dreamer run discovered a diamond within the budget and no baseline did.
- **Atari, 57 games** (sticky actions, 200M steps, 5 seeds, a 200M-parameter model): the Dreamer gamer median is above MuZero and PPO.
- **ProcGen** (16 games on hard difficulty with unlimited levels, 50M steps, a single seed each for Dreamer and PPO): normalised mean matches PPG and beats PPO.
- **DMLab** (30 tasks): Dreamer at 100M steps exceeds IMPALA at 1B steps (66.3); IMPALA reached 85.1 at 10B and R2D2+ 85.4 at 10B, while IMPALA at 100M scored 31.0 and PPO at 100M 35.9.
- **Atari100k** (26 games, 400K environment steps, replay ratio 128, 0.1 GPU days): gamer mean above IRIS, TWM, SPR and SimPLe but not EfficientZero, whose protocol differs.
- **Proprio Control** (18 DMC tasks, 500K steps, 12M model) and **Visual Control** (20 DMC tasks from pixels, 1M steps, 12M model): task means above D4PG, DMPO and DDPG, and above DrQ-v2 and CURL, respectively.
- **BSuite** (23 environments, 468 configurations, 10 seeds): task mean above Boot DQN, but near zero on the exploration category where Boot DQN scores 0.68.
- Scores improve as the model grows from 12M to 400M parameters and as replay ratio rises, and bigger models need fewer interactions (Crafter and one DMLab task, six sizes, replay ratios 1 to 64).
- Compute on Minecraft: 1 GPU for 9 days, against 720 GPUs for 9 days that the authors state for VPT, which uses behavioural cloning plus RL fine-tuning, a different setup.

## Later accounts (survey, reported)

Murphy's model-based RL chapter credits DreamerV3 as the earliest method to collect Minecraft diamonds with no human demonstrations, though it needed 17 days of training. It describes DreamerV4 as a latent video diffusion transformer world model fitted offline to Minecraft video that carries actions but no rewards, with the policy then trained entirely in imagination (behaviour cloning first, then actor-critic). DreamerV4 samples in 1-2 diffusion steps via a shortcut trick, since iterative diffusion is slow to sample.

## Limits

- The survey section on Dreamer is secondhand: Murphy runs no experiments, and the 17-day and DreamerV4 statements are cited from other work.

- By the authors' own concession, a diamond shows up in just 0.4% of episodes at the 100M-step budget.
- The model is 200M or 12M parameters and the replay ratio differs per benchmark, so "fixed" covers only the main hyperparameter table.
- On Atari100k EfficientZero scores higher (gamer mean 190 against 125) but relies on online search and early resets, which the authors say makes comparison difficult.
- The DMLab baselines run to 1B steps while Dreamer runs to 100M, since 10B-step runs were infeasible. ProcGen used 1 seed, and Dreamer scores 0.01 on BSuite exploration against 0.68 for Boot DQN.
- The Minecraft environment is a modified MineRL (early termination removed, jump held for 200 ms) and the authors set the evaluation protocol themselves.
- Every experiment is a simulator or game; no language models are involved.
- The text gives a prediction horizon T = 16 while the hyperparameter table lists an imagination horizon H = 15.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Deep Q-Network, Target Network and Experience Replay]] — alternative-to (model-free value-based agent on the same Atari suite)
- [[Arcade Learning Environment]] — prerequisite-for
- [[Dyna Planning]] — related (the imagined-experience idea Dreamer cites)
- [[LingBot-World Open-Source World Model]] — related
