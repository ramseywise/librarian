---
title: Self-Critiquing Models for Human Evaluators
tags: [eval, concept]
summary: "Saunders et al. fine-tune language models to write critiques of summaries and find that showing eight model critiques lets human labelers find about 50 percent more flaws, including 45 percent against 27 percent of deliberately planted ones (self-reported, 2022-era models)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-saunders-2022-self-critiquing-models-assisting-human.md
---

# Self-Critiquing Models for Human Evaluators

Saunders et al. (2022 preprint). The hypothesis is that checking a critique is easier than checking the original answer, so critique assistance should help people evaluate outputs that are hard to judge directly.

## Method

Decoder models in the GPT-3 style get supervised fine-tuning together on a base task (topic-based summarisation) and on four auxiliary tasks: critiqueability (whether an answer has flaws), critique, helpfulness (whether a critique names a real shortcoming) and refinement. Data came in three rounds of human collection. Next, labelers write critiques while eight model critiques are either shown or hidden. Using best-of-N, the paper also measures generator, discriminator and critique gaps (GDC gaps) and adds four synthetic tasks that have oracles.

## Results (self-reported)

Setup: topic-based summarisation on held-out passages of 2,048 to 3,840 tokens, best fine-tuned model as critic, eight model critiques shown.

- Labelers with assistance wrote about 50% more critiques over model, human and human-misleading answers. When answers were deliberately misleading, they caught the planted flaw 45% of the time versus 27% without help. Valid critiques per answer averaged 0.96 assisted and 0.62 unassisted, and just 15.3% of model critiques that were used got edited.
- For model answers, assisted labelers produced critiques for 78% of inputs and unassisted ones for 54%. Time per task barely differed (6.26 versus 6.27 min).
- The fine-tuned critic was more helpful than InstructGPT baselines and less than humans. Larger models were better at self-critiquing even though their answers were harder to critique.
- Conditional refinement beat direct refinement only when critiques were chosen best-of-N against helpfulness, and small models did not improve. Best-of-8 direct refinement looks like a stronger baseline than critique-conditioned refinement at equal compute.
- The critique-discrimination gap was positive and roughly constant across scale for summarisation, negative for Addition and RACE, and positive for 3-SAT, with no clear trend closing it. A naive two-step debate discriminated worse than the critiqueability score.

## Limits

- Summarisation lacks ground truth, labelers may trust summaries too much, and a misleading critique of a good answer looks the same as a good critique of a poor one. Humans need up to about ten minutes per task, so there is little speed-up to gain, and transfer to harder tasks is not shown.
- Only supervised fine-tuning is used, no RL, and the setup calls for large models, plenty of human data and several rounds. Parameter counts and hyperparameters are not given. Agreement on comparisons sat near 75%, and refinement results are noisy.

## See Also
- [[Shepherd Critic Model]] — related
- [[MetaCrit Adaptive Critique]] — related
- [[Constitutional AI and RLAIF]] — related
- [[RLHF Pipeline]] — related
