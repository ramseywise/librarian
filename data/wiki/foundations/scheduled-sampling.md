---
title: Scheduled Sampling
tags: [foundations, pattern]
summary: A training schedule for recurrent sequence generators that mixes the true previous token and the model's own sampled token as decoder input, with the true-token probability decaying over training, to narrow the gap between training and decoding.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-a-2015-scheduled-sampling-sequence-prediction-recurrent.md
---

# Scheduled Sampling

A recurrent sequence generator is trained with the true previous token as input at each step, but at decoding time it receives its own previous output. The paper behind this page asks how to shrink that train-versus-inference mismatch and proposes a curriculum: make the model gradually used to its own mistakes during training.

## Mechanism

During mini-batch SGD on an RNN or LSTM, a coin is flipped for every token. With probability eps_i the input is the true previous token; otherwise it is a token drawn from the model (or its argmax). The probability eps_i decays as training proceeds, on a linear, exponential or inverse-sigmoid schedule, so early training looks like ordinary teacher forcing and late training looks more like decoding. The inverse-sigmoid form is eps_i = k/(k+exp(i/k)) with k >= 1. No gradient flows back through the choice of token.

Two named ablations: **Always Sampling** feeds only the model's own predictions; **Uniform Scheduled Sampling** replaces the model's sample with a uniformly random token.

## Results (all self-reported)

- **Captioning** (MSCOCO dev 5k; an LSTM with 512 units; inverse-sigmoid decay): scheduled sampling raised BLEU-4 and CIDER over the baseline (self-reported). Always Sampling collapsed quality. Uniform scheduled sampling beat the baseline by less than model sampling, which the authors read as evidence that the gain is not only regularisation. An ensemble of 5 scheduled-sampling models beat an ensemble of 10 baselines on BLEU-4 (self-reported). Dropout hurt captioning metrics. An entry using the method ranked first in the 2015 MSCOCO challenge (self-reported).
- **Parsing** (WSJ section 22 dev; 40k training instances; 512-unit LSTM plus attention): F1 improved and the gain was additive with dropout (self-reported); Always Sampling often produced invalid trees.
- **Speech** (TIMIT test; two LSTM layers of 250; beam of 10; eps falling linearly from 0.25 to 0): the best configuration lowered decoding frame error rate. The baseline had the best next-step error but the worst decoding error, which exhibits the gap. Always Sampling worked well here, which the authors suggest is due to redundant HMM-state targets (self-reported).

## Limits

- Because no gradient reaches the sampling choice, training is inexact; the authors suggest this could explain speech validation accuracy falling after roughly 9 epochs, and defer it.
- The paper omits learning rate, batch size, schedule constants, dropout rate and the captioning and parsing beam sizes. Captioning and parsing each have one run per configuration and no significance tests.
- Speech numbers are per frame on HMM-state targets and cannot be set against hybrid HMM systems.
- For parsing, the authors are unsure if the gain reflects reduced mismatch or reduced overfitting.
- The extraction records that later work found the objective inconsistent; that point is outside the source.

## See Also
- [[Seq2seq Bottleneck and Attention]] — related (the decoder setting scheduled sampling trains)
- [[Sampling Parameters]] — related (decoding-time sampling, not training-time)
- [[Hierarchical Story Generation]] — related (decoding with top-k sampling)
