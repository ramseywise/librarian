---
title: "Linear Text Classifiers and the TF-IDF Baseline"
tags: [foundations, pattern]
summary: "TF-IDF plus a regularised linear model inside a pipeline is the text-classification baseline; Naive Bayes, trees and averaged word vectors compared, with coefficient reading as a leakage check."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--02-text-classification.md
---

# Linear Text Classifiers and the TF-IDF Baseline

Text features are very many, very sparse, and individually mostly irrelevant. That profile suits a high-dimensional linear separator with regularisation (see [[Regularisation as a Prior]]), which is why TF-IDF unigrams and bigrams with logistic regression or a linear SVM, built from [[Bag of Words, n-grams and TF-IDF]], is the baseline to beat. Always put the vectoriser inside the pipeline so vocabulary and idf are refit on each training fold ([[Pipelines Prevent Preprocessing Leakage]]), and grid-search regularisation and n-gram range together, since more features usually want more regularisation.

## What the baseline looks like on a hard task

Setup: predict a film's first listed genre from its description, six most common genres, 2,877 training and 960 test documents, 5-fold CV scored on macro-F1. The grid chose unigrams and `C=100`: CV macro-F1 0.424, test accuracy 0.532, test macro-F1 0.423. Always guessing the majority class scores 0.315, and the first listed genre is partly arbitrary, so judge the number against the task, not against 1. Bigrams added sparsity rather than signal at this size: a measurement, not a law.

On an easier binary review benchmark, each step is worth little: counts + logistic regression 0.88, `min_df=5` 0.88, stop words slightly lower, TF-IDF 0.89, (1,3)-grams with tuned `C` 0.91.

## Model comparison on sparse text

| Model | Result | Why |
|---|---|---|
| Multinomial Naive Bayes | Strong for its cost; use counts | One pass; counts fit the multinomial assumption |
| Logistic regression | Among the best | Linear, regularised |
| Linear SVM | Often top on TF-IDF | Same, hinge loss |
| SGD classifier (hinge) | Close to linear SVM | Online; scales past memory |
| Random forest | Clearly worse | Each split sees one sparse feature |
| Gradient boosting | Worst and slowest | Same, plus sequential |

Measured macro-F1 (3-fold, same genre task, counts / TF-IDF): Naive Bayes 0.362 / 0.230, logistic regression 0.384 / 0.391, linear SVM 0.363 / 0.404, SGD hinge 0.392 / 0.397, random forest (100 trees) 0.265 / 0.247, gradient boosting (50 rounds) 0.334 / 0.321 taking 10.8 seconds against 0.3 to 1.6 for the linear models. Naive Bayes collapses on TF-IDF because its priors swamp the small fractional weights and it predicts mostly the big classes. On a 20-class newsgroup task the tuned linear SVM wins at mid-70s percent accuracy, and its errors fall between related groups, which is label ambiguity no model fixes. Trees and boosting on sparse text are the pattern also seen in the ensemble ladder of a text competition, where they were mediocre.

## Dense features rarely win without help

Averaged word2vec, GloVe or FastText vectors fed to a linear model land below tuned TF-IDF; an MLP on averaged GloVe beats the linear model on the same vectors but not tuned TF-IDF. Averaging discards order and dilutes informative words with common ones. Check on the genre task: word2vec trained on the 2,877 training documents reaches macro-F1 0.35 against 0.423. Dense vectors win when training data is small, when test vocabulary differs, or when vectors are contextual and fine-tuned, see [[Sentence Embeddings as Features for Classical ML]] and [[Word Embeddings and Similarity Measures]].

## Read the coefficients

A linear model's per-class token weights show what drives each class. Top Horror features include terrifying, terror, zombies, hell; Action includes cop, kill, criminals, target. A franchise villain's name appearing as a horror word shows the model leaning on a few films. A reviewer's signature, a source name or an id near the top means leakage (compare [[Tabular ML Leakage Taxonomy]]). With trigram features, phrases like "not worth" among the strongest features show n-grams capturing negation that unigrams miss.

## Practical options

| Situation | Option |
|---|---|
| Imbalance | `class_weight="balanced"`, PR curves |
| Many classes, little data | Hierarchical labels; few-shot with embeddings or an LLM |
| Very large data | Hashing trick: `HashingVectorizer` + `partial_fit`, no vocabulary held |
| Typos, authorship, short text | Character n-grams (`char_wb`, range 2 to 5) |
| When to go neural | Order matters, lots of labels, or a fine-tunable pretrained model |

The hashing trick on the genre task reached macro-F1 0.415 against 0.423, at the cost of one-way features that cannot be read back. Character n-grams reached 0.437. A learning curve (287, 719, 1,438, 2,877 documents gives macro-F1 0.244, 0.270, 0.349, 0.423) was still climbing at full size.

## Pitfalls

- Vectorising before the split.
- Reading accuracy with skewed classes; see [[Text Classification Metrics: Macro-F1, Log-Loss and Calibration]].
- Fitting the vectoriser on train plus test text: legitimate only where test text is known in advance, as in a competition.
- Reaching for tree ensembles by habit.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[Text Classification Metrics: Macro-F1, Log-Loss and Calibration]] — extends
- [[Sentence Embeddings as Features for Classical ML]] — alternative-to
- [[Regularisation as a Prior]] — related
- [[Pipelines Prevent Preprocessing Leakage]] — related
