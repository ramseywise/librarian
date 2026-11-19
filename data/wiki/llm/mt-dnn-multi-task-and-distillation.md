---
title: MT-DNN Multi-Task Learning and Ensemble Distillation
tags: [llm, fine-tuning, pattern]
summary: "MT-DNN trains a shared BERT encoder with task-specific heads on all nine GLUE tasks before per-task fine-tuning; a follow-up distils task-specific MT-DNN ensembles into one multi-task student using averaged soft targets."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-liu-2019-multi-task-deep-neural-networks.md
  - data/raw/papers/2026-11-08-liu-2019-improving-multi-task-deep-neural.md
---

# MT-DNN Multi-Task Learning and Ensemble Distillation

## MT-DNN

Liu et al. use BERT as a shared encoder (lexicon and Transformer layers) with task-specific top layers: classification, SAN-based pairwise classification, regression and pairwise ranking. The model is trained further on all nine GLUE tasks by merging the datasets, shuffling, and drawing mini-batches from the pool, then fine-tuned per task. The authors' hypothesis is that multi-task learning and language-model pretraining are complementary.

Claims (self-reported):
- Initialised from BERT-large, MT-DNN reaches 82.7 on the GLUE test set, 2.2 above BERT-large (leaderboard as of Feb 25, 2019).
- Gains are largest on low-resource tasks: RTE dev 83.4 against 71.1 for BERT-large (2.5k training examples). CoLA test goes from 58.9 to 62.5 when per-task fine-tuning follows multi-task training.
- Domain adaptation (BERT-base based, mean of 5 samplings): given only 0.1% of SNLI training data (549 examples), MT-DNN scores 82.1 dev accuracy against 52.5 for BERT. MT-DNN-large reaches 91.6 on SNLI test and 95.0 on SciTail test, 1.5 and 6.7 above the prior best.

## Ensemble distillation

The follow-up extends Hinton-style distillation to the multi-task setting. Teachers come from six MT-DNNs that differ in shared-layer dropout. The three best are each fine-tuned on MNLI, QQP, RTE and QNLI, giving a three-model ensemble per task; the mean of their class probabilities is the soft target. The student keeps the vanilla MT-DNN architecture, and for each task its loss is the mean of the cross-entropy on hard labels and on soft targets, followed by per-task fine-tuning.

Claims (self-reported): the BERT-large based distilled model reports a single-model GLUE test score of 83.7%, a new best at the time (April 1, 2019 leaderboard) over vanilla MT-DNN, ahead of ALICE at 83.3 (unpublished, single or ensemble unknown). Gains also appear on tasks without a teacher (CoLA, with 8.5k training examples), and on RTE dev the student exceeds its own teacher ensemble (86.7). The student retains nearly all of the ensemble's gain on dev.

## Limits

- MT-DNN: no ablation separates multi-task learning from the SAN head beyond a single-task variant; single GLUE runs with no seeds or significance tests; compute and hardware are not stated; WNLI is not improved; the adaptation experiments are base-size only; the leaderboard results (Feb 25, 2019) have dated.
- Distillation: evaluated only on GLUE, with teachers for only 4 of 9 tasks; no seeds or significance tests although the paper uses stronger wording; dev gains on the larger tasks are small (MNLI 87.1 to 87.3, QQP 91.9 to 91.9); the weight on hard against soft loss is not ablated in the reported numbers (the authors say no significant difference); student cost and teacher compute are not reported; the comparison with ALICE and Snorkel MeTaL is partly unclear; the leaderboard claim is dated April 1, 2019.

## See Also
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for (the shared encoder)
- [[Knowledge Distillation with Soft Targets]] — prerequisite-for (the distillation recipe it extends)
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — related
