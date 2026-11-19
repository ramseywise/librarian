---
title: "Contrastive Visual Representations: SimCLR, MoCo, CPC v2 and PIRL"
tags: [multimodal, vision-backbones, comparison]
summary: "Four contrastive image-pretraining recipes compared by where the negatives come from and what the positive pair is: in-batch views with a projection head (SimCLR), a queue with a momentum key encoder (MoCo), spatial patch prediction (CPC v2) and pretext-transformed views against a memory bank (PIRL)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-chen-2020-simple-framework-contrastive-learning-visual.md
  - data/raw/papers/2026-11-07-he-2020-momentum-contrast-unsupervised-visual-representation.md
  - data/raw/papers/2026-11-07-henaff-2019-data-efficient-image-recognition-contrastive.md
  - data/raw/papers/2026-11-08-misra-2020-self-supervised-learning-pretext-invariant.md
---

# Contrastive Visual Representations: SimCLR, MoCo, CPC v2 and PIRL

These four papers learn image representations without labels and evaluate them mainly by a linear probe (a linear classifier on the frozen network) and by fine-tuning on few labels or on detection. They differ in how a positive pair is made and where the negatives come from. The overview of the family is [[Contrastive Self-Supervised Pretraining]]. All numbers below are self-reported by the respective papers, on ImageNet unless noted, and the comparison tables in the papers mix architectures, epochs and augmentations.

## SimCLR

Each image gets two random augmentations; a single shared ResNet encoder f and a small MLP projection head g (two layers) map both views to z. The NT-Xent loss (normalised temperature-scaled cross entropy) for a positive pair (i,j) is the negative log of exp(sim(z_i,z_j)/tau) divided by the sum of exp(sim(z_i,z_k)/tau) over every k other than i, so the other 2(N-1) views in the batch serve as negatives. Once pretraining ends g is discarded and the encoder output h is evaluated.

- ResNet-50 at 4x width, 1000 epochs, batch 4096: 76.5% top-1 linear, equal to a supervised ResNet-50. Fine-tuning with 1% of the labels gives 85.8% top-5 (supervised 48.4), and with 10% gives 92.6% top-5 (supervised 80.4). With all labels and broader pretraining augmentation, fine-tuning gets 80.4% top-1 against 78.4% from scratch.
- Ablations at 100 epochs on ResNet-50: a nonlinear head improves on a linear one by about 3% and on none by over 10%; the representation h is more than 10% better than g(h), because h keeps transformation information that g(h) discards (a rotation probe gets 67.6% from h but 25.6% from g(h), where chance is 25%). NT-Xent at 63.9 outperforms margin, logistic and semi-hard-negative losses, whose best is 57.9. Temperature 0.1 with l2 normalisation gives 64.4, against 57.2 or 57.0 without the normalisation.
- Stronger colour distortion (strength 1, with blur) lifts accuracy to 64.5% from 59.6% at strength 1/8, whereas a supervised model slips from 77.0 to 75.4; AutoAugment gives 61.1. At 100 epochs batch 256 reaches 57.5 and batch 4096 reaches 64.6, and longer training narrows the gap (800 epochs: 66.6 versus 68.9).
- Transfer by fine-tuning: the 4x model is significantly better than supervised on 5 of 12 datasets and worse on 2 (Pets, Flowers). A plain supervised ResNet-50 wins over SimCLR on every one of the 12 datasets under linear evaluation and on 10 of 12 when fine-tuned.

## MoCo

A query encoder is trained by SGD on an instance-discrimination task with the InfoNCE loss (a (K+1)-way softmax classifier that picks the positive key). Keys come from a queue of K past keys encoded by a key encoder that is a moving average of the query encoder, theta_k = m*theta_k + (1-m)*theta_q, so dictionary size is decoupled from mini-batch size. Shuffling BN shuffles the key mini-batch across GPUs before the key encoder, so query and positive key use batch statistics from different subsets; without it pretext accuracy rises above 99.9% and k-NN validation accuracy drops.

- Momentum m=0.999 yields 59.0% linear accuracy with K=4096; m=0.9 yields 55.2%, and m=0 fails to converge (ResNet-50, IN-1M).
- ResNet-50 with K=65536 reaches 60.6% linear, and R50w4x (375M parameters) 68.6%. A memory bank is 2.6% worse at the same K (58.0 against 60.6). MoCo v2 (smaller augmentation and projection head changes, reported as an extension) reaches 71.1%.
- Transfer: on VOC with Faster R-CNN R50-C4 (24k iterations, 5 trials), MoCo pretrained on Instagram-1B beats supervised ImageNet pretraining by 3.7 AP (ImageNet-pretrained MoCo +2.4 AP). On COCO Mask R-CNN R50-FPN, the 1x schedule gives MoCo IN-1M 38.5 against supervised 38.9, and the 2x schedule gives IG-1B 41.1 against 40.6. On VOC semantic segmentation MoCo is worse than supervised by at least 0.8 mIoU (73.6 against 74.4).

## CPC v2

A ResNet-161 encoder applied patch by patch to unlabeled ImageNet predicts patch features in four spatial directions with InfoNCE, using layer normalisation and heavy augmentation of each patch.

- Linear top-1 rises from 48.7% (CPC v1) to 71.5% (ResNet-161, frozen features). With 1% of labels a fine-tuned ResNet-33 on CPC v2 gets 78.3% top-5 against 44.1% for supervised pixels (top-1 52.7 against 23.1). With 100% labels the classifier reaches 83.4% top-1 against 80.2% supervised.
- With 1% of labels and frozen CPC v2 features, top-5 is 77.1, against 67.4 for AMDIM, 57.5 for rotation and 55.2 for BigBiGAN; fine-tuning improves this only slightly. A supervised stack of ResNet-161 and ResNet-33 equals ResNet-200, which leads the authors to dismiss model capacity as the cause.
- Ablation (custom validation set): layer norm recovers about 2% (batch norm hurts large CPC models), patch-based augmentation adds 4.5% altogether, and moving from ResNet-101 to ResNet-161 adds roughly 5% top-1. On VOC 2007 detection with Faster R-CNN the CPC v2 encoder scores 76.6 mAP against 74.7 supervised, while MoCo reports 74.9 in the same setting at the same time.

## PIRL

PIRL trains an image's representation to resemble that of a pretext-transformed copy instead of predicting the transformation. The loss is L(I, I^t) = lambda * NCE(m_I, g(v_I^t)) + (1 - lambda) * NCE(m_I, f(v_I)); negatives come from an NPID-style memory bank of 32,000 entries, and lambda=0 reduces to NPID. The pretext transformations are Jigsaw (nine shuffled patches) and Rotation.

- ResNet-50, 800 epochs on ImageNet-1k (batch 1,024, lambda=0.5, Jigsaw): linear top-1 beats the covariant Jigsaw version by over 15 points. NPID++ (lambda=0, but more negatives and longer training) lands at 59% top-1, so invariance itself contributes about 4.6 points. PIRL's table figure is 63.6.
- With Rotation, PIRL gains 11.3 top-1 over standard rotation prediction; combining Rotation and Jigsaw improves further. Jigsaw representations collapse at res5 while PIRL is best there. The L2 distance between f(v_I) and g(v_I^t) is small for PIRL and much larger in mean and variance for Jigsaw.
- Fine-tuned Faster R-CNN C4 (VOC07+12 train) beats supervised ImageNet pretraining on AP_all and AP75. Pretraining on uncurated YFCC-1M gives better Places205 than ImageNet pretraining. Lambda 0.5 is best, with sensitivity to the value (400 epochs, N=4,096).

## Limits

- SimCLR: ablations run only 100 epochs, and the authors concede peak performance is not reached; bars are single runs without ImageNet variance, and the permutation test ignores variability in training. It depends on very large batches (as many as 8192) spread over many TPU cores. A gap to supervised remains for a narrow ResNet-50 (69.3 against 76.3) and, under linear evaluation, on all 12 transfer datasets. The explanations given for the projection head and colour distortion are conjectures.
- MoCo: the Instagram-1B gain over ImageNet-1M is small; only the simple instance-discrimination pretext is explored; fine-tuning reuses supervised hyperparameters; seeds and warmup are not stated and IG-1B is not public. The linear protocol needs learning rate 30, implying feature magnitudes that differ from supervised features.
- CPC v2: the stack has over 500M parameters against about 60M for ResNet-200, and the label-propagation comparison uses different architectures and an assumption about unlabeled images. Ablations use a custom validation set; no seeds, error bars or compute are reported.
- PIRL: ResNet-50 on ImageNet scale only, single runs; PIRL AP50 on VOC07 is below supervised (73.4 against 74.5). Gains shrink against concurrent MoCo (55.2 AP_all, 60.6 top-1). PIRL (Jigsaw) is 62.2 in Table 5 and 63.6 in Table 2 with no explanation. Ablations use 400 epochs and N=4,096, and lambda, N and |T| are shown only as plots.

## See Also
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for
- [[BYOL Bootstrap Your Own Latent]] — alternative-to (drops negatives)
- [[SimCLRv2 Pretrain, Fine-Tune, Distill]] — extends
- [[DINO and iBOT Self-Distillation for Vision Transformers]] — alternative-to
- [[Instagram Hashtag Weakly Supervised Pretraining]] — related (the data MoCo scales to)
- [[Contrastive and Masked Vision-Language Pretraining]] — related
- [[ResNeXt Cardinality in Residual Blocks]] — related
