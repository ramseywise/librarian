---
title: BeaverTails Decoupled Safety Preference Dataset
tags: [llm, preference-and-alignment, reference]
summary: "A dataset that annotates harmlessness and helpfulness separately on red-team QA pairs, with a 14-category safety meta-label, used to train reward and cost models and a PPO-Lagrangian Safe RLHF run on Alpaca-7B."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-ji-2023-beavertails.md
---

# BeaverTails Decoupled Safety Preference Dataset

Ji et al. (NeurIPS 2023 Datasets and Benchmarks) test whether safety alignment, through moderation and RLHF, gains from a QA dataset whose harmlessness and helpfulness annotations are kept apart. Their hypothesis: separate annotations, plus a cost model built from safety rankings, outperform one blended preference score or a classifier-based cost. Baselines are PPO on a single blended preference score and PPO on HH-RLHF data.

## Construction

- Red-team prompts each receive several Alpaca-7B responses, which are annotated in two stages: first a safety meta-label across 14 harm categories, then separate rankings for helpfulness and for harmlessness.
- The release has safety meta-labels on 333,963 QA pairs and 361,903 expert comparison pairs, ranked separately for helpfulness and harmlessness.
- A QA pair counts as harmful or harmless according to its risk neutrality extent, meaning how far a positive response can defuse the risks carried by a question that may be harmful.
- Reward and cost models start from Alpaca-7B and use Bradley-Terry losses ([[Bradley-Terry Preference Model]]); Alpaca-7B is then tuned with PPO-Lagrangian (Safe RLHF) and compared with ablations through the win rate under a prompted GPT-4 judge.

## Results

The extraction lacks numbers for most rows, so these are qualitative and (self-reported):

- Crowdworkers agree more on the safety meta-label than on preference rankings, and two-stage annotation raised agreement in quality-control checks.
- Against Alpaca-7B fine-tuned on BeaverTails-30k (prompted GPT-4 judge), Safe RLHF wins most comparisons on helpfulness and on harmlessness.
- PPO on a blended single-score preference gets a lower harmlessness win rate than Safe RLHF, and so does PPO on HH-RLHF data.
- Ranking with the cost model beats an ensemble of 14 binary classifiers.
- Safe RLHF failures show up at temperature 1.0, with lower temperature helping; this is a qualitative observation.

## Limits

- The annotator team is demographically narrow; crowdworkers were paid between USD 7.02 and 9.09 an hour.
- The 14 categories overlap, may omit some harms, and are unbalanced in places (Child Abuse, Animal Abuse).
- Learning rate, batch size, steps and hardware are unstated. A single prompted GPT-4 judge produces the win rates; seeds and significance tests are absent and the count of evaluation prompts is not given.
- Only Alpaca-7B wrote the responses. At high temperature, Safe RLHF continues to fail on some prompts.
- Honesty goes unused; it is treated as equivalent to safety, apart from law, morality and personal safety.

## See Also
- [[Constitutional AI and RLAIF]] — related (harmlessness handled by separating it from helpfulness)
- [[RLHF Pipeline]] — prerequisite-for (the reward-model and PPO stages it adapts)
- [[Bradley-Terry Preference Model]] — prerequisite-for (loss for the reward and cost models)
- [[LM Red Teaming]] — related (red-team prompts as the data source)
