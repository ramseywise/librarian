---
title: "GLU Variants and GELU"
tags: [llm, architecture, concept]
summary: "Gated and smooth activations for the Transformer feed-forward layer: the GELU (x times the Gaussian CDF), the gated linear unit used in ConvS2S, and Shazeer's ReGLU, GEGLU and SwiGLU feed-forward variants tested in the T5 setup."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-hendrycks-2016-bridging-nonlinearities-stochastic-regularizers-gaussian.md
  - data/raw/papers/2026-11-07-shazeer-2020-glu-variants-improve-transformer.md
  - data/raw/papers/2026-11-08-gehring-2017-convolutional-sequence-sequence-learning.md
---

# GLU Variants and GELU

The Transformer feed-forward sublayer is two matrices with a ReLU between them ([[Transformer Architecture]]). Two lines of work change the non-linearity.

## GELU

Hendrycks and Gimpel define GELU(x) as x times Phi(x), where Phi is the standard Gaussian CDF (written with erf as x/2 times 1 plus erf(x over root 2)); it is the expected value of a random input-dependent mask drawn as Bernoulli(Phi(x)). It modifies adaptive dropout, using the Gaussian CDF. Two approximations are given, a tanh form (with the constant 0.044715) and x·sigma(1.702x). They also coin the SiLU, x·sigma(x), built on the logistic CDF, and say informally that it trails GELU yet usually beats ReLU and ELU (no numbers).

- Compared with ReLU and ELU (alpha=1) on MNIST, TIMIT, Twitter POS, CIFAR-10 and CIFAR-100; only the learning rate was tuned (three values), and medians are over 3-5 runs (self-reported).
- GELU had the lowest median error on CIFAR-10 (9-layer CNN, no augmentation, Adam 200 epochs, 3 runs), CIFAR-100 (WideResNet 40-4, 50 epochs, SGDR, 3 runs), Twitter POS (two-layer, 256 units) and TIMIT frame classification (5-layer 2048 net); the extraction gives no values for these gaps. The paper cites 22.89% for the original WRN 40-4 with ReLU on CIFAR-100.

## Gated linear unit

The GLU multiplies, element by element, two linear projections of the input, one of them squashed by a sigmoid first: v([A B]) = A ⊗ sigma(B). The Bilinear layer is a GLU without the activation. ConvS2S uses GLUs as the non-linearity of its convolution blocks (see [[Encoder-Decoder Translation Before the Transformer]]).

## GLU variants in the feed-forward layer

Shazeer replaces the ReLU FFN with GLU-style layers that use three matrices, such as FFN_SwiGLU(x, W, V, W_2) = (Swish_1(xW) ⊗ xV) W_2, plus ReGLU (ReLU gate) and GEGLU (GELU gate). To keep parameters and compute equal, d_ff is cut from 3072 to 2048.

Setup: T5-base (12 encoder and 12 decoder layers, d_model 768), pretrained on C4 span filling for 524,288 steps with dropout off, then one fine-tuning run on a GLUE, SuperGLUE and SQuAD mixture (dev sets, best checkpoint). Results are the author's own.

- GEGLU has the lowest held-out log-perplexity after 524,288 steps and SwiGLU is also below ReLU; the GELU FFN reaches 1.679, no better than ReLU. The standard deviation over four runs at 65,536 steps is 0.010.
- ReGLU is slightly above ReLU on SQuAD v1.1 F1 and on GLUE average; SwiGLU is above ReLU on SuperGLUE average.
- The author offers no explanation for why the gated variants work.

## Limits

- GELU: only 3-5 runs behind each median, no variance or significance tests, and gaps of 0.1 to 1 point; small models and datasets only, with no transformer or language-model runs; ReLU and ELU are the sole comparators and the learning rate the sole tuned setting. The SiLU claim has no numbers, and Appendix B is the authors' own account of priority disputes over SiLU and swish.
- GLU variants: each architecture was pretrained once for 524,288 steps (spread measured only at 65,536), fine-tuning was a single noisy run per model with checkpoints picked on dev sets, only T5-base scale was used, and some tasks (for example CoLA and CB) favour GELU or ReLU. The Raffel et al. baseline with the same architecture does notably worse, which the author puts down to pretraining dropout that he removed, so that comparison is confounded.
- ConvS2S: the GLU is its design choice; the extraction reports no ablation of the GLU itself.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Layer Normalization]] — related (the other sublayer change adopted in Transformers)
