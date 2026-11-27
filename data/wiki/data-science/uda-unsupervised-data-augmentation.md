---
title: "UDA: Unsupervised Data Augmentation"
tags: [data-science, deep-learning, concept]
summary: "UDA adds a consistency loss between predictions on an unlabeled example and its strongly augmented version (RandAugment for images, back-translation for text) to supervised cross-entropy, and reports 5.43% CIFAR-10 error with 250 labels."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-xie-2019-unsupervised-data-augmentation-consistency-training.md
---

# UDA: Unsupervised Data Augmentation

Xie et al. (NeurIPS 2020; arXiv v6) test whether swapping the simple noise used in semi-supervised consistency training for strong, state-of-the-art augmentation gives better results when labels are scarce. They expect the augmentations that are best for supervised learning to also be the best noise for unlabeled data.

## Method

UDA's objective adds a lambda-weighted consistency term to the ordinary supervised cross-entropy on labeled data. In words: the first term is the negative log-likelihood of the true label f* on labeled x1; the second is lambda times the expected cross-entropy between the fixed copy's prediction for an unlabeled x2 and the model's prediction for an augmented version xhat drawn from q.

The prediction on the unaugmented unlabeled input is produced by a copy of the model whose parameters are held fixed. The augmenters are RandAugment for images and, for text, back-translation (English-French, with sampling) and TF-IDF-based word replacement. Further techniques:

- **Training Signal Annealing (TSA):** a labeled example is dropped from the loss once p(y*|x) is above a threshold, and that threshold grows from 1/K to 1 as training proceeds.
- **Confidence-based masking:** the consistency term is applied only to unlabeled examples whose top predicted probability is over a threshold beta.
- Sharpening of predictions, and filtering unlabeled data for domain relevance.

## Results (self-reported)

- IMDb with 20 labeled examples, BERT-finetune initialisation: 4.20 error, below the pre-BERT state of the art of 4.32 trained on 25k labels.
- CIFAR-10, WRN-28-2, mean of 10 runs: 5.43% error with 250 labels (std 0.96); 4.32 with 4k labels against MixMatch's 6.24. PyramidNet+ShakeDrop (26M parameters) with 4k labels gets 2.7, matching fully supervised training on 50k. SVHN with 250 labels: 2.72.
- ImageNet 10% labels, ResNet-50, image size 224: top-1 rises from 58.84 (supervised with RandAugment) to 68.78. Adding 1.3M filtered JFT unlabeled images to the full label set (image size 331) moves it from 78.43 to 79.05.
- Augmentation quality carries over from supervised to semi-supervised: on CIFAR-10 with 4k labels RandAugment gives 4.32 against 10.94 for crop and flip. On Yelp-5 with 2.5k labels (random-init Transformer): back-translation 41.35, Switchout 43.38, none 50.80; TSA's exponential schedule cuts error from 50.81 to 41.35 (6m unlabeled).
- Cutting unlabeled data hurts more than cutting labeled data: CIFAR-10 with 250 labels gets 5.43 with 50,000 unlabeled and 35.41 with 5,000.

## Limits

- On five-class sentiment tasks, UDA with 500 labels per class remains clearly behind BERT trained on all the supervised data.
- RandAugment magnitude range and probability were not tuned.
- The accompanying theory presumes augmentation that is in-domain, label-preserving and reversible, which is a simplification.
- CIFAR-10 used augmentations generated ahead of time (dumped offline); the paper says generating them online is equal or better.
- Seed counts are not stated for text and ImageNet; the BERT optimiser and warmup are not stated.
- The authors' own MixMatch reimplementation was slightly worse than reported, and the table baselines are those MixMatch reported.

## See Also
- [[Noisy Student Self-Training]] — related
- [[Back-Translation with Monolingual Data]] — related
- [[GPT3Mix: LLM Text Augmentation]] — alternative-to
