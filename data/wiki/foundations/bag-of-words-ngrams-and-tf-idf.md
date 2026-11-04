---
title: "Bag of Words, n-grams and TF-IDF"
tags: [foundations, concept]
summary: "Sparse count and TF-IDF document vectors: how vocabulary controls, n-grams and idf weighting shape features, and why the vectoriser must be fitted inside the training fold."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--01-text-representation.md
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

## See Also
- [[Text Preprocessing and the Stop-Word Negation Trap]] — prerequisite-for
- [[Linear Text Classifiers and the TF-IDF Baseline]] — extends
- [[Word Embeddings and Similarity Measures]] — extends
- [[Topic Models and Extractive Summarisation]] — extends
- [[Pipelines Prevent Preprocessing Leakage]] — related
- [[Neural Text Models vs TF-IDF]] — related
