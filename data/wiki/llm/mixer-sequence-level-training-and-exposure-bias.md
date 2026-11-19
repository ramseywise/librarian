---
title: MIXER Sequence-Level Training and Exposure Bias
tags: [llm, reinforcement-learning, pattern]
summary: "MIXER (Ranzato et al., 2016) pretrains a text-generation RNN with cross-entropy, then replaces cross-entropy steps by REINFORCE steps from the end of each sequence backwards, optimising BLEU or ROUGE directly to address exposure bias; plain REINFORCE from scratch never converged."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-ranzato-2015-sequence-level-training-recurrent-neural.md
---

# MIXER Sequence-Level Training and Exposure Bias

Ranzato, Chopra, Auli and Zaremba ask how to train text-generation RNNs to avoid exposure bias and to optimise the test-time metric (BLEU, ROUGE) directly, despite the huge action space. **Exposure bias** is the authors' name for the model seeing only the training distribution during training, never its own predictions.

## Mechanism

MIXER stands for Mixed Incremental Cross-Entropy Reinforce.

1. Pretrain the RNN with cross-entropy (XENT) for N_XENT epochs.
2. For each sequence, apply XENT to the first s steps and REINFORCE on the remaining T - s steps. The REINFORCE part samples words, uses a sequence-level BLEU or ROUGE-2 reward and a learned linear baseline.
3. After every N_XE+R epochs, lower s by delta, until every step uses REINFORCE.

The authors justify the XENT warm start by stating that an untrained language model has perplexity close to the vocabulary size (about 10,000), where a trained one has about 50.

## Results (self-reported)

Setup: greedy generation on the test set, a single model per method, hyper-parameters picked on validation data.

| Task | MIXER | XENT | Other |
|---|---|---|---|
| Gigaword summarisation, ROUGE-2 | 16.22 | 13.01 | not stated |
| IWSLT14 De-En, BLEU-4 | 20.73 | 17.74 | DAD 20.12 |
| MSCOCO captioning, BLEU-4 | 29.16 | 27.8 | not stated |

- Gains over XENT are 1 to 3 points across the three tasks.
- Greedy MIXER is stated to be at least 10 times quicker than XENT at beam size 10, and baselines using beam search match it in only one of the three tasks (the speed claim was not timed).
- The reward metric matters: on Gigaword, BLEU is 8.16 for XENT, 5.80 for MIXER trained on ROUGE and 9.32 for MIXER trained on BLEU; ROUGE-2 of MIXER trained on BLEU is 15.1 against 16.22 when trained on ROUGE.
- a REINFORCE run that began from a random policy did not converge, and the XENT-plus-REINFORCE loss without the incremental schedule failed to take off.
- The End-to-End backprop baseline did little: 17.77 on translation against XENT's 17.74, and 26.42 on captioning, under XENT's 27.8.

## Limits

- The models are small (128 to 512 hidden units), the datasets small and the networks 2015-era RNNs, not Transformers.
- Each method has one run, with no seeds or significance tests; learning rates and many other hyper-parameters are missing.
- The beam-search comparison appears only as a plot, and the speed claim was not timed.
- The authors admit the reward baseline is estimated poorly, which can slow convergence, and training uses one sample.
- The reward is BLEU or ROUGE on a single reference. The extraction adds that later work showed this correlates imperfectly with quality; that point is not in the paper.

## See Also
- [[Scheduled Sampling]] — alternative-to (the DAD baseline family; narrows the same train-test mismatch without a sequence reward)
- [[REINFORCE with a Baseline]] — prerequisite-for
- [[Neural Abstractive Summarisation 2015-2017]] — related (the Gigaword setup and the self-critical mixed objective that cites MIXER)
- [[Deep RL Dialogue Generation Rewards]] — related (reuses the maximum-likelihood-to-REINFORCE curriculum)
