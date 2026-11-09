---
title: Chain of Hindsight
tags: [foundations, pattern]
summary: "Chain of Hindsight fine-tunes a language model on sequences that pair outputs with templated 'Bad' and 'Good' feedback using the ordinary next-token loss, so no RL stage is needed; on GPT-J 6B it beat PPO-based RLHF in pairwise human preference."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-liu-2023-chain-hindsight-aligns-language-models.md
---

# Chain of Hindsight

Liu, Sferrazza and Abbeel ask whether ordinary supervised fine-tuning, with no reinforcement learning, can let a model use every piece of human feedback, favourable and unfavourable alike. Human-ranked model outputs become one text sequence with templated feedback ("Bad: ... Good: ..."). A decoder-only model trains with the standard next-token objective, but the feedback tokens themselves are excluded from the loss. When the model is used, the prompt supplies the favourable tag ("Good"). The idea borrows hindsight from goal-conditioned RL.

## Results

Setup for the human comparisons: GPT-J 6B, pairwise evaluation by 75 labelers, win rate in percent; the tie share is the remainder. All numbers are self-reported.

- Summarization (TL;DR, filtered Stiennon validation set): CoH was preferred on average over RLHF (RLHF 30.8, tie 24.0), SFT (28.2), the base model (19.9), SFT with unlikelihood (21.4) and conditional SFT (29.6, the smallest margin).
- Dialogue (Anthropic HH validation): CoH was preferred over RLHF (RLHF 23.4, tie 39.8) and SFT (19.1, tie 41.5).
- Without the natural-language feedback, CoH still came out ahead of RLHF on summarization in human preference (RLHF won 32.1, ties 26.5); the full method beat the variant lacking language feedback head-to-head, though most comparisons ended in ties (10.6 against a 74.3 tie rate).
- Language Model Evaluation Harness, 22 tasks, GPT-J, 5 seeds: zero-shot average GPT-J 40.60 and SFT 40.54; few-shot average GPT-J 39.38 and SFT 39.59. The extraction records that CoH shows no alignment tax, but gives no CoH average beside these two.
- At small scale CoH sits a little under SFT, but with larger models it overtakes both SFT and RLHF (read from a figure). It performs about equal to Koala (SFT on ShareGPT), and combining CoH with Koala beats Koala alone.

## Limits

- CoH sequences are long, which raises training compute; the authors rely on costly hired labelers and judge automated metrics less reliable.
- Feedback is templated from ratings rather than open-ended language, and inference uses only the positive token.
- Key results for ROUGE, HH accuracy, scaling and the Koala comparison are given only in figures, and the human evaluation reports no variance, seeds or significance tests. Learning rate, steps, sequence length, decoding, hardware and compute are not stated.
- The extraction notes that the dialogue evaluation relies on synthetic dialogues assembled from existing human conversations. Preference data is offline only. The baselines are GPT-J (about 6B) trained with PPO-based RLHF, which looks dated next to DPO-style methods.

## See Also
- [[RLHF Pipeline]] — prerequisite-for
- [[Direct Preference Optimization]] — alternative-to
- [[Post-Training for Agents]] — related
