---
title: "ImageNetV2 and the Adaptivity Gap in Test-Set Reuse"
tags: [data-science, concept]
summary: "Recht and colleagues rebuilt the CIFAR-10 and ImageNet test sets by the original recipe: every model lost accuracy, but the ranking held and later models did not lose more, which points at distribution shift rather than overfitting to the reused test set."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-recht-2019-do-imagenet-classifiers-generalize-imagenet.md
---

# ImageNetV2 and the Adaptivity Gap in Test-Set Reuse

Years of tuning against one fixed test set could make its scores optimistic. Recht, Roelofs, Schmidt and colleagues test this by drawing new test sets, 2,000 images for CIFAR-10 and 10,000 for ImageNet, by re-running the original creation pipelines, without running any classifier during collection, then scoring existing models on both. The ImageNet set in the extraction is called MatchedFrequency.

## Two gaps

- **Adaptivity gap:** the amount by which fitting to the test set makes test error understate population loss.
- **Distribution gap:** the loss change caused by moving from the original data distribution to the new one.

The conventional expectation the authors state is that drops come from adaptivity, so the most heavily tuned, latest models should gain least on fresh data.

## Results (self-reported)

| Finding | Setup |
|---|---|
| CIFAR-10 accuracy drops of 3 to 15% | Broad model testbed, new 2,000-image set |
| ImageNet top-1 drops of 11 to 14%; best model fell from 82.9 to 72.2 | PNASNet large, MatchedFrequency set |
| New accuracy is roughly linear in original accuracy, so ranking is almost preserved | ImageNet slope 95% CI [1.07, 1.19]; CIFAR-10 slope [1.63, 1.76], so better models lose less there |
| Best CIFAR-10 model dropped only 3 points | AutoAugment PyramidNet |
| Top-5 accuracy on ImageNet fell about 6 points, which the authors liken to roughly five years of progress | 2018 state of the art, 96% to 90% |
| Re-tuning a VGG against the new CIFAR-10 set gained at most 0.5 points | Grid search on learning rate, dropout and weight decay |
| Near-duplicates of training images make up about 800 (8%) of the original CIFAR-10 test set and account for at most about 1% of the gap | Visual inspection of nearest neighbours |
| A CNN discriminator separating old from new CIFAR-10 test images reached at best 53.1% | Pretrained ResNet-110 discriminator |
| An adversarially robust CIFAR-10 model sits on the same fit | Madry et al. baseline |

Sampling strategy alone moved ImageNet accuracy by 14 points. Average change over models relative to the original validation set was -11.8 (MatchedFrequency), -3.2 (Threshold0.7) and +2.1 (TopImages). Selection frequency (the share of MTurk workers choosing an image for its class) averaged 0.73, 0.85 and 0.93 for the three sets, and 0.71 for the original validation set. Images with selection frequency in [0.4, 0.6) scored about 20% lower than the whole new set.

Because later models did not lose more, the authors read the gap as mostly distribution shift, the leading hypothesis rather than a proven cause.

## Limits

- The two gaps cannot be fully separated: if every model lost the same amount to adaptivity, no diminishing-returns pattern would appear. A fully i.i.d. "super hold-out" would be needed, and none exists for these datasets.
- The ImageNet MTurk process cannot be replicated exactly (2010 to 2012 worker pool, agreement thresholds), hence three sampling strategies.
- The human check is small and preliminary (9 graduate students, CIFAR-10 only, hardest images). The Fisher-vector model is not a faithful reproduction.
- What makes the new images harder is not identified; only a correlation with selection frequency is shown. Image classification only.
- The Gaussian difficulty model that explains the linear probit-scale fit is, per the authors, not the true explanation.

## See Also
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[ImageNet-A and ImageNet-O Natural Adversarial Examples]] — related (a harder shift built by filtering against a model)
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
- [[Test-Time Training with a Rotation Auxiliary Task]] — related
