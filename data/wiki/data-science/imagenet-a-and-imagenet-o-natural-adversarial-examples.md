---
title: "ImageNet-A and ImageNet-O Natural Adversarial Examples"
tags: [data-science, deep-learning, concept]
summary: "Hendrycks and colleagues keep only real images that a ResNet-50 gets wrong, giving test sets on which many unseen models fail; augmentation and extra data help little, architecture helps more."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-hendrycks-2021-natural-adversarial-examples.md
---

# ImageNet-A and ImageNet-O Natural Adversarial Examples

## Construction (adversarial filtration)

Adversarial filtration discards examples that fixed models classify correctly and retains the hardest ones, which strips out simple spurious cues.

- **ImageNet-A:** 7,500 unmodified images over 200 ImageNet classes, scraped from iNaturalist, Flickr and DuckDuckGo. An image stays only if ResNet-50 misclassifies it with low confidence; the remainder are hand-selected. For the dragonfly class, 81,413 downloads went to 8,925 after the filter, 1,452 after a diversified shortlist and 80 by hand.
- **ImageNet-O:** 2,000 out-of-distribution images from ImageNet-22K, drawn from classes outside ImageNet-1K and kept when ResNet-50 assigns them a label with high confidence. Scored by AUPR, with chance about 16.67%.

## Results (self-reported)

Setup: top-1 accuracy on ImageNet-A and AUPR on ImageNet-O. Intervention rows (pretraining, augmentation, adversarial training) modify a ResNet-50 trained on ImageNet-1K; architecture rows are that architecture.

| Model or intervention | ImageNet-A | ImageNet-O AUPR |
|---|---|---|
| ResNet-50 baseline | 2.17% | 16.20% |
| DenseNet-121 (not used in filtering) | about 2% | near random |
| ResNet-152 | 6.1% | 18.0% |
| ImageNet-21K pretraining, then 1K fine-tune | 11.41% | 21.86% |
| CutMix | 7.3% | not stated |
| Mixup / MoEx / Cutout / AugMix | 6.6 / 5.5 / 4.4 / 3.8% | not stated |
| Adversarial training (Wong et al. 2020) | 1.68% | not stated |
| Places365 pretraining | 1.56% | 14.88% |
| Res2Net-152 v1b | 22.4% | 23.9% |
| DeiT-base (aggressive augmentation) | 28.2% | 24.8% |

Other findings (self-reported): fine-tuning on 80% of ImageNet-A did not clearly help the remaining 20% (top-1 below 2%); FID between ImageNet-A and the ImageNet validation set is 50.40 against about 0.99 between validation and test; estimated graduate-student accuracy is about 90%. The best augmentation gains about 5 points; on ImageNet-O, a maximum-logit detector does not beat the maximum softmax probability baseline.

Contrast with [[ImageNetV2 and the Adaptivity Gap in Test-Set Reuse]]: the paper cites Engstrom et al. as putting the ImageNetV2 drop below 3.6%, while ImageNet-A accuracy can fall more than 50%.

## Limits

- Only ResNet-50 did the filtering, so the sets lean toward its mistakes; transfer to other models is shown empirically.
- Each trained-model result is one number, with no seeds or intervals and no augmentation hyperparameters given. Vision only.
- Image overlap leads the authors to discount ImageNet-O gains from ImageNet-21K pretraining; they advise not training on ImageNet-22K because the task would turn trivial.
- DeiT-small appears as 19.1 in Table 1 but 19.0 in the text (the text compares it with 14.6 for Res2Net-50).
- The 3.6% figure for ImageNetV2 is reported second-hand from Engstrom et al. and is not the 11 to 14% top-1 drop that Recht et al. measured; the extraction does not say what quantity it covers.

## See Also
- [[ImageNetV2 and the Adaptivity Gap in Test-Set Reuse]] — related
- [[Dynabench]] — related (examples collected against a target model)
- [[Noisy Student Self-Training]] — related
