---
title: "Auto-Encoding Variational Bayes"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "Kingma and Welling's SGVB estimator reparameterises the variational lower bound so a recognition model (encoder) and a generative model (decoder) train jointly by stochastic gradient descent; the VAE is AEVB with a neural-network encoder."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-kingma-2013-auto-encoding-variational-bayes.md
---

# Auto-Encoding Variational Bayes

The paper asks how to do efficient approximate inference and learning in directed models with continuous latent variables whose posteriors are intractable, on large datasets. Results are the authors' own (self-reported).

## Mechanism

- **SGVB** is an estimator of the variational lower bound that is reparameterised, differentiable and unbiased, so ordinary stochastic gradient methods can optimise it.
- **AEVB** applies SGVB to i.i.d. data with one continuous latent per datapoint, fitting a **recognition model** q(z|x) (a probabilistic encoder) to the intractable posterior. The **probabilistic decoder** p(x|z) gives a distribution over x for a code z. A **variational auto-encoder** is the case of AEVB where the recognition model is a neural network.
- Samples are drawn as z = mu + sigma * eps with eps ~ N(0,I), which is the reparameterisation. With a diagonal Gaussian posterior and N(0,I) prior the KL term is analytic, so the estimator is the analytic KL term (half, summed over latent dimensions j, of one plus log sigma_j^2 minus mu_j^2 minus sigma_j^2) plus the average over L samples of log p(x|z).

## Experimental setup

Encoder and decoder are one-hidden-layer MLPs; the encoder gives a diagonal Gaussian, the decoder a Bernoulli or Gaussian. Both are trained jointly with Adagrad, minibatch M = 100, one sample per datapoint (L = 1), on MNIST (latent size 3 to 200) and Frey Face (2 to 20). Baselines are wake-sleep and Monte Carlo EM.

## Findings

- Against wake-sleep, AEVB converged far faster and ended at a better lower bound, whatever the latent dimensionality.
- Adding latent variables did not increase overfitting; the authors credit the bound's regularising effect.
- One sample per datapoint sufficed when the minibatch was large enough (M = 100).
- On estimated marginal likelihood (MNIST, 1,000 and 50,000 training points, 3 latent variables, 100 hidden units), AEVB converged faster than wake-sleep and Monte Carlo EM; Monte Carlo EM could not be applied efficiently to full MNIST.

## Place in this wiki

The bound itself is explained on [[Variational Inference and the ELBO]]. [[Generative Adversarial Nets Minimax Game]] cites this paper as the other back-propagated generative machine, and [[Deep Unsupervised Learning Using Nonequilibrium Thermodynamics]] reports a similar variational bound with a frozen-noise trick. Autoencoders also serve as the first stage of [[Latent Diffusion Models]] and, as a VQ-VAE, of [[Jukebox Multi-Scale VQ-VAE Music]].

## Limits

- The text has no numeric results; every comparison is a curve in Figures 2 and 3.
- Only MNIST and Frey Face with shallow MLPs; hierarchical or convolutional models, time series and full variational Bayes on parameters are left to future work.
- The marginal-likelihood estimator is reliable only for latent spaces under 5 dimensions, so that comparison stops at 3.
- The diagonal Gaussian posterior is a stated choice rather than a limit of the method; only continuous latents are covered.
- Hidden-unit counts come from the earlier autoencoder literature; no seeds or repeated runs; dataset sizes, step counts and weight decay are not stated.

## See Also

- [[Variational Inference and the ELBO]] — prerequisite-for
- [[Generative Adversarial Nets Minimax Game]] — alternative-to
- [[Deep Unsupervised Learning Using Nonequilibrium Thermodynamics]] — related
- [[Latent Diffusion Models]] — related
- [[Diffusion and GAN Image Generation]] — prerequisite-for
