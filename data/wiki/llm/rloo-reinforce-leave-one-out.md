---
title: RLOO REINFORCE Leave-One-Out
tags: [llm, preference-and-alignment, pattern]
summary: "RLOO samples k completions per prompt and uses the mean reward of the other k-1 as each sample's baseline, treating the whole generation as one action; one paper reports it beating PPO, DPO and RAFT on TL;DR and Anthropic-HH with 6.9B and 7B models."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-ahmadian-2024-back-basics.md
  - data/raw/papers/2026-11-08-murphy-rl-ch06-llms-rl.md
---

# RLOO REINFORCE Leave-One-Out

Ahmadian et al. ask if RLHF for language models can skip PPO's computational and optimisation overhead without losing quality. Their premise is that the policy begins from a strong pretrained or SFT model, so extreme variance and big off-policy steps seldom occur, which would make PPO's clipping, variance reduction and token-level modelling unneeded.

## Mechanism

- **REINFORCE (this work)** applies the REINFORCE estimator to the return of the entire trajectory, so the whole generation counts as one action, with a moving-average baseline.
- **Vanilla PG** applies the estimator to the return from each partial completion and learns a baseline; it is PPO with lambda=1, no clipping and no ratio.
- **RLOO** draws k i.i.d. samples per prompt from the current policy and gives each sample the average reward of its k-1 siblings as baseline:

```
grad = mean over i of [ R_i - mean over j!=i of R_j ] * grad log pi(y_i|x)
```

The estimator comes from Kool et al. (2019). The paper pits it against PPO, Vanilla PG, RAFT and [[DPO Loss and Implicit Reward]] on two datasets, Reddit TL;DR and Anthropic-HH, using Pythia-6.9B for both and Llama-7B. Quality is judged by reward model and by simulated GPT-4 win rates (the AlpacaFarm setup; see [[AlpacaFarm Simulated Human Feedback]]).

## Results

All numbers are (self-reported), one run per cell.

- RLOO (k=4) outscores PPO in win rate by 10.3 points on TL;DR (Pythia-6.9B, GPT-4 judging against the reference SFT completions, at the checkpoint with best test reward), 14.5 on HH with Pythia, and 32.1 on HH with Llama-7B, where PPO wins only 32.0.
- TL;DR win rates with Pythia-6.9B: RLOO (k=4) at 77.9, RAFT (k=4) at 73.2, Vanilla PG at 70.4, DPO at 66.6.
- A moving-average-baseline REINFORCE equals or exceeds Vanilla PG (HH Pythia 37.9 against 36.4; HH Llama 55.3 against 52.3), so modelling partial completions is unnecessary. The paper's headline margin for Vanilla PG over PPO runs from 3.2% to 20.3% in win rate.
- Under 5% of PPO's loss terms per batch are clipped on average, meaning updates stay close to on-policy. In the Llama-7B HH ablation, reward drops steadily as GAE lambda is lowered through 0.95 and 0.5 to 0.0 from 1.0.
- RLOO at k=2 equals or beats RAFT at k=4 with half the online samples. Averaged over three dataset-model pairs, RLOO averages 61.9 at k=4 and 61.3 at k=2; RAFT averages 59.5 and 56.1 at the same k.
- On HH with Llama, DPO yields the longest outputs (104.4) and PPO the shortest (16.5). With a baseline, REINFORCE has 27% lower reward variance than Vanilla PG (Llama HH: 2.7 against 3.7).
- RAFT reacts more strongly than RLOO to raising the KL weight (0.25 up to 1.0, HH Pythia, k=2), and loses much more reward when Gaussian noise (sigma 3.0 and 5.0) is added to reward-model logits.
- For the Llama SFT model used on HH, about 60% of the probability sits on the top token once past the first generated token, and more than 90% on the top 16.
- Murphy's survey chapter (algebraic derivation, Eq 6.27-6.28) shows the Dr GRPO advantage equals the RLOO advantage up to a factor of J/(J-1).

## Limits

- Reward-model over-optimisation is not investigated (see [[Reward Model Overoptimization Scaling Laws]]), and the leave-one-out baseline is untried with per-token actions and intermediate rewards.
- Evaluation uses simulated GPT-4 win rates only, with no measured link to human judgement and no other reward types (ROUGE, BLEU).
- No seeds, error bars or significance tests; just 6.9B and 7B models; PPO ablations only on Llama-7B HH; code, hardware and compute are unstated.
- PPO's win rate on HH with Llama (32.0) is extremely low and its learning-rate sweep had only two values (1e-6, 1e-5), so some of the large gap may come from how PPO was tuned.

## See Also
- [[RLHF Pipeline]] — prerequisite-for (PPO is its Stage 3, the method this ablates)
- [[DPO Loss and Implicit Reward]] — alternative-to (offline baseline in the same comparison)
- [[Preference Optimization Algorithms]] — prerequisite-for (the family RLOO is compared within)
- [[Reward Model Overoptimization Scaling Laws]] — related (the over-optimisation question this paper leaves open)
