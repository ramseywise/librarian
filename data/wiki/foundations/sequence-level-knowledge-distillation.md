---
title: Sequence-Level Knowledge Distillation
tags: [foundations, pattern]
summary: "Seq-KD trains a small student on the teacher's beam-search outputs instead of its word distributions; Kim and Rush (2016) report students about 10x faster than the teacher with little BLEU loss on English-German translation."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-kim-2016-sequence-level-knowledge-distillation.md
---

# Sequence-Level Knowledge Distillation

Word-level knowledge distillation trains a student to match the teacher's next-token distribution. Kim and Rush (EMNLP 2016) argue that for translation the target is a whole sequence, and propose training the student on sequences the teacher generates, so the student can be decoded without beam search.

## Variants

- Seq-KD: run beam search with the teacher over the training source sentences and take the top-scoring output as the new target; the student is then trained with ordinary negative log-likelihood on it. The loss approximates the teacher's sequence distribution by its single beam-search mode.
- Seq-Inter: from the teacher's beam, pick the hypothesis with the highest smoothed sentence BLEU against the gold target, and train on that instead.
- Word-KD can be added as an extra loss; the student can also be magnitude-pruned and retrained.

Teacher and student are attentional LSTM sequence-to-sequence models. No Transformer was tested.

## Reported results (self-reported)

Setup unless stated: English-German, WMT 2014, newstest2014, tokenized BLEU, a 2x500 LSTM student (84m parameters) distilled from a 4x1000 LSTM teacher (221m).

- With greedy decoding Seq-KD scored 4.2 BLEU above a baseline of the same size; with beam 5 the gap was 1.4 BLEU. Word-KD alone gave +0.7 BLEU greedy.
- On a GeForce GTX Titan X, the greedy student ran roughly ten times faster than the beam-5 teacher.
- Pruning 80% of a Seq-KD plus Seq-Inter student (beam 5; teacher 19.5 BLEU) left 13x fewer parameters than the teacher at a 0.4 BLEU loss; pruning 90% gave 8m parameters (26x fewer) at a 1.0 BLEU loss.
- A teacher fine-tuned on Seq-Inter data decoded greedily at the level the original reached with beam 5 (19.5).
- Thai-English (IWSLT 2015, teacher 2x500 at 47m, student 2x100 at 8m, greedy): Seq-KD plus Seq-Inter plus Word-KD was best, +3.6 BLEU.
- Word embeddings were about 63% of the 2x500 student's parameters (50m of 84m).

## Side effects the paper reports

The Seq-KD student puts 16.9% of its probability mass on its greedy output against 0.9% for the baseline, so it is more peaked. Its perplexity was worse (22.7 against 8.2) even though BLEU was better, so lower perplexity did not mean higher BLEU. The teacher's single beam-1 output held only 1.3% of its distribution.

## Limits

- Two language pairs, LSTM models only, one run per cell, no seeds or significance tests.
- Optimizer, batch size, epochs, dropout and training hardware are not stated (deferred to the teacher's source paper).
- The CPU model for the CPU speed test is not stated, and the 4x1000 teacher could not be opened on the Android phone used for the phone test.
- The authors note that one beam mode holds only about 1-3% of the teacher's probability mass.

## See Also
- [[On-Policy Distillation]] — related (distillation on student-generated rather than teacher-generated sequences)
- [[LLM Inference Economics]] — prerequisite-for
- [[Straight-Through Estimator]] — related
- [[Model Compression with MUNGE Mimic Nets]] — related (ensemble compression into a small net)
