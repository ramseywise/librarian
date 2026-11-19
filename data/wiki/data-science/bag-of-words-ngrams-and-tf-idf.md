---
title: "Bag of Words, n-grams and TF-IDF"
tags: [data-science, concept]
summary: "Sparse count and TF-IDF document vectors: how vocabulary controls, n-grams and idf weighting shape features, and why the vectoriser must be fitted inside the training fold."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--01-text-representation.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch07-working-text-data.md
---

# Bag of Words, n-grams and TF-IDF

The classical route from text to numbers: tokenise (see [[Text Preprocessing and the Stop-Word Negation Trap]]), count tokens per document, optionally reweight, and keep the result as a sparse document-term matrix. Order is discarded, which sounds too crude, yet which words a document uses says much about its subject and the rest needs far more data to learn. With a few thousand labels this is close to the best available, and it is the input to the linear baselines in [[Linear Text Classifiers and the TF-IDF Baseline]].

## Sparsity

Each document uses a few hundred words out of a vocabulary of tens of thousands. In one review benchmark the vocabulary of 25,000 reviews has 74,849 words. Keep the matrix as a sparse structure: calling `.toarray()` on real data runs out of memory.

## Controlling the vocabulary

| Setting | Effect |
|---|---|
| `min_df=5` | Drops tokens in fewer than 5 documents (typos, rare names); on the review benchmark 74,849 to 27,271 features at the same accuracy |
| `max_df=0.9` | Drops corpus-specific stop words |
| `stop_words="english"` | Drops a 318-word list; slightly worse on the benchmark, more useful for small data |
| `max_features` | Keeps the most frequent, which keeps corpus-specific stop words and discards rare informative terms |
| default token pattern | Drops one-letter tokens |

Measured on a corpus of 4,803 film descriptions (median 55 words):

| Configuration | Features |
|---|---|
| default | 21,809 |
| `min_df=5` | 5,435 |
| `min_df=5, max_df=0.5` | 5,429 |
| stop words + `min_df=5` | 5,175 |
| (1,2)-grams | 168,646 |
| (1,3)-grams | 398,412 |
| (1,3)-grams, `min_df=5` | 13,657 |

`max_df=0.5` removed only six words because few words occur in half of such short texts: look at the data before copying a setting. The long tail is why `min_df` is cheap: the top 100 words are 44.2% of all tokens and 9,561 of the 21,809 words occur once.

## n-grams

Single words lose "not good" and proper names. Adding pairs and triples recovers local order at the price of many more features. On the review benchmark a (1,3) range with TF-IDF and logistic regression moved accuracy from 0.89 to 0.91. Always pair n-grams with `min_df`, since most long n-grams occur once and teach nothing. Collocation scoring is the principled way to keep only the informative ones, see [[Collocations and Pointwise Mutual Information]].

## TF-IDF

Raw counts over-weight words common everywhere. TF-IDF weights a term by its frequency in this document and its rarity across the corpus. The scikit-learn default (smooth idf, L2-normalised rows) is

tfidf(t, d) = tf(t, d) * (ln((1 + N) / (1 + df(t))) + 1)

Implementing it from scratch and checking it matches the library output is the quickest way to see there is no magic. `sublinear_tf=True` replaces tf by 1 + log(tf). The lowest-idf terms are the corpus's own stop words ("the", "to", "and" on the film corpus), found without a list; the highest are rare terms.

**TF-IDF is a fitted transform.** The vocabulary and idf come from data, so fitting on all data leaks the test set. Put the vectoriser in the pipeline, as in [[Pipelines Prevent Preprocessing Leakage]].

## Similarity from the vectors

Rows are unit length, so a dot product is cosine similarity, which ignores document length. Nearest neighbours on film descriptions find sequels ("Toy Story" to its sequels), but a crime drama lands on a family comedy through shared family vocabulary: TF-IDF knows which words match and nothing about meaning. That lexical gap is why dense vectors exist, see [[Word Embeddings and Similarity Measures]].

## Sequences for neural models

The other route maps tokens to integer ids, pads to a fixed length and lets an embedding layer learn vectors, so order survives. Decisions: vocabulary size (roughly 5k to 50k words), always set an out-of-vocabulary token (otherwise unseen words vanish silently), choose a sequence length covering about 90 to 95 percent of documents (on the film corpus the 95th percentile is 113 tokens; truncating at 20 would cut 97.1% of descriptions), and for RNNs pre-padding keeps real tokens near the final state. Word-level vocabularies cannot handle new words or misspellings, so transformers use subword tokenisation (BPE, WordPiece).

## Choosing a representation

| Representation | Order kept | Semantics | Use with |
|---|---|---|---|
| Counts / binary | No | No | Naive Bayes, linear models |
| n-gram TF-IDF | Locally | No | Linear models |
| Topic proportions (10 to 200 dims) | No | Coarse | Exploration, features |
| Averaged word vectors (100 to 300 dims) | No | Yes | Small data |
| Token-id sequences | Yes | Learned | CNN, RNN, transformer |
| Sentence embeddings (384 to 1024 dims) | Encoded | Yes | Retrieval, few-shot classification |

## Measurements on IMDb reviews (Müller and Guido)

Setup for all rows: the Maas movie-review set (25,000 training and 25,000 test reviews, balanced), logistic regression, `GridSearchCV` over C, 5-fold CV.

- Default counts give 88% mean CV accuracy; the tuned C=0.1 gives 89% CV and 0.88 test.
- `min_df=5` leaves CV accuracy at 0.89. Adding `stop_words="english"` trims just 305 further features (27,271 down to 26,966), and CV accuracy slips to 0.88 from 0.89.
- TF-IDF with `min_df=5, norm=None` in a pipeline gives 0.89; adding bigrams and trigrams with C searched up to 100 gives 0.91 (best range (1,3), C=100).
- spaCy lemmatization cuts the `min_df=5` vocabulary from 27,271 to 21,596 features. With only 1% of the data for training (five stratified shuffles), best CV accuracy rises from 0.721 to 0.731.

The authors advise stripping HTML such as `<br />` before vectorising, using linear models on high-dimensional sparse counts and tuning C by cross-validation, keeping unigrams and adding bigrams (n-grams to length 5 risk a feature explosion and overfitting), reading the largest coefficients to inspect a text model, and trying lemmatization or stemming for small datasets.

## Limits

- The textbook uses one dataset and one classifier, with CV scores printed to two decimals and no variance, so 0.88 against 0.89 cannot separate `min_df`, stop words or TF-IDF.
- Cross-validating a `CountVectorizer` outside a pipeline is valid only because its defaults collect no statistics; the author prefers a pipeline.
- The chapter's code targets old releases of scikit-learn (for example `get_feature_names`) and spaCy 1.x. Word2vec, recurrent networks and transformers are out of scope.

## See Also
- [[Text Preprocessing and the Stop-Word Negation Trap]] — prerequisite-for
- [[Linear Text Classifiers and the TF-IDF Baseline]] — extends
- [[Word Embeddings and Similarity Measures]] — extends
- [[Topic Models and Extractive Summarisation]] — extends
- [[Pipelines Prevent Preprocessing Leakage]] — related
- [[Neural Text Models vs TF-IDF]] — related
- [[Lexical Diversity: Types, Tokens and Conditional Frequency Counts]] — prerequisite-for
