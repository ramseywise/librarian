---
title: "Contrastive Self-Supervised Pretraining"
tags: [foundations, comparison]
summary: "Learn embeddings without labels by pulling positives together and pushing negatives apart (triplet loss, SimCLR, MoCo) or by avoiding negatives with a predictor plus moving-average target (BYOL), or by masking and reconstructing patches; collapse is the central failure and toy-scale runs do not reproduce paper gains."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--04-convolutional-networks.md
---

# Contrastive Self-Supervised Pretraining

## Triplet loss and verification

A classifier cannot handle new identities with one photo each, so learn f mapping an input to a vector where distance means identity. Triplet loss: max(||f(A)-f(P)||^2 - ||f(A)-f(N)||^2 + margin, 0). Verification thresholds one distance (one-to-one); recognition finds the nearest stored person (one-to-many). Toy on digits with 8 and 9 withheld: seen classes mean distance same 0.331, different 0.935; unseen 8 and 9, 0.449 vs 0.503. Eight training identities were too few to generalise to new ones.

## Contrastive methods

- **CPC v2** predicts a patch's representation from surrounding patches against negatives: 71.5% ImageNet linear-probe accuracy, up from 48.7% for v1.
- **MoCo** keeps a queue of past keys so negatives do not depend on batch size; keys come from a momentum encoder (0.999). Without momentum training failed; at 0.9 linear accuracy was 55.2% vs 59.0%.
- **SimCLR** uses the other 2(N-1) augmented images in a batch as negatives (NT-Xent loss, temperature-scaled cosine similarity); crop plus colour distortion; the representation before the projection head was over 10 points better than after. 76.5% linear at 4x width. Batch matters for short training: at 100 epochs 57.5% (batch 256) vs 64.8% (batch 8,192).
- **BYOL** drops negatives: an online network plus predictor chases a moving-average target (0.996 rising to 1). Without the moving average, or without predictor and negatives, it collapses to a constant (linear accuracy 0.3% or below). 74.3% vs SimCLR's 69.3%; 78.6% vs 76.5% at 4x width. Collapse not occurring is shown empirically, not explained, and batch norm stays throughout.
- **wav2vec 2.0** masks about half of 20 ms audio frames and picks the true quantized frame among 100 distractors. Quantizing inputs as well raised WER from 7.97 to 12.18. With 10 minutes of labels: 4.8/8.2 WER with a language model, 40.2/38.7 without.

## Masked-image pretraining

BEiT hides about 40% of ViT patches and predicts one of 8,192 discrete codes: 83.2% top-1; regressing raw pixels instead cut 82.86 to 81.04. Its frozen linear probe was weak (56.7% vs 78.2% for DINO). A masked autoencoder hides 75% of patches and runs the encoder only on the visible quarter, cutting compute 3.3x: ViT-H 87.8% at 448 px, frozen ViT-L probe 75.8% vs 77.6% for MoCo v3. ConvNeXt V2 masks 60% of 32x32 patches with sparse convolutions; Global Response Normalization raised 83.7 to 84.6 with no seeds reported. These features need fine-tuning.

## Toy reality check

NT-Xent plus a linear probe on digits lost to a supervised CNN at 20, 50 and 100 labels (0.404 vs 0.618, 0.571 vs 0.842, 0.651 vs 0.900): only about 1,250 unlabelled rows and weak augmentation. The mechanics reproduce; the label-efficiency result does not.

## See Also
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — prerequisite-for
- [[Transfer and Multi-Task Learning Conditions]] — related
- [[Neural Probabilistic Language Model]] — related (embeddings learned by prediction)
