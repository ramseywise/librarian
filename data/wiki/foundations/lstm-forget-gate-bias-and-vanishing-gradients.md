---
title: "LSTM Forget-Gate Bias and Vanishing Gradients"
tags: [foundations, pattern]
summary: "Default-initialised LSTMs pass a gradient of about 10^-12 from the first step, no better than a plain RNN; setting the forget-gate bias to 1 or 2 (mind PyTorch's two bias vectors) restores long memory, and gradient clipping handles the opposite failure."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05-sequence-models.md
---

# LSTM Forget-Gate Bias and Vanishing Gradients

## Cells

A recurrent cell reuses the same weights each step; training unrolls it and backpropagates through time. The LSTM adds a cell state updated by addition and gates that erase and write; it has four times the RNN's parameters (18,688 vs 4,672 at hidden size 64, input 8). The GRU merges forget and update gates and has three sets. Digits read as 8 rows of 8 pixels (test): RNN 0.957 (5,386 parameters), GRU 0.966, LSTM 0.962, all behind a CNN's 0.983; eight steps is too short for the cells to differ. See [[Convolution, Shift Sensitivity and Parameter Sharing]].

## The failure

Backpropagating over T steps multiplies T factors; below one, the signal vanishes. Test: the label is the sign of the first number, the rest is noise, so one bit must survive the sequence. PyTorch leaves LSTM biases at ordinary initialisation, so the forget gate starts near 0.5 and halves memory each step. Gradient from the first step: RNN and LSTM both about 10^{-12} at default bias; bias 1 about 10^{-5}; bias 2 about 0.02, as large as the last step's.

Accuracy on the first-sign task, 3 seeds: T=20, default bias 0.53 for RNN and LSTM, bias 1 and 2 both 1.0. T=50: bias 2 reached [0.502, 0.892, 1.0], so longer needs more than the bias. A GRU with defaults at T=20 also sat at about 0.53. So the LSTM advantage is not automatic.

## The two-bias trap

`nn.LSTM` has two bias vectors (bias_ih, bias_hh) and each gate adds both. The widely copied snippet that writes 1 to the forget chunk of every parameter with "bias" in its name sets a total of 2; and a check against a misspelled parameter name silently does nothing. Measure the gradient rather than trust the assignment.

## Exploding gradients

Rescale the whole gradient when its global norm exceeds a threshold (`clip_grad_norm_` between backward and step). On a character model of 195 names the largest norm was 0.83, under the threshold of 1.0, so clipping was insurance.

## Sampling

Training feeds the true previous character (teacher forcing); sampling feeds back its own output, so a model never sees its own mistakes in training. Low temperature concentrates on the likeliest next token; t=3.0 flattens the distribution until structure breaks.

## See Also
- [[Seq2seq Bottleneck and Attention]] — extends
- [[Sequence Models vs Hand-Built Event Windows]] — related
- [[Weight Initialisation and Activation Scale]] — related
