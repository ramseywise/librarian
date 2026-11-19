---
title: SimPO and PRO Reference-Free Preference Optimization
tags: [llm, preference-and-alignment, comparison]
summary: "Two alternatives to DPO: SimPO scores a response by its length-normalised average log-likelihood with a target margin, PRO contrasts the best response against all lower-ranked ones over a ranking of any length, each with its own evaluation setup and limits."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-meng-2024-simpo.md
  - data/raw/papers/2026-11-08-song-2024-preference-ranking-optimization-human-alignment.md
---

# SimPO and PRO Reference-Free Preference Optimization

SimPO trains offline on preference data and needs no reference model; the PRO extraction does not say either, and uses DPO only as a baseline. Relative to [[DPO Loss and Implicit Reward]], SimPO changes the reward, while PRO changes the contrast from a pair to a ranking.

## SimPO

SimPO (Meng, Xia and Chen, NeurIPS 2024) drops DPO's log-ratio reward. Its reward is the mean per-token log-probability of the response, scaled by beta, and a required reward gap gamma (greater than 0) separates chosen from rejected inside the Bradley-Terry sigmoid:

```
loss = -log sigmoid( (beta/len_w) * logp_w  -  (beta/len_l) * logp_l  -  gamma )
```

The authors' stated motivation is that DPO's reward does not match the mean log-likelihood that guides generation, which they suspect hurts quality. Preference pairs come from UltraFeedback ([[UltraFeedback Scaled AI Feedback Dataset]]) under two configurations: Base (a Zephyr-style SFT model trained on UltraChat-200k) and Instruct (completions regenerated on-policy and scored with PairRM). Tests use AlpacaEval 2, Arena-Hard and MT-Bench. Every figure below is (self-reported).

- Over four configurations (Mistral and Llama-3 at 7B/8B, each Base and Instruct), SimPO leads the strongest baseline on AlpacaEval 2 LC win rate by a margin between 3.6 and 4.8 points. Eight baselines (DPO, R-DPO, IPO, KTO, CPO, ORPO, RRHF, SLiC-HF) were each searched over a modest hyperparameter grid.
- Arena-Hard: the widest lead over DPO is 7.5 points (Llama-3-Base). On Mistral-Instruct, CPO scores higher than SimPO there, though its outputs run roughly 50% longer.
- Ablation on Mistral-Base: without length normalisation, AlpacaEval 2 LC falls from 21.5 to 11.9, under DPO; with gamma set to zero it is 16.8.
- On a held-out set with Mistral-Base, the Spearman correlation between mean log-likelihood and length is 0.34 for SimPO, 0.59 for DPO, and 0.82 for SimPO minus normalisation.
- In Mistral-Base on the UltraFeedback training data, close to half of DPO's training triples are ranked by its reward differently than by mean log-likelihood.
- Llama-3-Base on 8xH100: DPO took 73 min and 77 GB, SimPO 60 min and 69 GB, i.e. roughly 20% less time and 10% less memory as the paper tells it.
- Adding length normalisation to DPO gives Mistral-Base a lift (LC 15.1 up to 21.0) while Mistral-Instruct drops (26.8 down to 21.7).
- With the ArmoRM labeller instead of PairRM, Llama-3-Instruct SimPO reaches LC 53.7, and DPO matches SimPO on raw win rate (both 47.5), so the gap between algorithms narrows. Putting an SFT loss on top of SimPO reduces LC from 53.7 to 41.4.
- The released Gemma-2-9B-it model, trained on ArmoRM-labelled UltraFeedback at learning rate 8e-7, scores LC 72.4 on AlpacaEval 2 and 59.1 on Arena-Hard.
- GSM8K falls after preference optimisation: Llama-3-Instruct (v0.1 data) goes from 68.69 under SFT to 50.72 under SimPO. Raising the learning rate improves chat scores but increases forgetting (at 1e-6: LC 53.7, GSM8K 57.4).
- The authors observe that MT-Bench discriminates poorly between the methods.

## PRO

Preference Ranking Optimization (Song et al., AAAI-24) frames alignment as supervised fine-tuning on a human-ranked list of n responses. At each rank k, response k must outscore every response ranked below it; the score is the length-normalised log-likelihood. The top response also gets an NLL term weighted by beta:

```
ranking term = -sum over k of log( exp(s_k) / sum_{i>=k} exp(s_i) ),   total = ranking term + beta * NLL(top response)
```

This turns the Bradley-Terry pairwise comparison into a one-versus-many one. An optional dynamic temperature, computed from reward-model score gaps, makes the penalty on negatives uneven. A ranking can be enlarged with outputs of other LLMs (Alpaca, ChatGPT, Curie) and re-ordered by a reward model. All runs use LLaMA-7B on HH-RLHF, and results are (self-reported):

- Raw HH-RLHF pairs: PRO's Reward exceeds SFT's by 6.52 and DPO's by 2.6, yet its Total BLEU of 21.54 trails SFT (21.80) and DPO (22.62).
- With ChatGPT added to make rankings of length 3, PRO's Total Reward is 67.97; ChatGPT answering zero-shot gets 68.48, DPO 64.10, best-of-N 63.83.
- With Alpaca added instead (length 3), DPO edges ahead: 59.27 against PRO's 58.72, with best-of-N at 57.66 and RLHF at 57.28.
- GPT-4 as judge favours raw-data PRO over the dataset's golden answer (55.00 win, 40.63 lose). Human raters mostly call it a tie: 56.25 ties, 22.50 wins and 21.25 losses.
- Raw-data ablation: with neither the SFT term nor the temperature, Total BLEU is 5.14 and Reward 46.17, compared with 21.54 and 55.35 for the full method; with only the SFT term removed, BLEU is 9.85 and Reward 53.25.
- Longer rankings tend to help, as do stronger or more varied added responses (Curie plus Alpaca at length 4 beats Alpaca plus Alpaca).

## Limits

- SimPO: the paper admits it lacks a rigorous theoretical explanation, and gamma adds a hyperparameter that must be tuned by hand. Beta and gamma vary by setting (beta between 2.0 and 2.5 in most, but beta 10 with gamma 3 for Llama-3-Instruct v0.2).
- SimPO: UltraFeedback centres on helpfulness; safety and honesty get no evaluation besides TruthfulQA. Preference optimisation hurts GSM8K and at times MMLU, more so with large learning rates. With no KL term, reward hacking is possible in principle, though none was seen when tuning was careful.
- SimPO: PPO is not compared, training is offline and single-round, and the benchmarks depend on GPT-4 judges over a narrow query set. MT-Bench gaps might be noise. Gains shrink with a better SFT model and cleaner labels. Seeds, run counts and token counts go unreported.
- PRO: scoring is mainly reward-model Reward plus BLEU, using open-source reward models the paper does not name. The GPT-4 and human checks pit PRO only against the golden response (never DPO), on small samples with three raters and no agreement or significance figures.
- PRO: one model size (LLaMA-7B) and one dataset (HH-RLHF); no seeds or variance; learning-rate schedule and compute are not given.
- PRO: gains from longer rankings are tangled up with reward-model signal and distillation from a stronger teacher (ChatGPT). Its link to Plackett-Luce, and the idea that it nears perfect alignment as n grows without bound, are assumptions that were not tested. The temperature needs reward-model scores, and its effect is isolated from the SFT term only through Table 3.

## See Also
- [[DPO Loss and Implicit Reward]] — prerequisite-for (the reference-ratio objective both methods replace)
- [[Preference Optimization Algorithms]] — prerequisite-for (the family these two join)
- [[Bradley-Terry Preference Model]] — prerequisite-for (the pairwise objective SimPO keeps and PRO extends)
- [[UltraFeedback Scaled AI Feedback Dataset]] — prerequisite-for (SimPO's training data)
- [[Tulu 3 Post-Training Recipe and RLVR]] — related (its ablation compared SimPO with length-normalised DPO)
