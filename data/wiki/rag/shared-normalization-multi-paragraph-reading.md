---
title: Shared-Normalization Multi-Paragraph Reading
tags: [rag, pattern]
summary: "Shared-norm trains a paragraph-level reader with a softmax shared across sampled paragraphs, including ones without the answer, so confidences stay comparable when the reader is run over many paragraphs."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-clark-2018-simple-effective-multi-paragraph-reading.md
---

# Shared-Normalization Multi-Paragraph Reading

The problem: a paragraph-level QA model applied to a long document or many documents gets distracted. The authors' hypothesis is that a model trained only on answer-containing paragraphs gives confidence scores that are poorly calibrated and not comparable across paragraphs. The fix has two parts. First, a BiDAF-style reader with self-attention is trained on distantly supervised answer spans using a summed (marginalised) start/end objective. Second, in **shared normalization**, several paragraphs per context (including ones with no answer) are sampled in each batch and span scores go through one softmax across all of them, forcing scores to be comparable. At test time the span with the highest pre-softmax score over all paragraphs wins (the **confidence method**).

## Results

All numbers are self-reported.

- TriviaQA web test, S-Norm model with paragraphs of 800 at test and 600 in training: 66.37 exact match / 71.32 F1, roughly 10 points above earlier published results. TriviaQA wiki test: 63.99 exact match versus 51.59 for the best prior. TriviaQA unfiltered dev (16 paragraphs): 61.55 / 67.61.
- Ablation on TriviaQA web dev with a single selected paragraph: refined model + TF-IDF + sum objective 61.10 exact match, versus BiDAF 50.21 and a baseline 41.08.
- Against simply truncating the document, a linear-classifier paragraph selector raises, on TriviaQA web, the odds that the chosen text holds the answer (83.1% to 85.1%).
- Document-level SQuAD with 15 paragraphs: shared-norm peaks at 72.37 F1 / 64.08 exact match; the naive base model degrades past two paragraphs.
- On the Chen et al. document set, 59.14 exact match versus 49.7 reported for DrQA.
- Curated TREC (694 test questions), model trained on TriviaQA unfiltered and not retrained on TREC: 53.31% accuracy versus 37.18 for YodaQA with Bing and 25.7 for DrQA+DS. Corpora differ, so this is not strictly comparable.
- The authors hand-labelled 500 SQuAD training questions: 67.4% stand alone, 22.6% depend on the document, 10% on the paragraph. Among 200 errors on TriviaQA web dev, 40.5% lacked enough evidence in the document and 17% were absent from the answer key.
- Per the paper's plots, the naive model loses performance as paragraphs are added, being overconfident in wrong extractions, while shared-norm does not drop (read from plots, not tabulated).

## Limits

- SQuAD questions were not designed to be answered without their paragraph; about 10% depend on it.
- The TREC comparison spans different corpora and training data, so the authors disclaim claims about individual components.
- Articles in the Chen et al. document set were edited after the questions were written.
- Method rankings are read off line plots; there are no seeds, variance or significance tests, and learning rate and hardware are unstated.
- No evidence aggregation across paragraphs. The extraction notes it is dated (LSTM/GRU reader with GloVe); the leaderboard comparison was made 5/01/2018.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[DrQA Machine Reading at Scale]] — prerequisite-for
- [[BiDAF Bi-Directional Attention Flow]] — prerequisite-for
- [[Fusion-in-Decoder]] — alternative-to (fuses passages in the decoder instead of comparing scores)
