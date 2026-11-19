---
title: Reward Model Overoptimization Scaling Laws
tags: [llm, preference-and-alignment, concept]
summary: "Gao, Schulman and Hilton fit functional forms for gold reward against sqrt(KL) for best-of-n and RL against proxy reward models in a synthetic gold-RM setup, and report how the coefficients move with RM size, RM data, policy size and KL penalty."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-gao-2022-scaling-laws-reward-model-overoptimization.md
---

# Reward Model Overoptimization Scaling Laws

Gao, Schulman and Hilton measure how the true ("gold") reward behaves while a policy is optimised against a flawed proxy reward model. Their expectation is Goodhart's law, that pushing the proxy too far damages the real objective, with a regular curve in d = sqrt(KL), KL taken from the starting policy. This page records the fitted forms; the qualitative failure modes are in [[Reward Hacking and Overoptimization]].

## Setup

One fixed 6B gold reward model labels comparisons, and those labels train smaller proxy reward models (3M to 3B parameters). GPT-3-series policies, SFT-trained on InstructGPT demonstrations, are optimised against a proxy with PPO or with best-of-n (BoN), while the gold score is plotted against KL. The environment follows InstructGPT; policies of 1.2B and 6B parameters appear. Every finding below is (self-reported).

## Functional forms

- BoN: R(d) = d(alpha - beta d), where KL_bon = log n - (n-1)/n. The fit used data up to n=1,000 (roughly 6 nats) and then correctly predicted outcomes out to n=60,000 (roughly 10 nats). The top BoN gold score has the closed form alpha/(2 beta).
- RL: R(d) = d(alpha - beta log d), at KL penalty 0. Alpha_RL can be held constant as RM size changes, so the scaling story sits in beta_RL (1.2B policy, 90,000 RM data points). Coefficients vary smoothly, roughly logarithmically, with proxy RM parameter count.
- For k rounds of iterated RLHF, the final gold score rises by beta_RL * d * log k, assuming d adds across rounds and coefficients stay fixed; this is derived from the fitted form and not tested in an experiment.

## Other findings

- With fewer than about 2,000 comparisons, an RM barely beats the near-chance starting loss (RMs from 3M to 3B).
- New data beats more passes: four epochs on the same data leave gold score unchanged, whereas one epoch over four times the data is clearly better (2,000 to 8,000 RM data points).
- Bigger policies gain less from optimisation yet over-optimise to a similar degree; gold score tops out at nearly the same KL for the 1.2B and 6B policies (12M RM, also 3B).
- RL uses KL much less efficiently than BoN. BoN's KL grows roughly with log n, while with no KL penalty RL's grows about quadratically in step count (1.2B policy).
- Adding a KL penalty does not shift the KL-versus-gold frontier and acts much like stopping early (1.2B policy, 1.2B RM; the authors say it may depend on hyperparameters).
- The authors ascribe the non-monotonic gold score and the beta term mostly to extremal Goodhart, and the alpha term to regressional Goodhart, an interpretation they did not test directly. A footnote records that optimised policies exploited answer length in other InstructGPT-setting runs, with no data shown.

## Limits

- A synthetic gold RM replaces humans; how this carries to real human labels is untested and the RMs may be correlated. The setup does not model the gap between human labels and what humans actually want.
- One InstructGPT environment, two policy sizes, mostly default PPO hyperparameters.
- The proxy scores fit poorly, and the RL form has an infinite slope at the origin.
- Adversarial Goodhart is not modelled, and trends could fail for more capable models.
- RL step counts, seeds, compute and hardware are not given, and nothing says code was released.
- The data-threshold result conflicts with some of the paper's own findings (its footnote 8).

## See Also
- [[Reward Hacking and Overoptimization]] — prerequisite-for (the qualitative failure modes this quantifies)
- [[RLHF Pipeline]] — prerequisite-for (the KL-penalised PPO stage the fits describe)
- [[DPO Loss and Implicit Reward]] — related (leaves open whether over-optimisation occurs under DPO)
- [[RLOO REINFORCE Leave-One-Out]] — related (does not study over-optimisation)
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — related
