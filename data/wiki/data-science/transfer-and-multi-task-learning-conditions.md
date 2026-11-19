---
title: "Transfer and Multi-Task Learning Conditions"
tags: [data-science, pattern]
summary: "Transfer learning needs a much larger source task and shared low-level features, and can lose to training from scratch (frozen backbone 39.48% vs scratch 11.82% error); multi-task learning with masked loss uses partially labelled rows and halved error versus keeping only complete rows."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-kornblith-2019-do-better-imagenet-models-transfer.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--03-structuring-ml-projects.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Transfer and Multi-Task Learning Conditions

## Transfer learning

It applies when task A has far more data than task B, the inputs are of the same type, and A's low-level features plausibly help B. Measured feature transfer shows features go from general to specific by layer, and fine-tuning transferred features can help further.

Counter-example on 8x8 digits: pretrain on digits 0-4, learn 5-9 from 25 labelled rows (5 seeds): from scratch 11.82% error, frozen backbone 39.48%, fine-tuned 15.54%. Transfer lost at every label count from 10 to 100. The conditions were not met: task A had only about twice B's rows, scratch training already worked because digits are nearly linearly separable, and an MLP's first layer sees the whole image so it has no general local features such as edges to hand over. Always keep the from-scratch control.

## Do better ImageNet models transfer better?

Kornblith, Shlens and Le retrained 16 CNNs under one shared recipe (BN scale on; label smoothing, dropout and auxiliary head off) and scored 12 classification datasets three ways: L2 logistic regression on frozen penultimate-layer features, fine-tuning the whole network, and random initialisation. Accuracy was compared on the logit scale (self-reported):

- ImageNet top-1 correlated with frozen-feature transfer (r = 0.99) and with fine-tuned transfer (r = 0.96, 20,000 steps). Training from random init gave a much weaker correlation overall: weak on the 7 datasets under 10,000 examples, strong on the larger ones.
- With 16 public checkpoints, which vary in regularisation, the frozen-feature correlation was weak and not significant. Inception-style regularisers moved top-1 by under 1% yet cut frozen-feature transfer by about the gap between the worst and best ImageNet models (four Inception variants: no BN scale, label smoothing, dropout, auxiliary head).
- Of 192 dataset-model pairs, fine-tuning won over logistic regression in 179 and over scratch in 189. On Stanford Cars and FGVC Aircraft, fine-tuned Inception v4 (299x299) barely beat scratch (92.7% and 88.8%), though better ImageNet architectures still scored higher. Pretraining sped convergence about 17-fold on average (26 epochs against 444 to reach 90% of maximum odds, Inception v4 public checkpoint, geometric mean over datasets).
- Retrained models beat public checkpoints on frozen-feature transfer for 162 of 192 pairs; best retrained Inception-ResNet v2 against best public ResNet v1 152, t(11)=5.6, p=0.0002. On FGVC Aircraft, 16 examples per class were enough for scratch to match fine-tuning.

### Limits

- No variance over initialisations or data order was measured, so the r values rest on 16 single trained models.
- Only CNNs on image classification.
- Fine-tuning settings were picked using large validation sets, which may not mirror small-data practice.
- Retrained NASNet-A Large reached 80.8% against 82.7% published because regularisers were disabled.
- The ranking of architectures depends on the training recipe.
- Few-shot and adaptable-feature methods were not tested.

## Multi-task learning

One network trained on several tasks, sharing a representation. For an input with several things at once use one sigmoid per label, not a softmax (labels are not exclusive). For partially labelled rows, mask the loss on unknown labels. On digits with half the labels hidden, 157 of 1,257 rows had all three labels. Per-label error with masking over all rows: 7.96, 5.56, 4.81; training on complete rows only: 13.33, 14.81, 14.63.

## End-to-end learning

One network from input to output lets the data speak but shuts out useful hand-designed components; it is the more promising route when the training set is large.

## See Also
- [[Big Transfer (BiT) Generalist Pretraining]] — instance-of
- [[SimCLRv2 Pretrain, Fine-Tune, Distill]] — instance-of
- [[Error Analysis, Bias and Variance Gaps]] — related
- [[Contrastive Self-Supervised Pretraining]] — related (another way to use unlabelled or other-task data)
