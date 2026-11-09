---
title: "pix2pix Conditional Adversarial Image Translation"
tags: [multimodal, concept]
summary: "pix2pix uses a conditional GAN with a U-Net generator and a 70x70 PatchGAN discriminator plus an L1 term as one general recipe for paired image-to-image translation across tasks."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-isola-2017-image-image-translation-conditional-adversarial.md
---

# pix2pix Conditional Adversarial Image Translation

The paper asks whether a conditional GAN with a learned loss can serve as a general-purpose solution to paired image-to-image translation without per-task loss engineering. The hypothesis is that a discriminator-learned loss penalises structure that per-pixel L1 or L2 losses miss and avoids blur, with L1 covering low frequencies and a patch-level GAN covering high frequencies.

## Mechanism

A U-Net generator G and a **PatchGAN** discriminator D, which classifies each 70x70 patch as real or fake over (input, output) pairs and averages the responses. The objective is the conditional GAN loss plus lambda times an L1 term on paired data (lambda 100 in the Cityscapes runs). The same architecture and objective are retrained per dataset.

## Results (self-reported)

Setup: Cityscapes labels to photo, 256x256, 200 epochs, batch size 1, evaluated by FCN-score (a segmenter run on synthesised photos) and AMT real-or-fake tests.

- L1 plus conditional GAN gives the best per-pixel FCN accuracy among objectives, close to the ground truth value of 0.80. An unconditional discriminator collapses to near-identical outputs.
- U-Net beats an encoder-decoder, which gets worse when the GAN term is added. A 70x70 patch reaches the best FCN accuracy; a full-image discriminator is much worse.
- Maps to aerial photos (about 50 Turkers): 18.9% of trials fooled, against nearly none for L1. Aerial to map: no significant difference from L1.
- Colourisation on ImageNet: 22.5% of trials fooled, similar to the L2 variant of a prior colourisation method but below that method's full version (27.8%).
- Photo to labels: plain L1 beats the GAN variants. L1 narrows the output colour distribution; the GAN term moves it toward ground truth.

## Limits

- Needs paired data; no unpaired setting.
- The noise input was ignored by G, so only dropout adds randomness; the full conditional distribution is not captured.
- Hallucinates small objects in segmentation; artifacts on sparse or unusual inputs.
- Each run is single, FCN-scores come without seeds, and both FCN-score and AMT tests are weak proxies. The bottleneck layer is zeroed by BatchNorm when batch size is 1 (an erratum the authors left unfixed). Community applications are uncontrolled.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[SR3 and Palette Image-to-Image Diffusion]] — alternative-to (diffusion models for the same translation tasks)
- [[AttnGAN Attentional Text-to-Image GAN]] — related (another conditional GAN, conditioned on text)
