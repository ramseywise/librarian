---
title: "Score-Based Generative Modeling Through SDEs"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "Song et al. unify score-matching (SMLD) and DDPM models as discretisations of forward SDEs and their reverse-time SDE, giving predictor-corrector samplers, a probability flow ODE with exact likelihood, and controllable generation from one unconditional score model."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-song-2020-score-based-generative-modeling-through.md
---

# Score-Based Generative Modeling Through SDEs

The paper asks whether score-based models (SMLD) and diffusion models (DDPM) can be unified as discretisations of one continuous-time SDE (together with its reverse-time SDE), so that new samplers, exact likelihood and controllable generation follow. Results are the authors' own (self-reported).

## Mechanism

- A forward SDE diffuses data into a prior. A score network s(x,t) that depends on time is fitted with denoising score matching and plugged into the reverse-time SDE, whose drift is f(x,t) minus g(t)^2 times the score, with diffusion g(t) dw.
- **VE SDE** (variance exploding) is the continuous limit of the SMLD noise perturbation; **VP SDE** (variance preserving) is the continuous limit of DDPM; **sub-VP SDE** is a new one, with variance that never exceeds that of the VP SDE.
- **Predictor-Corrector sampler:** a numerical step of the reverse SDE acts as predictor, and score-based MCMC (Langevin) then acts as corrector.
- **Probability flow ODE:** a deterministic process whose marginals match the SDE's, with drift f minus half of g^2 times the score and no noise term. It gives exact likelihood and supports adaptive ODE solvers.
- Class-conditional generation, inpainting and colourisation come from a single unconditional score model.
- New architectures NCSN++ and DDPM++ (the DDPM U-Net with FIR resampling, rescaled skip connections, BigGAN-style blocks and extra blocks) set CIFAR-10 records.

## Findings

- NCSN++ (deep, VE, continuous) sets a new unconditional CIFAR-10 FID and Inception score with the PC sampler, and DDPM++ (deep, sub-VP, continuous) gives the best likelihood on uniformly dequantized CIFAR-10 via the probability flow ODE. The extraction gives no values for these.
- On the VE SDE with reverse-diffusion predictors, PC1000 (1000 predictor plus 1000 corrector steps) beats P2000 and P1000 on CIFAR-10 (mean of 5 runs); probability flow predictors do much worse on VE.
- With a larger error tolerance, an adaptive ODE solver reduced function evaluations by more than 90% with no visible loss of quality (DDPM, 256x256 CelebA-HQ).
- Sub-VP gives better likelihood than VP for DDPM++ continuous. The DDPM ELBO bound for the same DDPM model is at most 3.75 bits/dim (Lsimple).
- For VP models FID gets worse after 0.5M iterations, so the best FID seen in training is not the final checkpoint's.

## Limits

- Sampling is still slower than with GANs; the authors want stable training combined with fast sampling.
- Sampler hyperparameters (r, step count, number of corrector steps) need hand tuning, and no automatic selection is given.
- VE gives better samples but worse likelihood than VP and sub-VP, so each domain needs its own choice of SDE.
- Visible flaws, such as facial asymmetry, remain in 1024x1024 CelebA-HQ samples.
- Without a corrector, probability flow ODE samplers get a worse FID than SDE solvers, most clearly for VE.
- The paper omits compute, hardware, learning rate and parameter counts, and uses no training seeds.

## See Also

- [[Deep Unsupervised Learning Using Nonequilibrium Thermodynamics]] — prerequisite-for
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
- [[Consistency Models]] — extends
- [[SDEdit Guided Image Synthesis]] — related
- [[Diffusion and GAN Image Generation]] — prerequisite-for
