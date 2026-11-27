---
title: "Colorization as Classification over Quantised Colour Bins"
tags: [data-science, deep-learning, concept]
summary: "Zhang, Isola and Efros predict a distribution over 313 quantised ab colour bins per pixel, reweight by colour rarity and decode with an annealed mean; the paper reports that 32% of AMT trials judged its output real, and tests colorization as a self-supervised pretext task (self-reported)."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-zhang-2016-colorful-image-colorization.md
---

# Colorization as Classification over Quantised Colour Bins

Zhang, Isola and Efros (ECCV 2016) ask whether a CNN can colorize grayscale photos plausibly rather than only accurately, given that one grey pixel admits many colours, and whether the task can serve as a pretext for self-supervised feature learning. Their hypothesis is that per-pixel classification over quantised colour bins with class rebalancing, in place of L2 regression, avoids desaturated output.

## Mechanism

- **Network:** a single-stream CNN in the style of VGG, with dilated convolutions and BatchNorm in place of pooling, turns the L channel into a distribution over Q = 313 quantised ab bins for every pixel.
- **Loss:** soft-encoded multinomial cross-entropy, reweighted by colour rarity.
- **Decoding:** the annealed mean takes the mean of the softmax distribution after readjusting its temperature T, interpolating between the mean and the mode. T = 0.38 is used, chosen to keep the vibrancy of the mode and the spatial coherence of the mean: with f_T(z) = exp(log z / T) divided by the sum over bins q of exp(log z_q / T).
- **Evaluation:** three measures: an AMT real-versus-fake test (a colorization Turing test), how well VGG-16 classifies the recolorized images, and AuC. Training uses 1.3M ImageNet photos.
- **Pretext use:** the model is a cross-channel encoder: like an autoencoder, but it reads one set of image channels (L) and predicts another (ab). AlexNet pretrained this way is tested with ImageNet linear probes and on PASCAL.

## Results (self-reported)

- Test set: the same 10k ImageNet validation images Larsson et al. used. With classification loss, rebalancing and T = 0.38, 32% of AMT real-versus-fake trials were fooled; this is significantly above every baseline except Larsson et al. (p = 0.10). In the attention check, Random colorizations were called fake 87% of the time.
- Rebalancing yields the top class-balanced AuC of any method. Without class balancing, desaturated pixels dominate AuC, and a prediction of plain grey scores close to the full method. VGG-16 top-1 on recolorized images beats its grayscale value; ground-truth colour gives 68.3.
- Speed on a Titan X with Caffe: 22.1 ms against 122.1 ms for Larsson et al.
- An L2-regression model trained from scratch is worse than the classification model; started from the classification network and fine-tuned, it ties (AuC 91.5 against 91.6).
- On a 240-image, 6-category LEARCH/SUN test set (the input is the mean of R, G and B; the model was not trained on SUN) the AMT fooling rate beats Deshpande et al. (9.8%).
- As pretraining (AlexNet, 450k iterations, FCN fine-tune, colour input), the colour-input net reaches state-of-the-art VOC2012 segmentation among the self-supervised methods tested. On VOC2007 detection with Fast R-CNN the extraction reports 47.9 and 46.9 (see Limits), both below Doersch et al. (51.1) and ImageNet supervision (56.8).

## Limits

- The goal is plausible colour rather than the true colour, and AuC measured against ground truth does not favour the full method (89.5 against 91.7 for Larsson et al.).
- The 32% AMT rate is well below the 50% ground-truth ceiling. Failure modes include long-range consistency, red and blue confusion, and sepia tones in busy indoor scenes.
- The paper omits the batch size, the seeds, how many GPUs were used and how long training ran, and part of the architecture detail is on the project page.
- The appendix analyses were produced with the earlier v1 model and not the v2 model used in the main text.
- The extraction's detection figures are inconsistent: one passage ties 47.9 to grayscale input and also mentions it for colour, while another gives 46.9 for colorization-pretrained detection.
- Linear probes lose about 6% with grayscale input. Table 3 compares self-supervised methods that each use AlexNet with different architectural modifications.

## See Also
- [[VGG Depth with Stacked 3x3 Filters]] — prerequisite-for
- [[Contrastive Self-Supervised Pretraining]] — related (another pretext route to image features)
- [[Batch Normalization]] — prerequisite-for
- [[SR3 and Palette Image-to-Image Diffusion]] — related (Palette also reports a colorization result)
