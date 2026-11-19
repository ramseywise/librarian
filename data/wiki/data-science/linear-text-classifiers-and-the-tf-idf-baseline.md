---
title: "Linear Text Classifiers and the TF-IDF Baseline"
tags: [data-science, pattern]
summary: "TF-IDF plus a regularised linear model inside a pipeline is the text-classification baseline; Naive Bayes, trees and averaged word vectors compared, with coefficient reading as a leakage check."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--02-text-classification.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch04-text-classification.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch06-learning-classify-text.md
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

## An untuned six-model comparison on 20 Newsgroups

Sarkar's chapter 4 trains six models (two classifiers, four feature sets): naive Bayes on bag of words and TF-IDF, and an SVM on bag of words, TF-IDF, averaged word2vec and TF-IDF-weighted word2vec. Setup: `fetch_20newsgroups` with headers, footers and quotes removed and empty documents dropped, a 33% test split with seed 42, and normalisation covering contractions, lemmas, special characters and stop words, default hyperparameters, one run, weighted-average scores. The SVM is `SGDClassifier(loss='hinge', n_iter=100)` and Naive Bayes is `MultinomialNB`.

| Model and features | Accuracy |
|---|---|
| SVM, TF-IDF | best of the six (figure not given) |
| Multinomial NB, TF-IDF | 0.72 (weighted F1 0.70) |
| Multinomial NB, bag-of-words counts | 0.67 |
| SVM, bag-of-words counts | 0.61 (weighted F1 0.62) |
| SVM, averaged word2vec (500-d, window 100, min_count 30, trained on the training split) | 0.55 |
| SVM, TF-IDF-weighted averaged word2vec | 0.53 |

The extraction puts the averaged word2vec SVM 22 points below the TF-IDF SVM. The SVM's confusion matrix shows mistakes between neighbouring topics, for example alt.atheism read as soc.religion.christian and talk.politics.misc read as talk.politics.guns. Unlike the genre task above, Naive Bayes did better on TF-IDF than on counts here, so the ordering depends on the data. Removing headers, footers and quotes is the authors' guard against a model overfitting to email addresses. The book asserts that random forests and gradient boosting often do poorly on text because they overfit, and tests neither.

A worked metric example takes 20 emails, half spam and half ham, with spam as the positive class and 11 predicted spam. TP=5, FP=6, FN=5 and TN=4 give accuracy 0.45, precision 0.45 and recall 0.5. scikit-learn prints F1 as 0.48 and a hand computation from the rounded precision and recall prints 0.47.

## Naive Bayes runs in the NLTK book

Bird, Klein and Loper's chapter 6 uses NLTK's naive Bayes classifier throughout. On the Names Corpus, with 500 names held out, the last letter alone gives 75.8% for gender. A kitchen-sink feature set (first and last letter, letter counts, letter presence) scores about a point lower. On a 1,000-name dev-test set, the last letter scores 76.5% and adding two-letter suffixes after error analysis raises it to 78.2%. On the movie review corpus, binary presence features for each of the 2,000 commonest words reach 81% on 100 held-out reviews, with "outstanding" the most informative feature at 11.1:1 positive to negative. The book gives no maximum entropy comparison; it is left as an exercise.

The authors advise a training, dev-test and test split, with the dev-test split changed each round of error analysis and the test set untouched until the end; smoothing, so unseen feature and label pairs do not zero a label; and avoiding strongly correlated features, which naive Bayes counts twice. They also advise that the rarest label occur some 50 or more times in the test set.

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

## Limits

- The 20 Newsgroups comparison is untuned (the book says its models work well at defaults), uses one split with no cross-validation or variance, and covers only Naive Bayes and a hinge-loss SVM.
- The text says the test set is 30 percent, but the code uses 0.33.
- Its word2vec is trained on the training split only; no pretrained or contextual vectors are tried, and no reason is given for dense features losing beyond the numbers.
- The code is Python 2 era.

- The NLTK book's accuracies are single runs on one shuffle or positional split with no seed; its movie review test set holds 100 documents, and sentence segmentation (97.4%) and dialogue acts (66%) have no majority-class baseline. Its code is Python 2 and it predates scikit-learn, regularised logistic regression and embeddings.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[Text Classification Metrics: Macro-F1, Log-Loss and Calibration]] — extends
- [[Sentence Embeddings as Features for Classical ML]] — alternative-to
- [[Regularisation as a Prior]] — related
- [[Pipelines Prevent Preprocessing Leakage]] — related
