---
title: "StyleGAN Style-Based Generator"
tags: [multimodal, gans, concept]
summary: "StyleGAN rebuilds the GAN generator around a mapping network and per-layer style modulation; StyleGAN2 replaces AdaIN with weight demodulation and drops progressive growing, StyleGAN3 removes aliasing to fix texture sticking, and Self-Distilled StyleGAN filters uncurated data and truncates toward cluster centres."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-karras-2019-style-based-generator-architecture-generative.md
  - data/raw/papers/2026-11-07-karras-2021-alias-free-generative-adversarial-networks.md
  - data/raw/papers/2026-11-07-mokady-2022-self-distilled-stylegan.md
  - data/raw/papers/2026-11-08-karras-2020-analyzing-improving-image-quality-stylegan.md
---

# StyleGAN Style-Based Generator

Four papers on one generator family. The first asks whether a generator rebuilt around style transfer gives better quality and a less entangled latent space; the second what causes StyleGAN's image artifacts; the third why fine detail sticks to pixel coordinates; the fourth how to train on raw Internet photos.

## StyleGAN (2019)

The Progressive GAN generator is redesigned. An 8-layer MLP maps z to an intermediate latent w; learned affine maps turn w into a scale and bias per feature map at every convolution (**AdaIN**); synthesis starts from a learned 4x4x512 constant; Gaussian noise is added after each convolution. **Mixing regularisation** forms some training images from two latents, switching at a random layer. Discriminator and loss are unchanged. The paper adds two latent-space metrics, **perceptual path length** and **linear separability**, and releases FFHQ, 70,000 faces at 1024x1024.

Results (self-reported), FFHQ unless noted:
- FID falls from 8.04 (baseline) to 4.40 (full model); CelebA-HQ from 7.79 to 5.17. The style generator improves on the tuned traditional one (FID 4.42 against 5.25).
- Mixing regularisation at 90% improves FID when four latents are mixed at test time (9.03 against 17.41).
- Path length in W is 200.5 with noise inputs, against 412.0 for the traditional generator in Z; linear separability is 3.61 in W against 10.78 in Z.
- Mapping depth: FID 5.06 with no mapping layer, 4.60 with one, 4.43 with two, 4.40 with eight. Full model on LSUN: Cars 3.27, Bedroom 2.65 and Cats 8.53 (FID). Parameters: 26.2M versus 23.1M.

## StyleGAN2 (2020)

Hypotheses: droplet artifacts arise because the generator smuggles signal-strength information around instance normalisation; a low perceptual path length goes with better images; and limited capacity prevents full use of the top resolution. The starting point is the official TensorFlow StyleGAN (config A); changes B-F are stacked one on another and scored on FFHQ and four LSUN categories by FID, PPL, precision and recall.

- **Weight demodulation** replaces AdaIN: after the style scales the convolution weights (w' = s w), each output feature map's weights are divided by the root of their summed squares plus eps.
- **Lazy regularisation** evaluates regularisers less often than the main loss (R1 every 16 minibatches) without harm.
- **Path length regularisation** penalises deviation of the Jacobian-projected norm ||J_w^T y||_2 from a constant a, so a step of fixed size in W gives an image change of fixed size; the authors add that inversion of the generator becomes easier.
- Progressive growing is replaced by a skip generator and residual discriminator, and feature maps at 64^2-1024^2 are doubled.
- Projection to W with noise-map regularisation lets generated images be attributed to a network.

Results (self-reported): FFHQ FID 2.84 against 4.40 for baseline StyleGAN (1024x1024, best-FID snapshot, 10 seeds average) and LSUN Car 2.32 against 3.27; FFHQ path length falls from 212.1 to 145.0 (lowest 122.5 at config D) and LSUN Car PPL from 1484.5 to 415.5. Weight demodulation by itself leaves FFHQ FID essentially unchanged (4.40 to 4.39); removing progressive growing gives 3.31; large networks lift recall from 0.449 to 0.492 and add 22% generator parameters (25M to 30M). On LSUN Car, path length regularisation trades FID (2.83 to 3.43) for PPL (981.6 to 651.2). Cat FID goes 8.53 to 6.93, Church 4.21 to 3.86, Horse 3.83 to 3.43. Adding spectral normalisation to G and D made FFHQ FID worse, 2.83 to 3.40. Training at 1024^2 runs 37 img/s (config A), 61 (E) and 31 (F) on 8 V100. Over the whole project, energy use was 131.61 MWh and compute 51.05 V100 GPU-years; the final FFHQ model 0.68 MWh. The baseline droplet artifact is missing from about 0.1% of images, producing severely corrupted ones (claim). [[Progressive Growing of GANs]] is the technique this paper removes.

## StyleGAN3 (2021)

Hypothesis: aliasing, from imperfect upsampling filters and pointwise nonlinearities, lets absolute position leak into the hierarchy. The StyleGAN2 generator is converted in stages: Fourier-feature input, no noise inputs, windowed-sinc filters, leaky ReLU placed between an upsampling and a downsampling step, flexible per-layer filters. StyleGAN3-R adds 1x1 convolutions and radially symmetric filters. Two new metrics, EQ-T and EQ-R (PSNR in dB), score translation and rotation equivariance.

- The final configuration scores FID 4.50 on FFHQ-U at 256x256, versus 4.79 for the Fourier-feature baseline (25M images, 50k samples). The extraction lists more FID, equivariance and parameter results but gives no values.
- Turning noise inputs back on lowers EQ-T; path length regularisation worsens FID; doubling capacity helps FID at almost 4x the training time. A fused custom kernel speeds training about 10x. One StyleGAN3-R run at 1024x1024 uses 0.9 MWh against 0.7 MWh for StyleGAN2.
- By the authors' visual judgement, EQ-T above about 50 dB and EQ-R above about 40 dB look high quality.

## Self-Distilled StyleGAN (2022)

A StyleGAN2 and an encoder are trained together on the raw collection. Images whose LPIPS reconstruction distance falls under a threshold (0.36 by default) are kept, and StyleGAN2 is retrained on them from scratch. At inference the latent is truncated toward the closest of 64 KMeans centres (closest by LPIPS) rather than the global mean.

- LSUN-Bicycle FID is 3.66 filtered against 5.42 unfiltered; a random subset of equal size performs like the unfiltered set.
- People rated 60-70% of samples real across five datasets. Multi-modal truncation is preferred over mean truncation at matched FID (Dogs, 27.37 against 27.18).

## Limits

- The source calls the 4.42 against 5.25 gain "almost 20%", but the numbers give about a 16% reduction.
- StyleGAN: the full-path metric is biased toward Z; mixing regularisation distorts W somewhat (path length 200.5 to 234.0); FID gains under R1 come with longer path length; no seeds or variance; FIDs are computed without truncation.
- StyleGAN2: the authors acknowledge that FID and precision/recall lean toward texture and miss some quality differences, which is why PPL is used alongside; path length regularisation trades FID against PPL on less structured data; larger networks may help further and the R1 gamma was not fully tuned; training needs tens of thousands of images; uncurated figures use truncation psi = 0.5; the attribution claim depends on one projection method with particular hyperparameters.
- StyleGAN3: only the generator is equivariant; it assumes unaliased training data; FID is slightly worse than StyleGAN2 on aligned FFHQ; no seeds; the video claims rest on hand-picked seeds; token-based GANs such as [[VQGAN Taming Transformers]] are left open.
- Self-Distilled StyleGAN: still struggles with complicated backgrounds; FID is measured against each model's own training set; rater counts, significance and seeds are not reported; the threshold was set by eye.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[BigGAN Large-Scale GAN Training]] — related (origin of the truncation trick that StyleGAN and Self-Distilled StyleGAN adapt)
- [[Frechet Inception Distance and the Two Time-Scale Update Rule]] — prerequisite-for
- [[StyleCLIP Text-Driven StyleGAN Editing]] — extends
- [[Progressive Growing of GANs]] — prerequisite-for
- [[Spectral Normalization for GANs]] — related (tested in StyleGAN2 and found to worsen FFHQ FID)
