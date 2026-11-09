---
title: SPADE Spatially-Adaptive Normalization
tags: [multimodal, method]
summary: "SPADE injects a semantic segmentation mask into a GAN generator through per-pixel scale and bias predicted for each normalization layer, instead of feeding the mask as the input."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-park-2019-semantic-image-synthesis-spatially-adaptive.md
---

# SPADE Spatially-Adaptive Normalization

The question is whether a generator makes more photorealistic images from semantic segmentation masks when the mask drives the normalization layers rather than serving as the network input. The hypothesis is that normalization washes out the semantics of the input mask, and that learned, spatially varying scale and bias keep them. The authors argue analytically, with a figure for pix2pixHD, that for uniform masks InstanceNorm after a convolution gives all-zero activations whatever the label.

## Mechanism

SPADE (SPatially-Adaptive (DE)normalization) is a conditional normalization layer: instead of vectors, its scale and bias are spatial tensors computed from the input mask. Each layer applies BatchNorm without learned parameters and then a per-pixel gamma and beta that a two-layer conv net predicts from the resized mask: gamma(m) * (h - mu)/sigma + beta(m). The generator stacks SPADE residual blocks with nearest-neighbour upsampling and has no encoder. Training reuses the pix2pixHD multi-scale discriminator and loss with hinge GAN loss, and an optional VAE image encoder gives multi-modal, style-guided synthesis.

## Results

- On COCO-Stuff, SPADE reaches a higher mIoU than pix2pixHD and CRN (self-reported). Setup: 256x256; the numbers are in Table 1 of the paper.
- Users prefer SPADE over pix2pixHD and CRN on COCO-Stuff, while on Cityscapes their preference against SIMS is close to chance. Setup: crowd workers, 500 questions x 5 workers.
- On Cityscapes, SIMS gets a better FID than SPADE (49.7 against 71.8) but worse segmentation.
- Feeding the mask in by concatenation at every layer does worse than SPADE: the concatenation decoder scores worse than the SPADE decoder (self-reported). Setup: Table 3, COCO-Stuff.
- A compact SPADE decoder (61M parameters) matches the full one with fewer parameters; a 1x1 kernel on the label map and removing the perceptual loss both hurt COCO-Stuff mIoU (self-reported).

## Limits

- Evaluation leans on pretrained segmentation networks, which only check agreement of layout, plus FID and a human study; there are no repeated runs or seeds.
- The text and Table 1 give different COCO-Stuff mIoU values (35.2 against 37.4).
- Images are small (256x256, or 512x256 for Cityscapes); SIMS numbers come from the authors where they exist and were not retrained.
- Flickr Landscapes masks are machine-predicted. Comparisons are GAN-era; no diffusion models.

## See Also
- [[Denoising Diffusion Probabilistic Models]] — alternative-to (the later generative family)
- [[SR3 and Palette Image-to-Image Diffusion]] — alternative-to (image-to-image translation with diffusion)
- [[Vision-Language Model Training Families]] — related
