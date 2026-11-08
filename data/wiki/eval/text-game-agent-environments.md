---
title: Text-Game Agent Environments (Jericho, ALFWorld, CALM)
tags: [eval, comparison]
summary: "Three 2020-era pieces of the text-game line of agent evaluation: Jericho (an interface to human-made interactive fiction, with template actions), CALM (a language model trained on human play that proposes candidate actions) and ALFWorld (text games mirroring embodied household tasks, where text training transferred to the embodied side); all numbers self-reported, RL-era agents only."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-hausknecht-2020-interactive-fiction-games.md
  - data/raw/papers/2026-11-07-yao-2020-keep-calm-explore.md
  - data/raw/papers/2026-11-07-shridhar-2020-alfworld.md
---

# Text-Game Agent Environments (Jericho, ALFWorld, CALM)

The three papers here all involve text games, but not one continuous line: CALM builds on Jericho (it is an agent component evaluated on Jericho's games), while ALFWorld comes from a separate line, pairing TextWorld text games with ALFRED's visual household tasks. The agents below are 2020 reinforcement-learning and imitation systems, not LLM agents.

## Jericho (Hausknecht et al., preprint, arXiv 1909.05398)

Jericho is an OpenAI-Gym-style Python interface to human-made interactive fiction with score-based reward, save and load, templates, vocabulary and world-change detection. Its template action space is built by filling templates with vocabulary words and keeping those that change the game world. The authors argue it is far smaller than raw word combinations: a 4-word action over a 700-word vocabulary gives 240 billion possibilities, and Zork1 with 237 templates and 697 words has 115 million template actions (illustrative counts).

Setup: 32 games and five runs, comparing a random agent, the untrained heuristic NAIL, the choice-based RL agent DRRN and the new Template-DQN; hyperparameters were tuned on Zork1.

- DRRN had the highest average progress, DRRN scored 32.6 of 350 on Zork1, and no agent scored on five games (self-reported).

## CALM (Yao et al., EMNLP 2020)

CALM trains a GPT-2 (or bigram) language model on ClubFloyd human play transcripts to propose top-k candidate commands given the previous two observations and the previous action. A DRRN agent then learns Q-values over those candidates on Jericho while CALM stays frozen. An admissible action is one the parser accepts and that changes game state; the DRRN and KG-A2C setups it is compared with are handed the admissible list as a handicap, which CALM does without.

Setup: 28 Jericho games, k=30 with DRRN, mean over the final 100 episodes, averaged over seeds.

- CALM (GPT-2) reached 9.4% average normalised score against 5.6% for NAIL, a gain of almost 69%, and beat handicap-assisted DRRN and KG-A2C on 8 of 28 games, though those two average 13.0% and 10.8% overall (self-reported).
- Variants (single runs): no pre-training 6.8%; adding 8 transcripts of the evaluation games 10.9%; k=10, 20 and 40 gave 5.6%, 9.6% and 9.2%; a random agent over CALM's top 30 actions scored 1.8%.
- Had RL fully used the best scores seen during exploration, the average would reach 14.7% (self-reported).

## ALFWorld (Shridhar et al., ICLR 2021)

ALFWorld pairs ALFRED embodied tasks with PDDL-derived TextWorld games. The BUTLER agent has a text policy learned with DAgger from a rule-based expert, a template-based visual state estimator and an A* controller, and runs zero-shot in the embodied world.

Setup: All Tasks, embodied transfer, average of three runs unless stated.

- Trained only in text, BUTLER reached 19% seen and 10% unseen embodied success; with perfect perception and navigation, 37% and 26%; pure text success was 40% and 35%. Human-annotated goals dropped it to 8% and 3%; a behaviour-cloning Seq2Seq baseline scored 6% and 5% (self-reported).
- Setup: 50K episodes with oracle state estimation and control, peak per split. Text-only training reached 34.3% unseen against 23.1% for embodied-only training, but embodied-only was higher on seen (33.6 against 27.1), and text training ran about 7 times faster (self-reported).

## Limits

- Jericho: agents were trained and evaluated on one game, with no unseen-game test; handicaps differ across agents (DRRN and Template-DQN use save/load and valid-action detection, NAIL none), so the authors give scores as benchmarks, not a like-for-like ranking. NAIL was developed on many of the games, and scores are training-episode means.
- CALM: variant ablations are single runs without significance tests; a plus-minus in one table is undefined; the authors say DRRN does not stably reach the best scores seen and the games are far from solved; their explanation for beating the handicap on some games is untested. The n-gram data split is 90/10 in the main text but 70/30 in the appendix, and neither compute nor DRRN hyperparameters are given.
- ALFWorld: only a subset of ALFRED, strong template and map assumptions, large text-to-embodied gap, human-goal results are preliminary, the best of 8 seeds per split is selected, and no significance tests or compute are reported. The main text says 100K training episodes and an appendix says 50,000.
- None of the three evaluates LLM agents.

## See Also
- [[AgentBench]] — related (reuses ALFWorld as its House Holding environment)
- [[MINT Multi-Turn Benchmark]] — related (reuses ALFWorld for decision-making)
- [[InterCode]] — related
