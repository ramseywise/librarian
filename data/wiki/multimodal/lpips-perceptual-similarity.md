---
title: LPIPS Perceptual Similarity
tags: [multimodal, concept]
summary: "Zhang et al. build the 484k-judgment BAPPS dataset and show deep features from supervised, self-supervised and unsupervised networks agree with human similarity judgments better than L2, SSIM and FSIM; calibrated features give LPIPS (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-zhang-2018-unreasonable-effectiveness-deep-features-as.md
---

# LPIPS Perceptual Similarity

Zhang et al. (CVPR 2018) test the hypothesis that perceptual similarity is an emergent property of deep visual representations rather than a special function.

## Method

- **BAPPS dataset:** 64x64 patch triplets with 484k human judgments in a two-alternative forced choice (which distortion is closer to the reference), plus a just-noticeable-difference test, covering traditional and CNN-based distortions and real algorithm outputs (super-resolution, frame interpolation, deblurring, colorization).
- **Distance:** activations are unit-normalised along channels, differenced and squared between the two feature maps, averaged over space and summed across layers. LPIPS adds learned per-channel weights ("lin"). Other variants fine-tune the network ("tune") or train it from scratch ("scratch"), each with a small network predicting the human judgment.

## Results (self-reported, 2AFC over all six BAPPS test sets)

- Human agreement, the ceiling, is 73.9%. Uncalibrated SqueezeNet, AlexNet and VGG get 68.6, 68.9 and 67.0, while L2, SSIM and FSIMc get 63.2, 63.1 and 63.8. The learned LPIPS variants span 69.2 to 70.2, merely 1 to 2 points over uncalibrated networks.
- On real algorithm outputs, linear calibration improved 11 of 12 scores by 0.3 to 1.5 points. Fine-tuning VGG reaches 81.4 on distortion sets (humans 82.6) but transfers worse to real algorithms.
- A network with random Gaussian weights gets 64.3 and an unsupervised k-means network 66.6, so architecture by itself does not explain the gap. Across methods, the correlation between 2AFC and JND scores is rho 0.928. Among AlexNet-like methods, 2AFC tracks PASCAL classification at .640 and detection only at .363.
- Calibration is cheap: 1472 learned parameters for VGG, with about half of 1152 weights zero for AlexNet-lin.

## Limits

- Patches measure 64x64 and capture low-level similarity alone. 2AFC can be swayed by cognition, with JND serving as the check. Judgments came from a crowd platform, two collected per training triplet.
- On real algorithms LPIPS improves only slightly over uncalibrated networks, and fine-tuning damages transfer. SSIM was not designed for the dataset's geometric distortions, which may inflate the gap. A direct fit to human judgments failed to generalize.

## See Also
- [[Diffusion and GAN Image Generation]] — related
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — alternative-to
- [[Improved Techniques for Training GANs]] — related
