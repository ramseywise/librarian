---
title: BYOL Bootstrap Your Own Latent
tags: [multimodal, concept]
summary: "BYOL learns image representations with no negative pairs: an online network with a predictor regresses the projection of a slow moving-average target network on another augmented view."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-grill-2020-bootstrap-your-own-latent.md
---

# BYOL Bootstrap Your Own Latent

BYOL tests whether a strong self-supervised image representation needs negative pairs at all. An online network (encoder, projector, predictor) is trained to regress the l2-normalised projection of a second augmented view produced by a target network. The target has the same architecture without the predictor, and its weights are an exponential moving average of the online weights. Gradients are stopped through the target and the loss is symmetrised over the two views. Pretraining is on ImageNet with ResNets; evaluation covers linear probing, fine-tuning and transfer.

## Reported ablations (self-reported)

All of these are 300-epoch ablations on 64 TPU v3 cores with three seeds, using the authors' own JAX reproduction of SimCLR as the contrastive comparison.

- Removing colour distortion costs BYOL 9.1 points against 22.2 for the SimCLR reproduction; with random crops only, BYOL keeps 59.4 against 40.3.
- A batch of 256 against 4096 gives only a small BYOL drop.
- A fixed random target network (tau=1) reaches 18.8 top-1, while the randomly initialised network on its own gives 1.4 (self-reported). An instantaneous target (tau=0) collapses. Among base tau values of 0.9, 0.99 and 0.999, 0.99 does best.
- In the paper's unified formalism, adding negatives (beta=1) scores 70.9 versus 72.5 for BYOL, and giving SimCLR only a target network adds 1.6 points (self-reported).
- With no target network, an optimal closed-form linear predictor or a higher predictor learning rate still avoids collapse.
- The main run uses 1000 epochs at batch 512 on 64 TPU cores, about 4 days (base lr 0.4, tau base 0.9995, weight decay 1.5e-6).
- Removing weight decay makes both BYOL and SimCLR diverge.

## Limits

- No proof of why collapse is avoided; the authors only hypothesise, under the assumption of an optimal predictor.
- Undesirable equilibria remain possible; the authors report not seeing them.
- Relies on vision-specific augmentations; batch normalisation stays in the encoder and heads, and the method was never run without batch statistics.
- The authors' own SimCLR reproduction is the baseline for the ablations, which use 300 epochs; the main results carry neither seeds nor variance. Large fine-tuned ResNets overfit, and on depth the RMS error is worse than several baselines.
- The extraction leaves the headline linear-evaluation and semi-supervised figures blank, so they are not reproduced on this page.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for (the contrastive baselines BYOL drops negatives from)
- [[DINOv2 Curated-Data Self-Supervised Features]] — related (later self-distillation recipe)
