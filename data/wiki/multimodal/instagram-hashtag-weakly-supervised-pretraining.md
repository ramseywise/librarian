---
title: Instagram Hashtag Weakly Supervised Pretraining
tags: [multimodal, vision-backbones, concept]
summary: "Mahajan et al. (ECCV 2018) pretrain ResNeXt-101 networks on up to 3.5B public Instagram images labelled by hashtags and reach 85.4% ImageNet-1k top-1; accuracy rises log-linearly with data, tolerates injected label noise, and the results cannot be replicated (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-mahajan-2018-exploring-limits-weakly-supervised-pretraining.md
---

# Instagram Hashtag Weakly Supervised Pretraining

Mahajan, Girshick, Ramanathan et al. (ECCV 2018) study supervised pretraining on billions of weakly labelled social-media photos and how well it transfers to classification and detection. They vary data size, label vocabulary, label noise, sampling and model capacity. The authors worry that hashtags are a noisy signal but expect sheer scale to make up for it, and they also expect the 1.5k-hashtag vocabulary to look visually like IN-1k while the 8.5k and 17k vocabularies reach finer-grained categories. All results are the paper's own (self-reported).

## Method

The networks are ResNeXt-101 32xCd models trained to predict hashtags with a softmax, using a multi-label target that gives each of an image's k hashtags weight 1/k; pretraining data is up to 3.5B public Instagram photos. Transfer targets are ImageNet, CUB2011 and Places365 (by full finetuning, or by training only a linear classifier over frozen features) and COCO through Mask R-CNN. One factor at a time changes: vocabulary, number of images, injected noise, class resampling, network size. Because hashtags follow a Zipf-like distribution, resampling gives hashtag h a rate that is the larger of 1 and phi applied to t divided by f(h) (phi is uniform or square-root), and an image takes the highest rate among its hashtags.

## Results

- Pretrained on IG-940M-1.5k and then finetuned on IN-1k, ResNeXt-101 32x48d (829M parameters) gets 85.4% single-crop top-1 and 97.6% top-5, the best reported at that time. For a 32x16d model, pretraining on about 1B images with 1.5k hashtags is 4.6 points better than using IN-1k alone.
- Using the 3.5B-image, 17k-hashtag model, a linear classifier on frozen features comes close to full finetuning.
- Accuracy grows log-linearly in the number of pretraining images (from 3.5M up to 3.5B); bigger networks gain more for each multiplication of data. The trend flattens through ceiling effects and bends between 1B and 3.5B images.
- A vocabulary matched to the target label set wins over a larger mismatched one: on IN-1k the aligned 1.5k set beats 17k, but on IN-9k the 17k set is ahead by roughly 7 points.
- Noise in the pretraining labels is tolerable: swapping 10% of hashtags for random ones costs under 1 point, and 25% costs about 2 (32x16d, IG-1B-17k, linear classifier on IN).
- Either uniform or square-root resampling lifts ImageNet transfer by 5 to 6 points relative to natural sampling (32x4d, IG-1B-17k).
- Rectifying IN-1k labels with five human annotators (four of five must agree) raises top-1 for the 3.5B-image 17k model from 87.5% to 90.4%.
- Instagram pretraining keeps paying off for larger models, whereas training from scratch on IN-1k saturates; 32x32d needs 2.4 times and 32x48d 4.3 times the FLOPs of 32x16d.
- Detection: a 32x16d Mask R-CNN backbone pretrained on Instagram instead of IN-1k lifts COCO box AP from 43.7 to 45.2. Such detectors need finetuning learning rates roughly 4 to 10 times smaller. Keypoint detection ends up worse than with IN-1k, which hints that hashtag pretraining might harm localisation.
- Over 80% of IN-1k classes improve with Instagram pretraining, and 20% improve by 10 points or more. Finetuning the whole 3.5B 17k model gives 58.0% on Places365 and 89.2% on CUB2011. How predictable a hashtag is correlates moderately with how concrete the noun is.
- The 32x16d network needed about 22 days on 336 GPUs (batch size 8,064) to train on 3.5B images.
- Some test images also occur in the pretraining pool; when they are counted wrongly, IN-1k accuracy only moves from 84.2 to 83.9 (R-MAC nearest-neighbour search across 3.5B images).

## Limits

- The authors state that the work cannot be replicated, since other people cannot tell which images were used or fetch them in bulk.
- Only ResNeXt-101 convolutional networks were tried; applying the findings to other architectures is a belief and was not tested.
- Noise was added by hand, and what real hashtag noise looks like is never characterised.
- The log-linear trend departs from a straight line from 1B to 3.5B images and flattens for IN-1k and CUB, which the authors put down to underfitting. The detection and keypoint results suggest localisation may suffer.
- Duplicate lower bounds were not computed for the ImageNet-pretrained baselines.
- Runs were single, without confidence intervals except for a two-sample check (under 0.1%) on the linear experiments with 1B images. Neither the GPU type nor the warm-up length is given.

- Superseded: ViT-scale and later web-scale and self-supervised pretraining have exceeded the 85.4% figure.

## See Also
- [[ResNeXt Cardinality in Residual Blocks]] — prerequisite-for (the architecture family used)
- [[Big Transfer (BiT) Generalist Pretraining]] — related (another large-scale pretraining recipe)
- [[DINOv2 Curated-Data Self-Supervised Features]] — related
- [[LAION-5B Open CLIP-Filtered Image-Text Dataset]] — related
