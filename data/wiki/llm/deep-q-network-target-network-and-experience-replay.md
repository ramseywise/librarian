---
title: Deep Q-Network, Target Network and Experience Replay
tags: [llm, reinforcement-learning, concept]
summary: "A Deep Q-Network fits a convolutional network to the Bellman target from raw Atari pixels and keeps that training stable with a replay memory sampled at random, stacked frames and (in the 2015 version) a periodically cloned target network; the two Mnih papers report Atari scores and ablations, and a textbook chapter implements it on Breakout."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch09-deep-reinforcement-learning.md
  - data/raw/papers/2026-11-07-mnih-2013-dqn-atari.md
  - data/raw/papers/2026-11-08-mnih-2015-human-level-control-through-deep.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch16-applications-case-studies.md
  - data/raw/papers/2026-11-08-ahilan-2023-succinct-summary-reinforcement-learning.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch04-deep-q-networks.md
  - data/raw/papers/2026-11-08-murphy-rl-ch02-value-based-rl.md
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

## The 2013 and 2015 Atari papers

Mnih et al. (2013) ask whether a single convolutional network, trained by a variant of Q-learning, can learn control directly from raw pixels. The network has one output per action, takes the last 4 preprocessed frames, and trains online with RMSProp on minibatches drawn uniformly from a replay memory, behaving epsilon-greedily. Replay memory holds the one million most recent frames, and each game was trained for 10 million frames. Rewards are clipped to +1/-1 during training only. The paper reports state of the art on six of seven ALE games and better than a human expert on three (self-reported). Average scores against its human reference: Breakout 168 vs 31, Pong 20 vs -3, Enduro 470 vs 368, Beam Rider 4092 vs 7456, Q*bert 1952 vs 18900, Seaquest 1705 vs 28010, Space Invaders 581 vs 3690 (self-reported; epsilon 0.05, evaluation step count not stated). It tracked average predicted Q on a fixed set of states gathered with a random policy on Breakout and Seaquest and saw it rise smoothly with no divergence, while episode reward stayed noisy (self-reported). The benchmark is described on [[Arcade Learning Environment]].

Mnih et al. (2015) add a target network, cloned from the Q-network every C updates (C = 10,000 parameter updates) and supplies the Q-learning targets for the next C updates. Each of 49 games gets its own network trained with identical settings: 4 stacked 84x84 luminance frames in, conv layers of 32 (8x8, stride 4), 64 (4x4, stride 2) and 64 (3x3, stride 1) filters, a 512-unit fully connected layer, and 4 to 18 linear outputs. Other settings: minibatch 32, discount 0.99, frame skip 4, replay memory of 1,000,000 frames, epsilon falling linearly from 1.0 to 0.1 across the first million frames, Bellman error clipped to [-1, 1], 50M training frames, chosen by informal search on 5 games.

- DQN beat the best earlier RL methods on 43 of 49 games and scored over three quarters of the human reference on 29 of 49 (self-reported; evaluation 30 episodes of up to 5 minutes at epsilon 0.05, human reference a professional tester after about 2 hours of practice).
- Ablation on five games at 10M frames, best of 3 learning rates, best checkpoint reported (self-reported; values from an image table): Breakout 316.8 with replay and target network, 240.7 with replay only, 10.2 with target network only, 3.2 with neither. Seaquest ran 2894.4, 822.6, 1003.0 and 275.8 across the same four settings.
- Swapping the convolutional network for one linear layer, with replay and target network kept, gave Breakout 3.00 against 316.8 and Seaquest 656.9 against 2894.4.
- The authors suggest prioritised sampling for the replay memory and concede that reward clipping removes reward-magnitude information.

The textbook chapter on applications restates the 2015 result: training of 50 million frames per game (roughly 38 days of play), and a comparison in which DQN outscored the human tester on 22 games (reported there, secondhand). The same chapter lists replay and the periodically frozen target network among the practices that stabilise bootstrapped Q-learning with function approximation. A summary paper says experience replay breaks correlation between samples and that a target network stops a runaway TD target, synced at intervals or by Polyak averaging. Why bootstrapped learning with approximation can diverge at all is on [[The Deadly Triad]].

## Extensions and practical numbers

Murphy's value-based RL chapter (survey, reported) lists the usual fixes. Double Q-learning curbs overestimation; dueling splits Q into V plus advantage minus its mean; prioritised replay samples with priority (delta + eps)^alpha, where alpha = 0 is uniform; REDQ keeps N > 2 Q-networks, takes the minimum over a random subset of M, and relies on an update-to-data ratio well above 1. Target networks can be an exponential moving average (rho about 0.999). A LayerNorm critic with bounded final-layer weights is said to suffice for off-policy nonlinear TD to converge. Rainbow uses n = 3; BBF on Atari-100k anneals n from 10 to 3 and gamma from 0.97 to 0.997 and drops noisy nets. Agent57 needed 80B frames, which MEME cut to 200M.

Winder's chapter lists Rainbow's parts as C51, prioritised replay, noisy nets and dueling. On Coach with a Tesla P4 VM, DQN averaged 4.8 h and about $5.80 per million frames against Rainbow's 7.6 h and about $8.50, and Rainbow needed about 0.5M more frames than DQN for a similar Pong result. He advises weighing its gain against the near doubling of compute. On CartPole a random policy lasts about 25 steps, and tabular Q-learning matched DQN only after feature engineering left about 150 discrete states. A BCQ agent converged with stable Q-values on a DQN-generated replay buffer where a DQN agent trained on the same buffer diverged (figure only).

## Limits

- The chapter prints no numeric results; performance appears only in two figures.
- Code is TensorFlow 1.x with gym CartPole-v0 and Breakout-v0, not runnable on current stacks, and it has bugs. Among them: the naive-returns loop iterates an empty range, the "solved" checks use the wrong slice of episode rewards, `sample_batch` hands back discounted returns where the terminal flag belongs, the annealing text says epsilon rises while the code lowers it, and the policy loss uses return with no baseline.
- The prose says `build_model` returns three action nodes although CartPole has two actions.
- Only methods from 2013 to 2016 appear (DQN, A3C, UNREAL, DRQN); PPO, TRPO, DDPG, SAC, double and dueling DQN, prioritised replay and RLHF are absent.
- The 2013 paper does not state its learning rate, gamma, RMSProp decay or evaluation step count, uses only seven games, has no target network, and gives no convergence guarantee (stability is shown empirically). Its human scores are the authors' own and run far above the ones in the ALE paper.
- The 2015 paper's hyperparameters came from informal search on 5 games, with no seeds or run-to-run variance reported. Its ablation uses 5 games, 10M frames and the best checkpoint, so the numbers are optimistic maxima, and the table values were read from an image. The human baseline is one professional tester over about 20 episodes. Montezuma's Revenge, which needs planning over long stretches, stays at a score of 0.
- The applications chapter says 29 of 46 games reach the 75% threshold where the paper says 29 of 49; the paper's figure is used above.

- The Ahilan summary reports no experiments, is secondary (drawn from Silver's course and Sutton and Barto), and mostly sketches or defers its proofs.
- Winder's cost comparison covers 2 games, one run each, with differing default hyperparameters, and he calls it only an indicator; the chapter predates 2021, training stopped early and no reward numbers are printed. Murphy's Rainbow diminishing-returns point rests on one figure, and its state-of-the-art statements are as of 2024.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Multi-Agent Reinforcement Learning]] — related
- [[Arcade Learning Environment]] — prerequisite-for (the games and evaluation protocol the DQN papers use)
- [[The Deadly Triad]] — prerequisite-for (why bootstrapping with function approximation is unstable)
- [[DreamerV3 World Model with Fixed Hyperparameters]] — alternative-to (model-based agent evaluated on Atari too)
- [[Q-Learning]] — prerequisite-for (the tabular update and its convergence proof)
- [[Temporal-Difference Learning, Sarsa and Expected Sarsa]] — prerequisite-for
- [[Semi-Gradient TD and Tile Coding]] — related (function approximation with bootstrapping)
