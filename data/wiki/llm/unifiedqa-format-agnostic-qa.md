---
title: UnifiedQA Format-Agnostic QA
tags: [llm, fine-tuning, pattern]
summary: UnifiedQA turns extractive, abstractive, multiple-choice and yes/no QA into plain text in and text out and trains one T5-11B (and BART-large) on a mixture of 8 seed datasets; the multi-format mixture beats single-format models on 12 unseen datasets (self-reported).
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-khashabi-2020-unifiedqa.md
---

# UnifiedQA Format-Agnostic QA

Khashabi and colleagues (Findings of EMNLP 2020) ask whether one text-to-text QA model trained across four answer formats can match format-specialised models and generalise to datasets it has not seen. Their hypothesis is that the reasoning needed for QA is largely common across formats, so out-of-format training data should help.

## Mechanism

- Every QA instance is rewritten as plain input text and output text with newline separators, with no format-specific prefixes (this departs from the task prefixes of [[T5 Text-to-Text Transfer Transformer]]).
- Eight seed datasets covering four formats (extractive, abstractive, multiple-choice, yes/no) are pooled; SQuAD 2, BoolQ, OBQA and NarQA are among those the paper names.
- T5-11B (and BART-large as a second base) is trained on the mixture, sampling evenly across datasets.
- Evaluation covers seen datasets, 12 unseen datasets, and fine-tuning on a target dataset.

## Results (self-reported)

- Averaged over 12 unseen datasets (T5-11B, zero-shot), the multi-format model beats every single-format variant.
- Zero-shot, it beats the fully supervised previous best on two yes/no sets it never saw, NP-BoolQ and BoolQ-CS (BoolQ-CS: 80.4 against 71.1).
- A T5-small pilot (BoolQ plus SQuAD2 training) adds an out-of-format set, and NP-BoolQ moves from 51.3 up to 59.4.
- Fine-tuned UnifiedQA beats fine-tuned T5 by the largest margin on ARC-challenge (without IR). The paper claims state of the art on 10 datasets in the abstract and introduction, but 11 in the Table 5 caption.
- Leave-one-out ablation (average over 9 seed evaluation sets): removing BoolQ costs the most (-8.4), and the top four contributors are BoolQ, SQuAD 2, OBQA and NarQA; dropping SQuAD 2 collapses SQuAD 2 performance.

## Limits

- The authors concede that what drives generalisation (size, domain) is not well understood. Only four formats are covered; direct-answer questions are left for future work; curriculum, distillation and teacher annealing are unexplored.
- Each setting was run once, without seeds or significance tests, and the hyperparameters sit in appendices absent from the extracted PDF.
- The "previous best" figures in Table 4 come from fully supervised systems, so they do not compare directly with zero-shot results.
- The state-of-the-art count is inconsistent (10 in abstract and introduction, 11 in the Table 5 caption).

## See Also
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — related (multitask training across formats)
- [[SQuAD 2.0 Unanswerable Questions]] — related (one of its seed datasets)
