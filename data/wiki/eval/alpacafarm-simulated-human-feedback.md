---
title: AlpacaFarm Simulated Human Feedback
tags: [eval, concept]
summary: "AlpacaFarm replaces crowdworker pairwise labels with a pool of prompted LLM annotators and scores systems by win-rate against Davinci003 on 805 instructions; across 11 systems the paper reports that method rankings match those from 10k real human preference pairs (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-dubois-2023-alpacafarm.md
---

# AlpacaFarm Simulated Human Feedback

Dubois, Li, Taori et al. (preprint, 2023) ask whether pairwise feedback simulated by LLMs, together with automatic win-rate evaluation and reference implementations, can let researchers build learning-from-feedback methods cheaply, with conclusions that carry over to real human feedback. Their hypothesis is that simulation ranks methods the same way human feedback does.

## Setup

- **Simulated annotators:** a pool of 13 differently prompted OpenAI-model annotators stands in for crowdworker pairwise labels; training labels get a further 25% label flips to reproduce human noise.
- **Evaluation:** win-rate against Davinci003 on 805 instructions.
- **Methods:** reference implementations of six **learning from pairwise feedback (LPF)** methods on a LLaMA 7B supervised model: PPO, best-of-n, expert iteration, Quark, binary FeedME and reward conditioning, with DPO also covered.
- **Validation:** the same methods trained on 10k human-labelled pairs and the rankings compared.

## Results

All numbers are the paper's own (self-reported).

- Rankings of 11 systems (six LPF methods, with GPT-4, ChatGPT, Davinci001, LLaMA 7B and Alpaca 7B) come out in the same order under simulation and human feedback. Five of the 11 are untrained API or base models; excluding them, the rank correlation is lower.
- The simulated pool agrees with the majority of three human labels about as often as a held-out human does, at a cost the paper puts at 25x lower than humans (humans at about 300 USD per model evaluation, MTurk median 21 USD per hour).
- One GPT-4 prompt agrees more with humans but varies far less than they do, so over-optimization never shows up with it and it is left out of the pool. A PPO model trained on one GPT-4 annotator transfers to human judgments better than one trained on the pool.
- PPO is the best LPF method under human feedback and improves over the 10k supervised baseline.
- Win rates on the composite eval set follow those on real Alpaca Demo instructions (11 systems, 200 demo instructions).
- Over-optimization appears at 25% label noise, the smallest ratio tested (0%, 17.5%, 25% and 35%). Humans and simulated annotators alike favour longer outputs, and mean output length rises after PPO (277.5 for the supervised baseline).

## Limits

- Instructions are simple and single-turn; every fine-tuned model starts from LLaMA 7B.
- Human validation is a small crowd (the text says 13 crowdworkers; 16 were selected and one outlier removed).
- The setup presumes an oracle LLM far stronger than the models studied, and settings such as the KL coefficient differ between simulated and human runs.
- Simulated annotators lean towards the first output shown and towards their own model family's outputs; rank mismatches remain (SFT10k against SFT52k, ChatGPT against PPO). Judges are 2023 OpenAI models, and a shortened ChatGPT prompt lets PPO beat it, showing length bias.

## See Also
- [[LLM-as-Judge Evaluation]] — prerequisite-for
- [[LLM Judge Biases]] — related (length and position preferences)
- [[Direct Preference Optimization]] — related (one of the implemented methods)
