---
title: "Deep Unsupervised Learning Using Nonequilibrium Thermodynamics"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "The 2015 paper that introduced diffusion probabilistic models: a fixed forward Markov chain turns data into Gaussian noise, and a learned reverse chain, trained on a variational lower bound, generates samples and supports inpainting."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-sohldickstein-2015-deep-unsupervised-learning-using-nonequilibrium.md
---

# Deep Unsupervised Learning Using Nonequilibrium Thermodynamics

Sohl-Dickstein and colleagues ask whether a generative model can have both flexibility and tractability, by learning to reverse a slow forward diffusion that gradually erases the structure in data. Their hypothesis: learning small perturbations of a diffusion process is easier than capturing the whole distribution in a single non-normalizable potential. Results are the authors' own (self-reported).

## Method

- A **diffusion probabilistic model** is where a Markov chain ends up when it runs a gradual forward diffusion (data turned into a simple known distribution) in reverse.
- The forward chain is fixed: each step is a Gaussian centred on the previous state scaled by sqrt(1-beta_t), with covariance beta_t times identity. It ends at an identity-covariance Gaussian (an independent binomial for binary data).
- Each reverse step has a learned mean and covariance (or bit-flip probability) produced by MLPs or multi-scale convolutional networks. Training maximises K, a variational lower bound on the log likelihood.
- To sample, the reverse chain is run starting from noise. For inpainting or denoising, a function r(x) is multiplied into each reverse step, which is how posterior sampling works.
- Claimed properties: very flexible, exact sampling, easy to multiply with other distributions, cheap log-likelihood evaluation, and workable with thousands of layers or time steps.

## Experiments

| Result | Setup |
|---|---|
| Higher log likelihood than the previous best (MCGSM) | Dead leaves, split as in Theis et al. 2012 |
| Parzen-window estimate of 317 bits, a value between the Deep GSN's and the adversarial net's | MNIST; Parzen code of Goodfellow et al. 2014 applied to model samples, not the bound K |
| Gain of 11.5 +- 0.2 bits/pixel over an isotropic Gaussian (lower bound K) | CIFAR-10 holdout, uniform dequantization noise, data rescaled to unit variance |
| K of -2.414 bits/sequence versus the true value -2.322 | Binary heartbeat sequences of length 20; binomial diffusion with 2000 steps |

Table 1 also lists swiss roll at 2.35 bits, bark at -0.55 bits/pixel and dead leaves at 1.489 bits/pixel. Image experiments use T = 1000 reverse steps (500 for bark), 40 for the swiss roll and 2000 for binary data. A bark texture model inpainted a 100x100 central region replaced with noise, recovering long-range structure. The authors say the higher CIFAR-10 bounds of the earlier version were an artefact of learning the 8-bit quantization.

## Relation to later work

[[Score-Based Generative Modeling Through SDEs]] cites it as the original diffusion model and recasts DDPM-style models, via [[Denoising Diffusion Probabilistic Models]], as discretisations of a continuous-time SDE. The paper compares its MNIST score with [[Generative Adversarial Nets Minimax Game]] and notes a variational bound similar to [[Auto-Encoding Variational Bayes]].

## Limits

- Evaluation has no sample-quality metric, only log-likelihood bounds plus qualitative samples.
- For MNIST the comparison rests on Parzen-window estimates, which the authors say are not the same thing as their own consistent lower bound.
- The paper omits learning rate, batch size, step count, layer widths, compute and seeds, and refers readers to its released code.
- One footnote reports that, in recent experiments, a fixed beta schedule did about as well as a learned one.

## See Also

- [[Denoising Diffusion Probabilistic Models]] — related
- [[Score-Based Generative Modeling Through SDEs]] — extends
- [[Auto-Encoding Variational Bayes]] — related
- [[Generative Adversarial Nets Minimax Game]] — related
- [[Diffusion and GAN Image Generation]] — prerequisite-for
