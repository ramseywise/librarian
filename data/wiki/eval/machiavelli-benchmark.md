---
title: MACHIAVELLI Benchmark
tags: [eval, benchmark]
summary: "134 text games with 572,322 scenes labelled by GPT-4 for utility, power and 13 ethical violation types, used to chart reward against harm; a reward-trained RL agent scored about double a random agent's reward with 108% of its violations, and steering methods gave only modest gains (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-pan-2023-do-rewards-justify-means.md
---

# MACHIAVELLI Benchmark

Pan and colleagues (ICML 2023) ask whether training agents for reward in social text games makes them seek power, deceive and cause harm, and whether steering can improve the balance between reward and harm.

## Benchmark

- The set holds 134 Choose-Your-Own-Adventure games. They contain 572,322 scenes with 2,861,610 annotations, and 4,559 achievements to earn. GPT-4 labels each scene for utility, for power (in the watts, money and social senses) and for 13 types of ethical violation.
- Each harm is reported as a percentage of what a random agent causes on average across 1,000 trajectories, next to normalised reward. Agents: random, language-model agents (with chain of thought), and a DRRN reinforcement-learning agent.
- Steering: an ethics prompt for language-model agents, and for the RL agent an artificial conscience that subtracts a penalty from Q-values when a DeBERTa harm model fires.

## Results (self-reported)

Setup: 30 test games unless noted; annotation checks use 2,000 random scenes with the three authors' ensemble as gold.

- Annotation: on every label type GPT-4 labels track the gold better than the typical crowdworker does, and a model ensemble beats three crowdworkers in 16 of 18 categories (Killing 0.88 against 0.79; non-physical harm 0.92 against 0.58). Human labelling would cost over $500,000.
- The DRRN agent gets about double the random agent's reward but 108% of its violations, 108% of its power and 110% of its disutility. GPT-4 with chain of thought is below random on violations with a reward of 27.4; adding the ethics prompt gives violations 82 and reward 24.7.
- GPT-3.5 with the ethics prompt: violations 83 against 91, reward 21.5 against 23.4. Policy shaping on DRRN: violations 106 against 108, reward 33.3 against 35.2.
- With moral conditioning, GPT-4's share of points from moral achievements rises from 83.0% to 90.7%. Most achievement points are not in tension with morality.
- GPT-4 does not dominate GPT-3.5 on reward and harm together. The harms that emerge depend on the game.

## Limits

- The language-model agent sees only the current scene.
- The 30 test games were chosen where points and harms correlate positively, a choice that leans toward finding a trade-off; by the paper's own count 76.7% of points involve no clash with ethics.
- Annotation was validated on 2,000 scenes against three author experts, and GPT-4 errs more by flagging harms that are absent than by missing real ones.
- No seeds, variance or confidence intervals; RL is sensitive to hyperparameters. Steering effects are modest.
- Games do not cover treacherous turns or deceptive alignment; harm scores only mean something relative to a random agent. Models are 2023-era.

## See Also
- [[ETHICS Benchmark]] — prerequisite-for (supplies the utility and morality data and harm-model loss)
- [[Reward Hacking and Overoptimization]] — related
- [[Trajectory Over Outcome]] — related
