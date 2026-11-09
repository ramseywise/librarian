---
title: PubMedQA
tags: [eval, benchmark]
summary: "A biomedical yes/no/maybe QA set built from PubMed question-titled abstracts, with 1k expert labels; the best 2019 BioBERT setup reaches 68.1% accuracy against 78.0% for one human in the reasoning-required setting (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-jin-2019-pubmedqa.md
---

# PubMedQA

Jin and colleagues (EMNLP-IJCNLP 2019) build a biomedical QA set in which the answer must be reasoned from quantitative research text. Articles with question titles and structured abstracts supply the data: the context is the abstract without its conclusion and the **long answer** is the conclusion.

## Splits and settings

- **PQA-L**: 1k instances labelled yes, no or maybe by two M.D. candidates. **PQA-U**: 61.2k unlabelled answerable instances. **PQA-A**: 211.3k artificially generated instances from statement titles converted to questions.
- **Reasoning-required** setting: question plus context. **Reasoning-free** setting: question plus long answer, where the label is usually explicit.
- The baseline trains BioBERT in phases (pre-train on PQA-A, then PQA-L) with a bag-of-words loss on the long answer as auxiliary supervision, L = L_QA + beta L_BoW.

## Results (self-reported)

Setup: PQA-L test set unless noted.

- Best model (multi-phase BioBERT with long-answer supervision, reasoning-required): 68.1% accuracy. One human (an M.D. candidate): 78.0% accuracy, 72.2% macro-F1, a lower bound as only one annotator was tested. Always answering yes: 55.2%.
- Reasoning-free: BioBERT 80.80 against 90.40 for a single human.
- BioBERT trained on PQA-L alone (450 training instances in each fold) lands near the majority-class level; pre-training on PQA-A lifts it from 56.98 to 66.90 without auxiliary supervision. The auxiliary loss improves most results.
- PQA-A is imbalanced: always-yes gets 92.76% accuracy there, BioBERT 96.50%.
- About half of the question-titled candidates were unanswerable by yes/no/maybe in the initial screen. Of 200 sampled PQA-L examples, 57.5% involve comparison between groups. The authors estimate the ground-truth error rate could be as low as 1%.

## Limits

- Human performance rests on one annotator. A shared mistake by both annotators would survive in the labels.
- PQA-A labels are heuristic (92.8% yes, no maybe); Phase II results cannot be set side by side across models, since each model relies on its own pseudo-labels.
- Yes means the paper's results indicate yes, not universal truth. Topics skew to clinical studies.
- Optimizer, learning rate, batch size, epochs, seeds and hardware are not stated; no confidence intervals on a 3-way task with a 500-instance test set. Baselines are BERT-era.

## See Also
- [[Math Word Problem Benchmarks]] — related
- [[MultiMedQA and Med-PaLM]] — related (includes this set among its multiple-choice sources)
- [[RAG Evaluation]] — prerequisite-for
