---
title: DPO Loss and Implicit Reward
tags: [llm, preference-and-alignment, concept]
summary: "Direct Preference Optimization rewrites the Bradley-Terry preference loss over the policy itself, using beta times the log-ratio to a reference model as an implicit reward, and what the DPO paper measured against PPO RLHF at up to 6B parameters."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-rafailov-2023-dpo.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch04-alignment.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch06-preference-alignment.md
---

# DPO Loss and Implicit Reward

Direct Preference Optimization (DPO; Rafailov et al., NeurIPS 2023) trains a language model on human preference data with a plain classification loss. It targets the same KL-constrained reward objective as the [[RLHF Pipeline]], with no separate reward model and no RL loop. The authors' hypothesis: rewriting the [[Bradley-Terry Preference Model]] loss in terms of the optimal policy (instead of the reward) should let DPO equal or beat PPO-based RLHF with less complexity and more stability.

## The loss

The training set is a fixed offline collection of preference pairs, and the reference policy pi_ref is the SFT model. DPO minimises

```
L = -log sigmoid( beta * (r_w - r_l) ),  r = log pi_theta(y|x) - log pi_ref(y|x)
```

with yw the chosen and yl the rejected completion. The **implicit reward** is beta times the log-ratio of the trained policy to the reference, so the language model plus its reference model define a reward. Two rewards are equivalent when they differ by a term depending only on x; the paper's Theorem 1 says the reparameterisation therefore gives up no generality over reward classes. Each example's gradient is scaled by how badly the implicit reward misorders that pair, and the authors report that dropping this scaling makes the model degenerate.

The appendix code computes `-F.logsigmoid(beta * (pi_logratios - ref_logratios))` and takes rewards as `beta * (pi_logps - ref_logps).detach()`.

## What the paper measured

Judging is by GPT-4 unless noted, and every figure is (self-reported).

| Task and setup | Result |
|---|---|
| TL;DR, GPT-J 6B SFT, DPO beta 0.5, GPT-4 (C) prompt, win rate against reference summaries | DPO about 61% at temperature 0.0; PPO with a learned reward 57% at its best temperature (0.0) |
| TL;DR, human study | DPO at temperature 0.25 preferred to PPO at temperature 0 |
| Same pairing, GPT-4 (C) against humans | GPT-4 gives DPO a 54% win rate over greedy PPO, humans 58%; GPT-4-human agreement is 67 against 65 between humans |
| IMDb sentiment, GPT-2-large, 22-run sweep, true reward from a classifier | DPO traces the best reward-KL frontier, ahead of PPO even given the ground-truth reward |
| Transfer: train on Reddit TL;DR, test on CNN/DailyMail at temperature 0 | DPO has the higher win rate against ground-truth summaries than PPO |
| Anthropic-HH, Pythia-2.8B, one-step test subset, win rate against the chosen completion | The only efficient method that beats the dataset's chosen completions; Best-of-N flattens near 64-128 samples |

Further observations:

- A publicly released PPO-trained HH model (reciprocate/ppo_hh_pythia-6B) did no better than base Pythia-2.8B under any prompt or temperature tried.
- Unlikelihood training emitted repeated-token gibberish on summarisation and dialogue, so it serves only as a sentiment baseline.
- DPO outputs can be wordy and invent facts, and GPT-4 occasionally judged wrongly on the HH examples the paper shows.

## LLM Engineer's Handbook DPO run

The LLM Engineer's Handbook DPO run on TwinLlama-3.1-8B (preference data mlabonne/llmtwin-dpo, blog-style imitation) set beta to 0.5 where 0.1 is the usual value, a learning rate of 2e-6 against 3e-4 for its SFT run, and 1 epoch against 3.

## Xiao and Zhu on DPO

Xiao and Zhu derive DPO in the same notation as their Bradley-Terry reward model and PPO sections, and advise it where training a reward model and sampling online cost too much.

## Limits

- The largest model is 6B; behaviour at larger scale is untested.
- Distribution-shift evidence is a single CNN/DailyMail experiment.
- Whether DPO suffers reward over-optimisation is left open; a small dip in the paper's Fig 3 (right) may be an example (compare [[Reward Model Overoptimization Scaling Laws]], which studies proxy reward models).
- GPT-4 win rates move with the judging prompt; the S prompt favours longer summaries than humans do.
- Beta received little tuning, so the authors suggest DPO is understated. Seeds, significance tests, compute and hardware are absent.
- The PPO baselines depend on the authors' own tuning plus a public checkpoint, which leaves their strength uncertain.
- The method presumes the preference data came from pi_SFT; when it did not, pi_ref is estimated by fitting the chosen completions with maximum likelihood.
- The handbook judges its DPO result from a single qualitative sample on one prompt, with no metric; its hyperparameters were chosen by comparing the outputs of over 20 trained models on a set of questions.


## See Also
- [[Bradley-Terry Preference Model]] — prerequisite-for (the pairwise loss DPO rewrites over the policy)
- [[RLHF Pipeline]] — prerequisite-for (the PPO pipeline DPO is compared against)
- [[Preference Optimization Algorithms]] — prerequisite-for (the family DPO sits in)
- [[Direct Preference Optimization]] — related (applied guidance on when DPO fits an agent project)
- [[SimPO and PRO Reference-Free Preference Optimization]] — extends (replace the reference-ratio reward)
- [[RLOO REINFORCE Leave-One-Out]] — alternative-to (an online method compared with DPO)
- [[Self-Rewarding Language Models]] — extends (iterative DPO on self-judged pairs)
- [[Tulu 3 Post-Training Recipe and RLVR]] — related (uses a length-normalised DPO stage)
