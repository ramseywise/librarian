---
title: "Denoising Diffusion Probabilistic Models"
tags: [multimodal, concept]
summary: "A diffusion model learns to undo gradual noising of an image; DDPM trains a U-Net to predict the added noise, and three follow-ups (score-based NCSN, Improved DDPM, DDIM) change the objective, the variances or the sampler."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ho-2020-denoising-diffusion-probabilistic-models.md
  - data/raw/papers/2026-11-07-nichol-2021-improved-denoising-diffusion-probabilistic-models.md
  - data/raw/papers/2026-11-07-song-2019-generative-modeling-estimating-gradients-data.md
  - data/raw/papers/2026-11-07-song-2020-denoising-diffusion-implicit-models.md
---

# Denoising Diffusion Probabilistic Models

A diffusion model is a Markov chain trained with variational inference so that running it for a fixed number of steps yields samples that match the data. This page covers the base recipe (DDPM) and three papers that the later image systems in [[Diffusion and GAN Image Generation]] build on.

## DDPM

A U-Net is given a noised image and a timestep t (T=1000, linear beta schedule) and is trained with a mean-squared error to predict the noise that was added (the simplified objective Lsimple). Sampling starts from pure noise and iterates the learned reverse Gaussian chain. The paper links noise prediction to denoising score matching at several noise levels, and links sampling to annealed Langevin dynamics.

- Unconditional CIFAR10 (32x32, 50,000 samples, FID against the training set): FID 3.17 and Inception score 9.46 (self-reported); against the test set the FID is 5.24 (self-reported).
- Table 2 ablation on CIFAR10: predicting the noise with Lsimple gives FID 3.17, against 13.22 for predicting the posterior mean with the true bound (self-reported). Learned diagonal variances with mean prediction gave FID 23.69 (self-reported).
- A model trained on the true bound has a slightly better test codelength (at most 3.70 bits/dim, against 3.75 for Lsimple) but worse samples (FID 13.51 against 3.17) (self-reported).
- LSUN 256x256, 50,000 samples: Bedroom FID 6.36 for the small model and 4.90 for the 256M-parameter model, Church 7.89, Cat 19.75 (self-reported).
- CIFAR10 model: 35.7M parameters, trained 800k steps over 10.6 hours on a TPU v3-8. Sampling takes 17 seconds for 256 CIFAR10 images, and 300 seconds for 128 images at 256x256 (self-reported).

## NCSN (score-based generation)

Noise Conditional Score Networks estimate the gradient of the log density of data perturbed at 10 geometrically spaced noise levels, using one network that takes the image and the noise level, trained with weighted denoising score matching. Images come from annealed Langevin dynamics, run at decreasing noise levels with step size proportional to the squared noise level. On unconditional CIFAR-10 (50,000 samples, checkpoint chosen by FID on 1000 images) it reports Inception score 8.87 and FID 25.32 (self-reported). In the same table SNGAN has FID 21.7 and class-conditional BigGAN FID 14.73 (reported). A single-noise-level baseline with plain Langevin sampling failed to give reasonable images (qualitative, no FID).

## Improved DDPM

Learns the reverse-process variances as an interpolation between two fixed values, trains with Lsimple plus 0.001 times the variational bound, uses a cosine noise schedule and T=4000, and samples with an evenly strided subset of steps.

- Unconditional ImageNet 64x64, 200K iterations, FID from 10K samples: the Ho et al. setup gives FID 32.5; cosine schedule with the hybrid loss gives NLL 3.62 and FID 28.0 (self-reported). At 1.5M iterations the hybrid loss reaches FID 19.2 (self-reported).
- Learned variances allow good samples from as few as 50 forward passes, and 100 steps are close to optimal FID for fully trained hybrid models (ImageNet 64x64 and CIFAR-10) (self-reported).
- ImageNet 64x64, class-conditional, 50K samples and 250 steps: the 270M model scores FID 2.92 with precision 0.82; the small model scores FID 6.92 with recall 0.72. For comparison, BigGAN-deep without truncation scores FID 4.06, precision 0.86, recall 0.59 (self-reported).
- Two-stage ImageNet 256x256 (class-conditional) gives FID 12.3, where a single stage gives 31.5 and BigGAN-deep 7.0 (self-reported).
- Across four ImageNet 64x64 models (30M to 270M parameters), FID tracks training compute with a power-law fit, 4.00 plus a decaying term in compute with exponent -0.22 (self-reported).

## DDIM

Defines non-Markovian inference processes that keep the DDPM training objective, so existing DDPM checkpoints work unchanged. With the noise term eta set to zero, sampling is deterministic, and it can step through a strided subset of the 1000 timesteps.

- CIFAR10 with eta=0: 50 steps nearly match 1000 steps, and 10 steps give FID 13.36 (self-reported).
- At 50 steps on CIFAR10, DDPM with the larger variance of the Ho et al. implementation scores 32.72 and DDPM with eta=1 scores 8.01 (self-reported).
- LSUN Bedroom 256x256 with 10 steps: DDIM 16.95 against DDPM (eta=1) 42.78; at 100 steps 6.62 against 6.81 (self-reported).
- The paper reports 10x to 50x faster sampling at comparable quality, and encode-decode reconstruction error on CIFAR-10 of 0.0001 at 500 and 1000 steps (self-reported).
- The Improved DDPM extraction reports that DDIM beats the learned-variance sampler below 50 steps and loses to it at 50 or more (ImageNet 64x64 and CIFAR-10).

## Limits

- DDPM: log likelihoods trail other likelihood-based models; on LSUN Cat and Church it trails StyleGAN and StyleGAN2; sampling takes T=1000 sequential evaluations; unconditional generation only, one run, hyperparameters tuned on CIFAR10.
- NCSN: only 32x32 images and only CIFAR-10 is evaluated quantitatively; FID is worse than SNGAN and BigGAN; the Metropolis-Hastings correction is ignored; no seeds or wall-clock.
- Improved DDPM: scaling results are preliminary, and NLL does not follow a clean power law; models overfit CIFAR-10 and class-conditional ImageNet 64x64; unconditional FID from 10K samples is biased upward by about 2 points compared with 50K; BigGAN-deep stays ahead at 256x256; single runs.
- DDIM: evaluated only on small unconditional image datasets, with no text conditioning or guidance; seeds, FID sample counts and intervals are not reported.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Classifier Guidance and the ADM Architecture]] — extends
- [[Cascaded Diffusion Models]] — extends
- [[SR3 and Palette Image-to-Image Diffusion]] — extends
- [[Video Diffusion Models]] — extends
- [[Diffusion Transformers (DiT)]] — extends
- [[Diffusion Model Training-Data Extraction]] — related
- [[SDEdit Guided Image Synthesis]] — extends
