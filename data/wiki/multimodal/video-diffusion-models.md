---
title: "Video Diffusion Models"
tags: [multimodal, concept]
summary: "A Gaussian diffusion model with a space-time factorized 3D U-Net generates video, trained jointly on images and video and extended in time or space with reconstruction-guided sampling."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ho-2022-video-diffusion-models.md
---

# Video Diffusion Models

The paper asks whether a plain Gaussian diffusion model with a 3D U-Net split across space and time can produce coherent video, including long and text-conditioned clips. Two ideas are tested: joint training on images and video, and **reconstruction guidance**, a new conditional sampler.

## Mechanism

Continuous-time Gaussian diffusion predicting noise (or v) with a 3D U-Net built from 1x3x3 convolutions, spatial attention and added temporal attention blocks. Training uses fixed-size frame blocks (16 frames at 64x64, 9 at 128x128). Longer or larger video is produced by conditional sampling from the model trained unconditionally. Reconstruction guidance corrects the denoising prediction for new frames using the gradient of how well the already-generated conditioning frames are reconstructed, scaled by a weight; the alternative is the replacement method. Video prediction reuses the unconditional models.

## Results (self-reported)

- Text-to-video, small 16x64x64 model, FVD against the training set: training with 8 independent images per video lowers FVD from 202.28 to 57.84.
- Large 16x64x64 text-to-video model with 8 image frames: classifier-free guidance weight 5.0 gives FVD 163.74, against 41.65 at weight 1.0 (no unguided row).
- Autoregressive extension to 64 frames from a 16-frame model (guidance weight 2.0): reconstruction guidance gives FVD 136.22 against 451.45 for replacement.
- UCF101 unconditional 16x64x64 (C3D features, 10,000 samples): FID 295 and Inception score 57; real data has 60.2.
- BAIR 64x64 video prediction (1 conditioning frame, 15 generated): FVD 66.92 using a Langevin sampler with 256 steps. Kinetics-600 64x64 (5 conditioning, 11 generated): FVD 16.2 at 128 steps, or 16.9 under the replacement-sampling protocol of prior work.

## Limits

- The 10-million-video captioned text dataset is not named or described, and models are not released because of societal-harm concerns; text-to-video inherits bias, not audited.
- Small fixed blocks mean longer videos rely on autoregressive extension. UCF101 is scored at 64x64, which the authors say may hurt it.
- Metric protocols differ across the literature, so scores from different papers diverge slightly. The independent images used in joint training come from the same video dataset.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
