---
title: "Classifier-Free Diffusion Guidance"
tags: [multimodal, concept]
summary: "One diffusion network is trained with the condition randomly dropped and, at sampling, the conditional and unconditional predictions are extrapolated, giving a fidelity/diversity trade-off without a separate classifier."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ho-2022-classifier-free-diffusion-guidance.md
---

# Classifier-Free Diffusion Guidance

The paper asks whether diffusion guidance can trade sample fidelity against diversity without training a separate classifier, the approach of [[Classifier Guidance and the ADM Architecture]].

## Mechanism

One class-conditional network is trained in which each training example has its label swapped for a null token with probability p_uncond; one network therefore yields both conditional and unconditional predictions. Sampling uses (1+w) times the conditional prediction minus w times the unconditional one. Larger w buys fidelity at the cost of diversity, and every step costs two evaluations. Data: class-conditional ImageNet, area-downsampled to 64x64 and 128x128.

## Results (self-reported)

- ImageNet 64x64 with p_uncond=0.1 and 400k steps: best FID is at almost no guidance (w=0.1); at w=4.0 FID worsens to 26.22 while Inception score reaches 260.2.
- ImageNet 64x64, w=0.0, 400k steps: p_uncond of 0.5 is worse than 0.1 or 0.2, and those two are about level.
- ImageNet 128x128, T=256 steps, 2.7M steps, w=0.3: FID 2.43, below the ADM-G value of 2.97 (as cited in the paper).
- ImageNet 128x128, T=256, w=4.0: the model beats BigGAN-deep at its maximum-IS truncation on both FID and IS.
- T=256 is described as a good quality/speed balance; because of the two evaluations per step, the compute-matched setting is T=128, which falls behind ADM-G on FID.

## Limits

- The authors describe it as a proof of concept; hyperparameters came from classifier-guidance tuning and may not suit this method.
- Two forward passes per step make sampling slower than with classifier guidance.
- Lower diversity under guidance could be a problem for datasets where rarer groups matter.
- Scope is class-conditional ImageNet alone, with no text conditioning. Optimizer, learning rate, batch size, model size and hardware are unstated, and there are no seeds or error bars.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Classifier Guidance and the ADM Architecture]] — prerequisite-for
- [[GLIDE Text-Guided Diffusion]] — extends
- [[Imagen Frozen Language Model Text Conditioning]] — extends
- [[InstructPix2Pix Instruction-Based Image Editing]] — extends
- [[Make-A-Scene Scene-Based Text-to-Image Generation]] — extends
- [[Make-An-Audio Text-to-Audio Latent Diffusion]] — instance-of
- [[Voicebox Flow-Matching Speech Infilling]] — related
