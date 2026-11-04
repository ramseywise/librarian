---
title: "Transfer and Multi-Task Learning Conditions"
tags: [foundations, pattern]
summary: "Transfer learning needs a much larger source task and shared low-level features, and can lose to training from scratch (frozen backbone 39.48% vs scratch 11.82% error); multi-task learning with masked loss uses partially labelled rows and halved error versus keeping only complete rows."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--03-structuring-ml-projects.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Transfer and Multi-Task Learning Conditions

## Transfer learning

It applies when task A has far more data than task B, the inputs are of the same type, and A's low-level features plausibly help B. Measured feature transfer shows features go from general to specific by layer, and fine-tuning transferred features can help further.

Counter-example on 8x8 digits: pretrain on digits 0-4, learn 5-9 from 25 labelled rows (5 seeds): from scratch 11.82% error, frozen backbone 39.48%, fine-tuned 15.54%. Transfer lost at every label count from 10 to 100. The conditions were not met: task A had only about twice B's rows, scratch training already worked because digits are nearly linearly separable, and an MLP's first layer sees the whole image so it has no general local features such as edges to hand over. Always keep the from-scratch control.

## Multi-task learning

One network trained on several tasks, sharing a representation. For an input with several things at once use one sigmoid per label, not a softmax (labels are not exclusive). For partially labelled rows, mask the loss on unknown labels. On digits with half the labels hidden, 157 of 1,257 rows had all three labels. Per-label error with masking over all rows: 7.96, 5.56, 4.81; training on complete rows only: 13.33, 14.81, 14.63.

## End-to-end learning

One network from input to output lets the data speak but shuts out useful hand-designed components; it is the more promising route when the training set is large.

## See Also
- [[Error Analysis, Bias and Variance Gaps]] — related
- [[Contrastive Self-Supervised Pretraining]] — related (another way to use unlabelled or other-task data)
