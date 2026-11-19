---
title: Arcade Learning Environment
tags: [llm, reinforcement-learning, benchmark]
summary: "The Arcade Learning Environment wraps the Atari 2600 emulator as an RL environment with a train/test split over games; its 2013 paper benchmarks five linear Sarsa(lambda) agents and two search agents on 55 games, and search won most games (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-bellemare-2013-arcade-learning-environment.md
---

# Arcade Learning Environment

Bellemare et al. set out to measure general, domain-independent agents on a wide range of Atari 2600 games. The Arcade Learning Environment (ALE) puts the Stella emulator for that console behind an RL interface. Their hypothesis is that a split over games, tuning on a few and scoring once on unseen ones, is a rigorous test of general competence. The DQN papers reuse its games and protocol ([[Deep Q-Network, Target Network and Experience Replay]]).

## Protocol

- The suite has 55 games: 5 for training and 50 for testing, the test games sampled at random from 123 eligible titles. Each agent acts every 5 frames, and an episode lasts 18,000 frames.
- An RL trial is 5,000 learning episodes followed by 500 scored episodes, with results averaged over 30 trials.
- Five linear SARSA(lambda) agents differ only in their features (Basic, BASS, DISCO, LSH, RAM). Two search agents treat the emulator as a model: full-tree breadth-first search, and UCT with 500 simulations per action, depth 300 and exploration constant 0.1. Reference points are the Random, Const and Perturb baselines and a beginner human.
- For inter-algorithm normalisation, the lowest and highest scores any of the algorithms reaches set the scale, so the normalised score z falls in [0, 1].

## Results (self-reported)

- The learners finished above the baselines in 40 of the 55 games. Search, whether full-tree or UCT, finished above learners and baselines in 49 of 55, and UCT is the top agent in 45 games of the search table. Among the RL methods BASS is strongest, topping 17 of 55 games.
- Freeway, Private Eye, Montezuma's Revenge and Venture are sparse-reward games where search is not the best agent.
- The RAM-feature agent was no better than the image-feature ones. DISCO scores acceptably on the training games and falls steeply on unseen ones, which the authors offer as evidence that the split is worth having.
- In a paired comparison (Welch t-test, 99% confidence interval), BASS beats DISCO in 48 games and loses in 5.
- Two pitfalls in summarising across games: scores normalised against a random agent blow up when the random score is close to 0 (Freeway, where random scores about 0 and learners 10 to 20; a worked example), and a plain average over games is dominated by outliers (LSH appears to lead only because of Zaxxon).
- Planning one second ahead exhaustively would take roughly 10^75 simulation steps (18 actions each of 60 frames, 18^60).

## Limits

- The human reference is one beginner averaging five episodes on selected games, and the authors call it neither exhaustive nor accurate.
- Test games were chosen from titles with Wikipedia pages. Spread is measured over 30 trials for RL agents and 10 episodes for search.
- The search agents assume a perfect emulator model and need about 15 seconds per action, so they run slower than real time and cannot be fairly set beside model-free learners.
- Features are hand-designed and the learners are linear SARSA(lambda); no deep networks appear.
- The authors concede that summarising scores across games needs more work, and that sparse-reward games call for long-horizon planning these methods lack.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Deep Q-Network, Target Network and Experience Replay]] — related (deep network agent evaluated on these games)
- [[DreamerV3 World Model with Fixed Hyperparameters]] — related (also evaluated on Atari)
