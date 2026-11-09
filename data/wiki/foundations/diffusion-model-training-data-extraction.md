---
title: Diffusion Model Training-Data Extraction
tags: [foundations, concept]
summary: "Carlini et al. show a black-box generate-and-filter attack that pulls memorized training images out of Stable Diffusion and Imagen, and a CIFAR-10 study finding diffusion models leak more training data than GANs (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-carlini-2023-extracting-training-data-diffusion-models.md
---

# Diffusion Model Training-Data Extraction

Carlini, Hayes, Nasr et al. (2023, arXiv 2301.13188) ask whether image diffusion models memorize and re-emit individual training images, and how modelling and data choices change that leakage. Their hypothesis is that diffusion models do not only generate novel images and are less private than GANs.

## Definitions

- **(l,delta)-Diffusion Extraction:** an image x counts as extractable when some efficient algorithm, never shown x, emits a copy within distance delta of x under l.
- **(k,l,delta)-Eidetic Memorization:** an extractable x with at most k training examples near it (within delta) is eidetically memorized.

## The attack

The attack is black box and has two steps. First it selects captions that appear many times in the training set (judged by CLIP embedding similarity) and samples 500 images for each. Then it marks any clique of at least ten near-identical samples (tile-wise l2 distance) as a memorization candidate and checks it against the training data. For CIFAR-10 the authors trained 16 diffusion models, each on a random half of the data, and tried untargeted extraction, inpainting, and two membership-inference attacks (a loss threshold and LiRA), with GANs as the comparison.

## Results (self-reported)

Large models, black box:

- Against Stable Diffusion v1.4, using the 350,000 prompts with the most duplicates and 500 samples each, the attack extracts 94 images at (l2, 0.15). Hand annotation of the top 1,000 samples raises that to 109 near-copies.
- A further run of the same attack identifies 50 memorized images and no false positives among 175 million samples.
- Against Imagen 2B at 500 samples per prompt, 23 of the top 1,000 duplicated prompts give memorized images.
- An outlier attack picks the 500 images furthest out by CLIP kNN distance: Imagen memorizes 3 of them, Stable Diffusion none out of 10,000.
- For Stable Diffusion at delta=0.1, eidetic memorization is rare below k=100 duplicates, and duplicated images are about one in a million training examples. This is an upper bound, since prompts came from duplicated images.
- Of the extracted Stable Diffusion images, 58% show a recognizable person and 35% have a copyright notice that is not permissive.

CIFAR-10 diffusion models (setups as given per line):

- Sixteen unconditional models (with an adaptive l2 cutoff, alpha=0.5, n=50) together yield 1,280 distinct training images, 2.5% of the set, out of 1 million samples.
- LiRA run with 16 shadow models on random halves, scoring loss at t=100, reaches over 70% TPR at 1% FPR; classifiers stay below 20%.
- A stronger LiRA with 20 noise draws plus flip augmentation moves the 0.1% FPR operating point from 7% TPR to 44%.
- Membership-inference success climbs from 7% to nearly 100% as training improves FID. TPR at 1% FPR rises from 5% after 5M processed examples to 99% after 102M.
- On ready-made CIFAR-10 models with FID 2.9 each, the best DDPM extracts 301 images and StyleGAN-ADA 150, per 1 million samples. Diffusion membership inference reaches 50% TPR at 0.1% FPR, while GANs (attacked via discriminator loss) stay under 30%.
- 244 images are memorized by both the diffusion model (1,280 in total) and a StyleGAN (361 in total); chance would give about 10.
- Removing 5,275 near-duplicates from CIFAR-10 (imagededup similarity above 0.85) lowers regenerated training examples only from 1,280 to 986.
- In the authors' codebase DP-SGD training diverged, even with epsilon near 50.
- Canaries of uniform noise, inserted twice, reach the maximum exposure of 10.

## Limits

- The definition of extraction is intentionally strict and l2-based, so a recognizable but non-identical output is not counted.
- Numbers for Stable Diffusion and Imagen come from heavily duplicated images and so bound the true rate from above; no extraction of a rarely duplicated Stable Diffusion image was found.
- Imagen's training data is not public, so no side-by-side examples exist.
- The extraction notes: the CIFAR-10 models come with no optimizer, learning-rate, batch or hardware details, and no seeds or confidence intervals.
- Why DP-SGD failed was not examined.
- The authors grant that copying versus generalizing is still undecided.

## See Also
- [[Min-K% Prob Pretraining-Data Detection]] — related (membership detection for language-model training data)
- [[LM Red Teaming]] — related (training-data leakage found by probing a deployed model)
- [[Laplace Mechanism and Sensitivity-Calibrated Noise]] — related (the formal privacy tool whose DP-SGD variant failed to train here)
- [[Diffusion and GAN Image Generation]] — related
- [[Pivotal Tuning Inversion]] — related
