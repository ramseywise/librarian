---
title: TyDi QA
tags: [eval, reference]
summary: A multilingual question-answering benchmark of 204K examples in 11 typologically diverse languages, with questions written natively from a short Wikipedia snippet and no translation, built so that question and answer overlap little.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-clark-2020-tydi-qa.md
---

# TyDi QA

Clark and colleagues (2020) ask how to build a trustworthy multilingual information-seeking QA benchmark without translation. Their hypothesis is that native-language questions, written before the writer sees any answer, overlap less with their answers and so give a harder and more dependable benchmark than translated SQuAD-style data.

## Construction

An **information-seeking question** is one where the asker does not yet know the answer. Annotators see the opening 100 characters of a Wikipedia article and write a question; a search limited to that language's Wikipedia returns the top article, and annotators then mark a passage answer and a **minimal answer** (the shortest span that still answers), or NULL, or YES/NO. The baselines are a rule that picks the first passage and multilingual BERT trained jointly across languages. A public leaderboard uses a hidden test set.

## Results (self-reported)

- On minimal-answer span selection and on passage selection, mBERT is well below the human estimate (TyDi QA dev, macro-average over the 10 non-English languages, mean of 4 replicas). On passage selection it is far above the first-passage baseline of 30.2 F1. The extraction gives no mBERT figures.
- mBERT fine-tuned only on English SQuAD 1.1 scores much lower on TyDiQA-GoldP than mBERT fine-tuned on GoldP, even for English (dev, 8 languages, zero-shot from 100k SQuAD 1.1 examples, mean of 5 fine-tunings; human 90.9).
- Question-answer lexical overlap on English (window of 200 characters, with the 100 most frequent tokens ignored): TyDiQA-GoldP scores 0.38, whereas MLQA scores 0.91 and XQuAD 1.52.
- Linguists judged 200 dev pairs in Finnish and Russian: NULL labels 85%, passage answers 92%, minimal answers 93% accurate.
- Between 46% and 82% of questions, depending on language, cannot be answered by their article.

## Limits

- Scores are not comparable across languages, since each has its own questions, content and annotator quality.
- The human estimate is a pessimistic one-versus-two comparison; a 25-way super-annotation on Natural Questions raised estimates by about 15 F1.
- NULL errors are false positives (missed answers); train is only singly annotated.
- Only 11 languages; Finnish and Kiswahili dev and test answers were not separately verified.
- Only an mBERT baseline with no hyperparameters is reported, and the benchmark has since been overtaken by stronger models.

## See Also
- [[SQuAD]] — prerequisite-for
- [[Benchmark Prompt Format Sensitivity]] — related (benchmark design choices change scores)
