---
title: Pivotal Tuning Inversion
tags: [multimodal, method]
summary: "Pivotal Tuning Inversion inverts a real face to a W-space pivot code in StyleGAN2, then fine-tunes the generator around the pivot with a locality regularizer so latent edits still work."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-roich-2022-pivotal-tuning-latent-based-editing.md
---

# Pivotal Tuning Inversion

The question is how to invert a real face image, even one far from the training domain, into StyleGAN so that it is rebuilt faithfully yet still editable with latent-space editors, escaping the distortion-editability trade-off (latents near W edit well but distort more; W+ distorts less but edits less well). The hypothesis is that StyleGAN's disentanglement lets a small local change to the generator send the image to an editable pivot code in W with no damage to editing behaviour.

## Mechanism

Step 1 finds a pivot code w_p in the W space of StyleGAN2 by direct optimization of the image (LPIPS plus noise regularization), keeping the generator frozen. In step 2 the generator's weights are released and tuned until G(w_p) reproduces the image (LPIPS plus L2), with a locality regularizer that leaves images from interpolated latents unchanged. Edits then use ready-made latent editors (InterfaceGAN, GANSpace, StyleCLIP). Pivotal tuning is a short training run that preserves the editability of a region of latent space inside the domain while changing the identity and look it depicts.

## Results

- PTI has the lowest LPIPS reconstruction error against SG2 W+ 0.34, e4e 0.4 and SG2 0.4, and the highest identity similarity (self-reported). Setup: StyleGAN2 trained on FFHQ, first 1000 CelebA-HQ test images.
- ID similarity after single edits (smile, pose, age averaged) and after sequential edits is highest for PTI (self-reported).
- At fixed rotations of +-5 and +-10 PTI keeps the best identity (self-reported).
- The whole two-step inversion runs on a single RTX 2080 per image; the limits section puts it at about 3 minutes.
- Letting the pivot move during tuning changes the image negligibly (self-reported).

## Limits

- Each image needs optimization (about 3 min), not a single feed-forward pass.
- Only StyleGAN2 faces were tested; one image per identity.
- Tuning many identities without locality regularization produces artifacts and shifts identity at latents far from the pivot. StyleCLIP needs pivots from e4e rather than W pivots.
- StyleCLIP edits need pivots from e4e rather than W pivots.
- The tables have no seeds or variance; PTI is compared only with SG2, SG2 W+ and e4e, and pSp is left out.

## See Also
- [[SDEdit Guided Image Synthesis]] — alternative-to (training-free editing without GAN inversion)
- [[Diffusion Model Training-Data Extraction]] — related
