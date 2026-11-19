---
title: "Layer Normalization"
tags: [llm, architecture, concept]
summary: "Layer normalization (Ba, Kiros, Hinton 2016) normalizes each training case over the hidden units of a layer instead of over the mini-batch, so it works for recurrent networks and small batches and behaves the same at train and test time."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-ba-2016-layer-normalization.md
  - data/raw/papers/2026-11-07-vaswani-2017-attention-all-you-need.md
---

# Layer Normalization

Layer normalization computes the mean and standard deviation over all H hidden units of a layer on a single training case, then applies a learned per-neuron gain and bias before the non-linearity: the layer's inputs minus their mean mu, divided by their standard deviation sigma, times the gain alpha, plus the bias beta (mu is the average of the H summed inputs and sigma the root of their mean squared deviation). Within a layer every hidden unit uses the same mu and sigma, while each training case gets its own. Where [[Batch Normalization]] depends on mini-batch statistics, this works per case, and the calculation is the same in training and at test time. The authors' hypothesis is that fixing these statistics reduces covariate shift and stabilises recurrent hidden-state dynamics.

In an LSTM the gates are computed as LN(W_h h_{t-1}) + LN(W_x x_t) + b, and the hidden output as h_t is sigma(o_t) times tanh of the normalised cell state; every LN has separate gain and bias.

## Results

All are the paper's, single runs on mostly recurrent models (self-reported):

- Order-embedding with a GRU on MSCOCO image retrieval: LN reaches its best validation model after 60% of the baseline's training time. It improves caption and image retrieval R@1 over the baseline (mean over 5 test splits).
- Attentive reader (CNN corpus, validation only): training is faster and the final validation result better than for the plain LSTM and the batch-norm variants. LN with scale initialisation 1.0 beat 0.1, whereas recurrent batch norm needs 0.1.
- Skip-thoughts (BookCorpus, 2400-d encoder) with LN outscore the self-trained baseline on SICK(r) and MR at 1M iterations; a further month of training (about 1.7M iterations) gave more gains on all but one task.
- DRAW (binarised MNIST; 64 glimpses, 256 LSTM units; Adam with batch 128): LN converges in about half the time and, after 200 epochs, reaches a slightly better test bound.
- Handwriting generation (IAM-OnDB, 3x400 LSTM): comparable log likelihood to the baseline, converging much faster.
- Permutation-invariant MNIST (784-1000-1000-10, Adam, batch size 128 and 4): LN is insensitive to batch size and converges sooner than batch norm.

## Invariance analysis

By the paper's analysis (Table 1), LN does not change under rescaling or shifting of the full weight matrix, or rescaling of a single training case, but does change if one weight vector alone is rescaled. In a generalized-linear-model analysis, doubling a weight vector's norm halves the curvature along it, which the authors describe as an implicit early-stopping effect.

## Use in the Transformer

Vaswani et al. apply layer norm after each residual sub-layer of the [[Transformer Architecture]]; the original arrangement and the later pre-norm variant are compared in [[Pre-Norm vs Post-Norm and Warm-Up]].

## Limits

- Convolutional networks: only preliminary experiments, and batch norm did better; the authors say further research is needed. No numbers, task or architecture are given for them.
- The skip-thought setup departs from the original because the public code does not condition at every decoder timestep. The attentive-reader results cover validation only, with batch-norm curves borrowed from Cooijmans et al.
- Single runs; seeds, learning rates and significance tests are absent, and many hyperparameters are left to the original papers. The comparison with Wang et al. on MSCOCO is not direct (one test set against a mean of five).
- It has no transformer or attention experiments, since the paper predates the Transformer.

## See Also
- [[Batch Normalization]] — alternative-to
- [[Transformer Architecture]] — extends
- [[Pre-Norm vs Post-Norm and Warm-Up]] — extends
