---
title: "Frozen vs Fine-Tuned Sentence Encoders"
tags: [foundations, comparison]
summary: "A pre-trained encoder is not one result: a small frozen encoder lost to TF-IDF at every label count, a larger one won with few labels, and fine-tuning DistilBERT first clearly beat word counts only at 5,000 labels (0.905 vs 0.886); measure on your task and keep TF-IDF as the bar."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--06-neural-text-models.md
---

# Frozen vs Fine-Tuned Sentence Encoders

Instead of learning embeddings from a few thousand reviews, start from an encoder pre-trained on far more text. Two options: freeze it and fit a linear head on its vectors, or train through it.

## Frozen (linear head), test accuracy at 100 / 500 / 2,000 / 5,000 labels

| Representation | 100 | 500 | 2,000 | 5,000 |
|---|---|---|---|---|
| TF-IDF + logistic regression | 0.719 | 0.8 | 0.862 | 0.886 |
| MiniLM (384-d) | 0.669 | 0.754 | 0.786 | 0.806 |
| mpnet (768-d) | 0.769 | 0.841 | 0.871 | 0.882 |

The small encoder, which reads at most 256 word pieces, loses to TF-IDF at every size. The larger one, reading 384, wins clearly on few labels (0.769 vs 0.719 at 100) and its lead is gone by 5,000. A frozen encoder earns its place when labels are few. A small encoder that truncates long text is a likely reason one loses.

## Fine-tuned DistilBERT (small learning rate, two epochs)

0.825 at 500 labels, 0.883 at 2,000, 0.905 at 5,000. At 500 it trails frozen mpnet (0.841); at 2,000 it leads (0.883 vs 0.871); at 5,000 it is the first score in the comparison to clearly beat word counts, by about two points. One split and one seed: differences under a point are ties. Neural models trained from scratch never got close; see [[Neural Text Models vs TF-IDF]].

## Practical notes

- Pipelines: pin the model, since defaults change between library versions; some pipeline tasks were removed in transformers 5.
- Entity grouping needs the right aggregation strategy ("first" kept names whole where "simple" split a name into word pieces).
- A base generative model completes text rather than following instructions.
- Sentence vectors also power semantic search.

## See Also
- [[Neural Text Models vs TF-IDF]] — prerequisite-for
- [[Bag of Words, n-grams and TF-IDF]] — alternative-to
- [[Transfer and Multi-Task Learning Conditions]] — related
- [[Choosing an Encoder vs CNN vs LSTM]] — related
- [[Sentence Embeddings as Features for Classical ML]] — related
