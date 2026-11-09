---
title: SDEdit Guided Image Synthesis
tags: [multimodal, method]
summary: "SDEdit noises a user guide image to an intermediate time t0 and runs the reverse SDE of a pretrained diffusion model, trading faithfulness to the guide against realism through t0, with no training."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-meng-2021-sdedit.md
---

# SDEdit Guided Image Synthesis

The question is how a pretrained diffusion or SDE generative model can synthesize and edit images from a user guide, trading faithfulness to the guide against realism, with no task-specific training and no inversion. The hypothesis is that noising the guide to an intermediate time t0 and then running the reverse SDE moves it onto the manifold of natural images, with t0 setting the balance.

## Mechanism

The guide is a full-resolution image made of manipulated RGB pixels. Forward SDE noise takes it to time t0 (for the VE SDE the noisy state is the guide x_g plus sigma(t0) times Gaussian noise z), and the reverse SDE is then simulated down to t = 0 by a pretrained score model. A mask variant protects unedited pixels by renoising the original at every step. Nothing is trained. A proposition bounds how far the output can deviate from the guide, a bound that grows with t0, assuming a limit on the score norm. Defaults are t0 = 0.5 for stroke synthesis and editing with the VP model, and 0.35 for compositing with the VE model; binary search on one image fixes the value, which the task then shares.

## Results

- On LSUN bedroom with human-drawn strokes, MTurk workers preferred SDEdit's realism over StyleGAN2-ADA by up to 98.09%, and overall satisfaction by up to 91.72% (self-reported). The closest baseline, e4e, is still beaten at 80.34% and 75.43%.
- Faithfulness L2 on human strokes is 32.55 against 53.76 for e4e (self-reported).
- A larger t0 means more realistic but less faithful outputs, and the sweet spot for reasonable guides is [0.3, 0.6] (self-reported). Setup: LSUN church, simulated strokes.
- On CelebA-HQ compositing, SDEdit's L2 is 21.70 against 36.67 for In-domain GAN (self-reported); against e4e, only 43.67% of workers preferred SDEdit on realism.
- It takes 29.1 s per 256x256 image on a 2080Ti against 5.2 s for In-domain GAN 2 (self-reported).
- A GAN-fake detector flags under 3% of SDEdit LSUN bedroom images against up to 93% of GAN images.

## Limits

- The text gives no per-t0 numbers for the trade-off curve, the sweet spot is empirical, and sharing one t0 per task is only justified by experiment.
- It is slower than GAN inversion with an encoder, requires a pretrained model from the target domain, and is unconditional.
- Realism is not uniformly better (e4e preferred on compositing); baselines are GAN inversion methods only.
- A misuse risk is noted: the fake detector misses SDEdit images.

## See Also
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for (the VP checkpoints it uses)
- [[SR3 and Palette Image-to-Image Diffusion]] — alternative-to (trained image-to-image diffusion)
- [[Pivotal Tuning Inversion]] — alternative-to (GAN inversion editing)
- [[Make-An-Audio Text-to-Audio Latent Diffusion]] — related
